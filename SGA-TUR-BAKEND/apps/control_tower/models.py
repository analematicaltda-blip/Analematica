# backend/apps/control_tower/models.py

from .domain.kpi import KPI
from .domain.alert import Alert
from .domain.threshold import Threshold

# Standardized to Technical English and UUID v4 (Schema v2.1)
KPI.__schema_version__ = "v2.1"
Alert.__schema_version__ = "v2.1"
Threshold.__schema_version__ = "v2.1"
