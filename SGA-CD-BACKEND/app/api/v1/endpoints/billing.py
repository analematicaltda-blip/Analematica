from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app import schemas, models
from app.api import deps
from app.services.billing_service import BillingService
from app.core.rate_limiter import rate_limit

router = APIRouter()

# -------------------------------
# Stripe
# -------------------------------
@router.post("/stripe/create-payment-intent", response_model=schemas.PaymentIntent, dependencies=[Depends(rate_limit("payment_intent", max_requests=10, window_seconds=60))])
async def create_stripe_intent(
    db: Session = Depends(deps.get_db),
    payment_in: schemas.PaymentIntentCreate = None,
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    """
    Create a Stripe Payment Intent.
    The frontend will use the returned client_secret to confirm the payment.
    """
    billing_service = BillingService(db)
    try:
        # Amount should be in cents
        amount_in_cents = int(payment_in.amount * 100)
        intent_details = billing_service.create_payment_intent(
            gateway_name="stripe",
            amount=amount_in_cents,
            currency=payment_in.currency,
            user_id=current_user.inquilino_id
        )
        return intent_details
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(deps.get_db),
):
    """
    Handle webhooks from Stripe. This endpoint does not require JWT authentication
    as it's called by an external service (Stripe). Verification is done via signature.
    """
    billing_service = BillingService(db)
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header.")

    try:
        event = billing_service.handle_webhook(
            gateway_name="stripe",
            payload=payload,
            signature=sig_header
        )
        # Handle specific event types
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            print(f"PaymentIntent {payment_intent.id} succeeded for user {payment_intent.metadata.user_id}")
            # Aquí se podría actualizar la base de datos (ej: marcar pago como 'succeeded')

        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------------
# Mercado Pago
# -------------------------------
@router.post("/mercadopago/create-preference", response_model=schemas.MercadoPagoPreference)
async def create_mp_preference(
    db: Session = Depends(deps.get_db),
    payment_in: schemas.PaymentIntentCreate = None,
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    service = BillingService(db)
    try:
        return service.create_payment_intent(
            gateway_name="mercadopago",
            amount=int(payment_in.amount * 100),
            currency=payment_in.currency,
            user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/mercadopago/create-pse-preference", response_model=schemas.MercadoPagoPreference)
async def create_mp_pse_preference(
    db: Session = Depends(deps.get_db),
    payment_in: schemas.PaymentIntentCreate = None,
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    service = BillingService(db)
    payment_methods = {
        "excluded_payment_types": [
            {"id": "credit_card"},
            {"id": "debit_card"},
            {"id": "ticket"},
        ]
    }
    try:
        return service.create_payment_intent(
            gateway_name="mercadopago",
            amount=int(payment_in.amount * 100),
            currency=payment_in.currency,
            user_id=current_user.id,
            payment_methods=payment_methods
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/mercadopago/webhook")
async def mp_webhook(request: Request, db: Session = Depends(deps.get_db)):
    service = BillingService(db)
    payload = await request.json()
    try:
        _ = service.handle_webhook(
            gateway_name="mercadopago",
            payload=payload,
            signature=""
        )
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------------
# Wompi
# -------------------------------
@router.post("/wompi/create-transaction", response_model=schemas.WompiTransaction)
async def create_wompi_transaction(
    db: Session = Depends(deps.get_db),
    payment_in: schemas.PaymentIntentCreate = None,
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    service = BillingService(db)
    try:
        return service.create_payment_intent(
            gateway_name="wompi",
            amount=int(payment_in.amount * 100),
            currency="COP",  # Wompi siempre maneja COP
            user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/wompi/webhook")
async def wompi_webhook(request: Request, db: Session = Depends(deps.get_db)):
    service = BillingService(db)
    payload = await request.json()
    try:
        _ = service.handle_webhook(
            gateway_name="wompi",
            payload=payload,
            signature=""
        )
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))