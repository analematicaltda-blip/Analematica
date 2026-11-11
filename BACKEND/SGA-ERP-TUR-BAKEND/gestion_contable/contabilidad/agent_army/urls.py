from django.urls import path
from .api import CatalogView,MissionView,StateView,EngineView,IntakeView,OptimizationView
urlpatterns=[path('',CatalogView.as_view(),name='accounting-army-catalog'),
 path('intake/',IntakeView.as_view(),name='accounting-army-intake'),
 path('missions/<uuid:request_id>/optimization/',OptimizationView.as_view(),name='accounting-army-optimization'),
 path('missions/',MissionView.as_view(),name='accounting-army-run'),
 path('missions/<uuid:request_id>/',StateView.as_view(),name='accounting-army-state'),
 path('missions/<uuid:request_id>/engines/<str:engine>/',EngineView.as_view(),name='accounting-army-engine')]
