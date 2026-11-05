from rest_framework.routers import DefaultRouter
from .views import AssetCategoryViewSet, FixedAssetViewSet, DepreciationCalculationViewSet

router = DefaultRouter()
router.register(r'categories', AssetCategoryViewSet, basename='asset-category')
router.register(r'assets', FixedAssetViewSet, basename='fixed-asset')
router.register(r'depreciations', DepreciationCalculationViewSet, basename='depreciation')

urlpatterns = router.urls
