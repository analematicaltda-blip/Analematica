"""Explicit additive installation. Default is inspection; --apply creates only missing tables."""
import argparse
from sqlalchemy import inspect
from app.db.session import engine
from app.models.workspace import WorkspaceLead
from .crm_models import CRMContact,CRMEvent
from .analytics_models import AnalyticsRecord,AnalyticsEvent
from .army_models import ArmyRecord,ArmyEvent
from .ads_models import AdsRecord,AdsEvent
from .inbox_models import InboxRecord,InboxEvent
from .publishing_models import PublishingRecord,PublishingEvent
from .mobile_message_models import MobileMessageRecord,MobileMessageEvent
from .email_campaign_models import EmailCampaignRecord,EmailCampaignEvent
from .generation_models import GenerationJob,GenerationEvent,GenerationResult
from .library_models import LibraryItem,LibraryEvent,LibraryBlob
from .capture_models import LandingCapture,CaptureEvent
from .landing_models import CommercialLanding,LandingEvent
from .payment_models import CommercialPayment,PaymentEvent
from .sales_models import CommercialSale,SaleEvent,SaleSpaceClaim
from .quotation_models import CommercialQuotation,QuotationEvent,QuotationAsset
from .pricing_models import CommercialPrice,PriceEvent
from .opportunity_models import CommercialOpportunity,OpportunityEvent
from .identity_models import CommercialGrant,CommercialConsent,CommercialIdentityAlias,CommercialPolicyEvent

def install(engine,apply=False):
    tables=[AnalyticsRecord,AnalyticsEvent,ArmyRecord,ArmyEvent,AdsRecord,AdsEvent,InboxRecord,InboxEvent,PublishingRecord,PublishingEvent,MobileMessageRecord,MobileMessageEvent,EmailCampaignRecord,EmailCampaignEvent,GenerationJob,GenerationEvent,GenerationResult,LibraryItem,LibraryEvent,LibraryBlob,LandingCapture,CaptureEvent,CommercialLanding,LandingEvent,CommercialPayment,PaymentEvent,WorkspaceLead,CommercialGrant,CommercialConsent,CommercialIdentityAlias,CommercialPolicyEvent,CRMContact,CRMEvent,CommercialOpportunity,OpportunityEvent,CommercialPrice,PriceEvent,CommercialQuotation,QuotationEvent,QuotationAsset,CommercialSale,SaleEvent,SaleSpaceClaim]
    existing=set(inspect(engine).get_table_names())
    missing=[m.__table__.name for m in tables if m.__table__.name not in existing]
    if apply:
        with engine.begin() as connection:
            for model in tables:model.__table__.create(connection,checkfirst=True)
            from .sales_space_guards import install
            install(connection)
    return {'missing_tables':missing,'applied':apply,'existing_data_modified':False}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true')
    print(install(engine,parser.parse_args().apply))
