from django.urls import path
from .api import CapabilitiesView, ContractView, IntentValidationView
urlpatterns = [path("capabilities/", CapabilitiesView.as_view()), path("contract/", ContractView.as_view()), path("intents/validate/", IntentValidationView.as_view())]

from .crm_api import CRMView
urlpatterns += [
    path('crm/context/', CRMView.as_view(), {'section':'context'}),
    path('crm/contacts/', CRMView.as_view()),
    path('crm/commands/', CRMView.as_view(), {'section':'commands'}),
    path('crm/contacts/<str:contact_id>/', CRMView.as_view()),
    path('crm/contacts/<str:contact_id>/history/', CRMView.as_view(), {'section':'history'}),
]

from .crm_api import CRMCompaniesView,CRMSessionStatus,CRMSessionLogin,CRMSessionMfa,CRMSessionRecovery,CRMSessionLogout
urlpatterns += [path('crm/companies/',CRMCompaniesView.as_view()),
 path('crm/session/status/',CRMSessionStatus.as_view()),path('crm/session/login/',CRMSessionLogin.as_view()),
 path('crm/session/mfa/',CRMSessionMfa.as_view()),path('crm/session/recovery/',CRMSessionRecovery.as_view()),
 path('crm/session/logout/',CRMSessionLogout.as_view())]

urlpatterns += [path('crm/receipts/<str:contact_id>/', CRMView.as_view(), {'section':'receipt'})]

from .crm_api import OpportunitiesView
urlpatterns += [path('crm/opportunities/',OpportunitiesView.as_view()),
 path('crm/opportunities/<str:opportunity_id>/',OpportunitiesView.as_view()),
 path('crm/opportunities/<str:opportunity_id>/history/',OpportunitiesView.as_view(),{'section':'history'}),
 path('crm/opportunity-commands/',OpportunitiesView.as_view(),{'section':'commands'}),
 path('crm/opportunity-receipts/<str:opportunity_id>/',OpportunitiesView.as_view(),{'section':'receipt'})]

from .crm_api import PricesView
urlpatterns += [path('crm/prices/',PricesView.as_view()),
 path('crm/prices/<str:item_id>/',PricesView.as_view()),
 path('crm/prices/<str:item_id>/history/',PricesView.as_view(),{'section':'history'}),
 path('crm/price-commands/',PricesView.as_view(),{'section':'commands'}),
 path('crm/price-receipts/<str:item_id>/',PricesView.as_view(),{'section':'receipt'})]

from .crm_api import QuotationsView
urlpatterns += [path('crm/quotations/',QuotationsView.as_view()),
 path('crm/quotations/<str:quotation_id>/',QuotationsView.as_view()),
 path('crm/quotations/<str:quotation_id>/history/',QuotationsView.as_view(),{'section':'history'}),
 path('crm/quotation-commands/',QuotationsView.as_view(),{'section':'commands'}),
 path('crm/quotation-receipts/<str:quotation_id>/',QuotationsView.as_view(),{'section':'receipt'})]

from .crm_api import QuoteResourcesView,QuoteMediaView,PublicQuoteView
urlpatterns += [path('crm/quotation-resources/',QuoteResourcesView.as_view()),path('crm/quotation-media/<str:asset_id>/',QuoteMediaView.as_view()),
 path('quote-links/<str:quotation_id>/<str:link_id>/',PublicQuoteView.as_view()),path('quote-links/<str:quotation_id>/<str:link_id>/media/<str:asset_id>/',PublicQuoteView.as_view())]

from .crm_api import SalesView
urlpatterns += [path('crm/sales/',SalesView.as_view()),path('crm/sales/<str:sale_id>/',SalesView.as_view()),path('crm/sales/<str:sale_id>/history/',SalesView.as_view(),{'section':'history'}),path('crm/sale-receipts/<str:sale_id>/',SalesView.as_view(),{'section':'receipt'}),path('crm/sale-commands/',SalesView.as_view(),{'section':'commands'}),path('crm/sale-accounts/',SalesView.as_view(),{'section':'accounts'})]

