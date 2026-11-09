"""Compatibility boundary. Never manufactures signatures, CUFE or DIAN approval."""
from apps.core_erp.accounting.dian_readiness import block_unverified_submission

class DIANIntegrationService:
    calculate_cufe=staticmethod(block_unverified_submission)
    generate_ubl_xml=staticmethod(block_unverified_submission)
    sign_and_send=staticmethod(block_unverified_submission)
