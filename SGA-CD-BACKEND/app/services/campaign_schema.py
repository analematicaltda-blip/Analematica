"""Install only additive campaign tables; retain existing and offline databases."""
import app.models
from app.models import workspace as workspace_models  # register FK metadata in this fresh process
from app.models.campaigns import CampaignContact,Campaign,CampaignTarget,CampaignVariant,CampaignScheduler,CampaignSetting
from app.db.session import engine

def install():
    for model in [CampaignContact,Campaign,CampaignTarget,CampaignVariant,CampaignScheduler,CampaignSetting]:model.__table__.create(engine,checkfirst=True)
    print('Tablas de audiencia, campañas y calendario preparadas sin eliminar datos.')
if __name__=='__main__':install()
