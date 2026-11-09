"""Legacy entry points fail before mutating invoices, numbering, keys or logs.

Previously these methods returned synthetic success and persisted plaintext XML.
They must not resume until a customer-custodied signer, qualified UBL profile and
verified habilitation/receipt adapter replace the fail-closed boundary.
"""
from apps.core_erp.accounting.dian_readiness import block_unverified_submission

class FacturacionElectronicaService:
    procesar_envio_dian=staticmethod(block_unverified_submission)
    generate_xml_dian=staticmethod(block_unverified_submission)
    calculate_cufe=staticmethod(block_unverified_submission)
    sign_invoice=staticmethod(block_unverified_submission)
    send_to_dian=staticmethod(block_unverified_submission)

class DianService(FacturacionElectronicaService):
    enviar_factura=staticmethod(block_unverified_submission)
