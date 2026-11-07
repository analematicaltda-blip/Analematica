from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List
from app.services.payment_gateway_adapter import payment_gateway

router = APIRouter()

PLANES_CATALOGO = [
    {
        "id": "plan_estudiante",
        "nombre": "Plan Estudiante Atleta/Artista",
        "precio": 50000,
        "moneda": "COP",
        "periodo": "Mensual",
        "beneficios": ["Acceso a entrenamientos y talleres", "Seguimiento de rendimiento", "Perfil deportivo verificado"]
    },
    {
        "id": "plan_docente",
        "nombre": "Plan Docente / Entrenador",
        "precio": 120000,
        "moneda": "COP",
        "periodo": "Mensual",
        "beneficios": ["Gestion de hasta 50 alumnos", "Planificador de clases IA", "Reportes biometricos"]
    },
    {
        "id": "plan_institucional",
        "nombre": "Plan Institucional / Club",
        "precio": 450000,
        "moneda": "COP",
        "periodo": "Mensual",
        "beneficios": ["Multi-sede ilimitado", "Ejercito de Agentes IA completo", "Pasarela de pagos personalizada"]
    }
]

class CheckoutRequest(BaseModel):
    plan_id: str
    nombre_cliente: str
    email_cliente: str
    telefono_cliente: str

@router.get("/plans")
def obtener_planes():
    return {"status": "success", "data": PLANES_CATALOGO}

@router.post("/checkout")
def crear_checkout_pago(pedido: CheckoutRequest):
    plan = next((p for p in PLANES_CATALOGO if p["id"] == pedido.plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    referencia = f"SGA-{pedido.plan_id.upper()}-{pedido.email_cliente[:5]}-101"
    cliente_info = {
        "nombre": pedido.nombre_cliente,
        "email": pedido.email_cliente,
        "telefono": pedido.telefono_cliente
    }

    resultado = payment_gateway.generar_link_pago(
        monto=plan["precio"],
        moneda=plan["moneda"],
        referencia=referencia,
        cliente_info=cliente_info,
        concepto=f"Suscripcion {plan['nombre']}"
    )
    return {"status": "success", "checkout": resultado}

@router.get("/config")
def obtener_configuracion_pasarela():
    return {
        "pasarela_activa": "CustomCompanyPaymentGateway (Wompi/PSE/Stripe Plug-and-Play)",
        "estado": "OPERATIVA",
        "monedas_soportadas": ["COP", "USD"]
    }