from .source_api import SaleSourceView
urlpatterns += [path('sale-source/<str:action>/',SaleSourceView.as_view())]

from .crm_api import PaymentsView
urlpatterns += [path('crm/payments/',PaymentsView.as_view()),path('crm/payments/<str:payment_id>/',PaymentsView.as_view()),path('crm/payments/<str:payment_id>/history/',PaymentsView.as_view(),{'section':'history'}),path('crm/payment-receipts/<str:payment_id>/',PaymentsView.as_view(),{'section':'receipt'}),path('crm/payment-commands/',PaymentsView.as_view(),{'section':'commands'})]

from .crm_api import AfterSalesView
urlpatterns += [path('crm/after-sales/<str:operation>/',AfterSalesView.as_view())]

from .crm_api import LandingsView,PublicLandingView
urlpatterns += [path('crm/landings/',LandingsView.as_view()),path('crm/landing-commands/',LandingsView.as_view()),
 path('crm/landings/<str:item_id>/',LandingsView.as_view()),path('crm/landings/<str:item_id>/history/',LandingsView.as_view(),{'section':'history'}),
 path('crm/landings/<str:item_id>/preview/',LandingsView.as_view(),{'section':'preview'}),path('crm/landing-receipts/<str:item_id>/',LandingsView.as_view(),{'section':'receipt'}),
 path('landing-pages/<str:item_id>/',PublicLandingView.as_view())]

from .crm_api import PublicLandingView,CaptureMetricsView
# Replace only the owned public page view; retain the GC-010 routes and history.
urlpatterns=[p for p in urlpatterns if str(p.pattern)!='landing-pages/<str:item_id>/']
urlpatterns += [path('landing-pages/<str:item_id>/',PublicLandingView.as_view()),path('landing-pages/<str:item_id>/<str:operation>/',PublicLandingView.as_view()),path('crm/landings/<str:item_id>/captures/',CaptureMetricsView.as_view())]

from .crm_api import LibraryView,PublicLibraryView
urlpatterns += [path('crm/library/',LibraryView.as_view()),path('crm/library/<str:item_id>/',LibraryView.as_view()),path('crm/library/<str:item_id>/versions/<int:version>/<str:kind>/',LibraryView.as_view(),{'section':'bytes'}),path('crm/library-receipts/<str:item_id>/',LibraryView.as_view(),{'section':'receipt'}),path('crm/library-commands/',LibraryView.as_view()),path('crm/library-upload/',LibraryView.as_view(),{'section':'upload'}),path('media-library/<str:item_id>/<int:version>/',PublicLibraryView.as_view())]

from .crm_api import GenerationView
urlpatterns += [path('crm/generation-profiles/',GenerationView.as_view(),{'section':'profiles'}),path('crm/generation/',GenerationView.as_view()),path('crm/generation/<str:job_id>/',GenerationView.as_view()),path('crm/generation/<str:job_id>/result/',GenerationView.as_view(),{'section':'result'}),path('crm/generation/<str:job_id>/history/',GenerationView.as_view(),{'section':'history'}),path('crm/generation-receipts/<str:job_id>/',GenerationView.as_view(),{'section':'receipt'}),path('crm/generation-commands/',GenerationView.as_view())]

from .crm_api import EmailCampaignView,PublicEmailUnsubscribeView
urlpatterns += [path('crm/email-campaigns/',EmailCampaignView.as_view()),path('crm/email-campaigns/<str:campaign_id>/',EmailCampaignView.as_view()),path('crm/email-campaigns/<str:campaign_id>/preview/<str:contact_id>/',EmailCampaignView.as_view(),{'section':'preview'}),path('crm/email-campaign-receipts/<str:campaign_id>/',EmailCampaignView.as_view(),{'section':'receipt'}),path('crm/email-campaign-commands/',EmailCampaignView.as_view()),path('email-unsubscribe/<str:campaign_id>/<str:contact_id>/<str:proof>/',PublicEmailUnsubscribeView.as_view())]

