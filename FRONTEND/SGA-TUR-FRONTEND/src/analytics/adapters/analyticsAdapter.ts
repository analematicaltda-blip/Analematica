import { KPIValue, TrendDirection } from '../types';

export const analyticsAdapter = {
  /**
   * Transforms a backend aggregate into a UI-ready KPI Value with trend calculation.
   */
  toKPIValue: (current: number, previous?: number, target?: number, unit: string = '$'): KPIValue => {
    let trend;
    if (previous !== undefined && previous !== 0) {
      const percentage = ((current - previous) / previous) * 100;
      trend = {
        value: Math.abs(Math.round(percentage * 10) / 10),
        direction: (percentage > 0 ? 'up' : percentage < 0 ? 'down' : 'neutral') as TrendDirection,
        label: 'vs periodo anterior'
      };
    }

    return {
      current,
      previous,
      target,
      trend,
      unit
    };
  },

  /**
   * Maps backend series data to TimeSeries format.
   */
  toTimeSeries: (data: any[]): any[] => {
    return data.map(item => ({
      timestamp: item.date || item.period,
      value: parseFloat(item.total || item.value || 0),
      label: item.label
    }));
  }
};
