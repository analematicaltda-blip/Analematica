"""Additive advertising tables and declared profiles; no API calls or authorization claims."""
import app.models
from app.models.advertising import MetaAdsApp, MetaAdsAuthorization, MetaAdsOAuthState, AdvertisingProfile, AdvertisingDraft, InstagramLoginConfig, InstagramAuthorization, InstagramOAuthState, MetaWebhookConfig, MetaWebhookEvent
from app.db.session import engine, SessionLocal

DECLARED_PROFILES = [
    ('facebook', 'https://www.facebook.com/profile.php?id=1414458975087720', '', '1414458975087720'),
    ('instagram', 'https://www.instagram.com/analematicaltda/', 'analematicaltda', ''),
    ('x', 'https://x.com/Analematicaltda', 'Analematicaltda', ''),
]

def install():
    for model in [MetaAdsApp, MetaAdsAuthorization, MetaAdsOAuthState, AdvertisingProfile, AdvertisingDraft, InstagramLoginConfig, InstagramAuthorization, InstagramOAuthState, MetaWebhookConfig, MetaWebhookEvent]:
        model.__table__.create(engine, checkfirst=True)
    with SessionLocal() as db:
        for network, url, handle, declared_id in DECLARED_PROFILES:
            if not db.query(AdvertisingProfile).filter_by(scope='platform', network=network).first():
                db.add(AdvertisingProfile(scope='platform', network=network, public_url=url, handle=handle, declared_id=declared_id))
        db.commit()
    print('Integración publicitaria preparada. Perfiles declarados; autorización y gasto no activados.')

if __name__ == '__main__':
    install()