from .crm_api import PublicEmailReceiptView
urlpatterns += [path('email-receipts/<str:campaign_id>/',PublicEmailReceiptView.as_view())]

from .crm_api import MobileMessageView,PublicMobileReportView
urlpatterns += [path('crm/mobile-messages/',MobileMessageView.as_view()),path('crm/mobile-messages/<str:job_id>/',MobileMessageView.as_view()),path('crm/mobile-message-receipts/<str:job_id>/',MobileMessageView.as_view(),{'section':'receipt'}),path('crm/mobile-message-commands/',MobileMessageView.as_view()),path('mobile-message-reports/<str:job_id>/',PublicMobileReportView.as_view())]

urlpatterns += [path('crm/mobile-messages/<str:job_id>/history/',MobileMessageView.as_view(),{'section':'history'})]

from .crm_api import PublishingView
urlpatterns += [path('crm/publications/',PublishingView.as_view()),path('crm/publications/<str:job_id>/',PublishingView.as_view()),path('crm/publications/<str:job_id>/history/',PublishingView.as_view(),{'section':'history'}),path('crm/publication-receipts/<str:job_id>/',PublishingView.as_view(),{'section':'receipt'}),path('crm/publication-commands/',PublishingView.as_view())]

from .crm_api import InboxView
urlpatterns += [path('crm/inbox/',InboxView.as_view()),path('crm/inbox/<str:job_id>/',InboxView.as_view()),path('crm/inbox/<str:job_id>/history/',InboxView.as_view(),{'section':'history'}),path('crm/inbox-receipts/<str:job_id>/',InboxView.as_view(),{'section':'receipt'}),path('crm/inbox-commands/',InboxView.as_view()),path('crm/inbox-ingress/',InboxView.as_view(),{'section':'ingress'})]

urlpatterns += [path('crm/inbox-native-ingress/',InboxView.as_view(),{'section':'native'}),path('crm/inbox-source-sync/',InboxView.as_view(),{'section':'source-sync'})]

from .crm_api import AdsView
urlpatterns += [path('crm/ads/',AdsView.as_view()),path('crm/ads/<str:job_id>/',AdsView.as_view()),path('crm/ads/<str:job_id>/history/',AdsView.as_view(),{'section':'history'}),path('crm/ads-receipts/<str:job_id>/',AdsView.as_view(),{'section':'receipt'}),path('crm/ads-commands/',AdsView.as_view())]

from .crm_api import ArmyView
urlpatterns += [path('crm/army/',ArmyView.as_view()),path('crm/army/<str:job_id>/',ArmyView.as_view()),path('crm/army/<str:job_id>/history/',ArmyView.as_view(),{'section':'history'}),path('crm/army/<str:job_id>/soup/',ArmyView.as_view(),{'section':'soup'}),path('crm/army-receipts/<str:job_id>/',ArmyView.as_view(),{'section':'receipt'}),path('crm/army-commands/',ArmyView.as_view())]

from .crm_api import AnalyticsView
urlpatterns += [path('crm/analytics/',AnalyticsView.as_view()),path('crm/analytics/<str:job_id>/',AnalyticsView.as_view()),path('crm/analytics/<str:job_id>/history/',AnalyticsView.as_view(),{'section':'history'}),path('crm/analytics-receipts/<str:job_id>/',AnalyticsView.as_view(),{'section':'receipt'}),path('crm/analytics-commands/',AnalyticsView.as_view())]

from .crm_api import OperationsView
urlpatterns += [path('crm/operations/',OperationsView.as_view()),path('crm/operations/<str:domain>/<uuid:record_id>/',OperationsView.as_view())]

from .access_api import AccessAdminView
urlpatterns += [path('crm/access/<str:section>/',AccessAdminView.as_view()),path('crm/access/receipts/<str:key>/',AccessAdminView.as_view(),{'section':'receipts'})]
