import { marketingKPIDefs } from '../definitions/comercial';
import { analyticsAdapter } from './analyticsAdapter';

export const marketingAdapter = {
  mapMarketingMetrics: (backendData: any) => {
    return {
      roi: analyticsAdapter.toKPIValue(
        backendData.roi_current,
        backendData.roi_previous,
        5.0, // target ROI
        'x'
      ),
      cac: analyticsAdapter.toKPIValue(
        backendData.cac_current,
        backendData.cac_previous,
        undefined,
        '$'
      ),
      ltv: analyticsAdapter.toKPIValue(
        backendData.ltv_current,
        backendData.ltv_previous,
        undefined,
        '$'
      ),
      ltvCacRatio: (backendData.ltv_current / (backendData.cac_current || 1)).toFixed(2)
    };
  }
};
