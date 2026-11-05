export enum KPICategory {
  COMMERCIAL = 'COMMERCIAL',
  FINANCIAL = 'FINANCIAL',
  OPERATIONAL = 'OPERATIONAL',
  MARKETING = 'MARKETING',
  SOVEREIGN = 'SOVEREIGN'
}

export type TrendDirection = 'up' | 'down' | 'neutral';

export interface KPITrend {
  value: number;
  direction: TrendDirection;
  label: string; // e.g., "vs last month"
}

export interface KPIValue {
  current: number;
  previous?: number;
  target?: number;
  trend?: KPITrend;
  unit: string; // e.g., "$", "%", "days"
}

export interface KPIBase {
  id: string;
  name: string;
  category: KPICategory;
  value: KPIValue;
  lastUpdated: string;
}

export interface TimeSeriesData {
  timestamp: string;
  value: number;
  label?: string;
}

export interface CohortData {
  period: string; // e.g., "2024-Q1"
  size: number;
  retention: number[]; // Array of percentages for each month/period
}

export interface AnalyticalDecision {
  id: string;
  kpiId: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  context: string;
  suggestion: string;
  impact: string;
}
