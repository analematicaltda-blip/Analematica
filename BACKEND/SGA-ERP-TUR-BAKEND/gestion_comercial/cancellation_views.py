from rest_framework.exceptions import ValidationError
from .quote_views import PrivateDraftView
from rest_framework.response import Response
from apps.core_erp.accounting.query_parser import AccountingQueryJSONParser
from apps.core_erp.accounting.exceptions import AccountingError
from . import cancellation_policies as service

OPERATIONS={
 'review_wallet_refund_lifecycle':{'reservation_id','request_id','action','evidence_digest','expected_revision','confirmed'},
 'confirm_wallet_refund_lifecycle':{'reservation_id','review_id','confirmed'},
 'wallet_refund_lifecycle_state':{'reservation_id'},
 'wallet_refund_sources':{'reservation_id','after'},
 'prepare_wallet_refund':{'reservation_id','source_wallet_id','destination_wallet_id','liability_line_id','evidence_digest','confirmed'},
 'review_wallet_refund':{'reservation_id','device_proof','confirmed'},
 'execute_wallet_refund':{'reservation_id','confirmation','device_proof','confirmed'},
 'wallet_refund_state':{'reservation_id'},
 'review_refund':{'reservation_id','request_id','original_payment_reference','evidence_digest','confirmed'},
 'authorize_refund':{'reservation_id','review_id','confirmed'},
 'refund_state':{'reservation_id'},
 'sources':{'policy_after','reservation_after'},
 'review_policy':{'request_id','policy_id','expected_revision','values','confirmed'},
 'publish_policy':{'review_id','confirmed'},
 'policy_state':{'policy_id'},
 'bind_policy':{'reservation_id','policy_id','policy_revision','accepted_at','consent_kind','consent_digest','confirmed'},
 'review_case':{'reservation_id','request_id','requested_refund','reason_code','evidence_digest','expected_revision','confirmed'},
 'confirm_case':{'reservation_id','review_id','confirmed'},
 'case_state':{'reservation_id'},
}
class CancellationPolicyCommand(PrivateDraftView):
    parser_classes=[AccountingQueryJSONParser]
    def post(self,request,operation):
        if operation not in OPERATIONS or not isinstance(request.data,dict) or set(request.data) not in (OPERATIONS[operation],OPERATIONS[operation]|({'cancellation_at'} if operation=='review_case' else set())) or set(request.query_params)!={'provider_id'} or len(request.query_params.getlist('provider_id'))!=1:raise ValidationError('Contrato de política comercial inválido; empresa única requerida.')
        try:result=getattr(service,operation)(actor=request.user,provider_id=request.query_params['provider_id'],**request.data)
        except (AccountingError,ValueError,TypeError,KeyError):raise ValidationError('Revisa porcentaje, contrato, versión, consentimiento, excepciones y autorizaciones. No se presume validez legal ni pago.') from None
        return Response(result)
