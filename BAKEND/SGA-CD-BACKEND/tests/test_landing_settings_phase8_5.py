import pytest
from app.api.v1.endpoints.admin_general import LandingSettings, validate_url_safe

def test_landing_settings_url_validation():
    # Valid relative assets URL
    assert validate_url_safe("assets/video/sga_cd_institutional_5min.mp4") is True
    assert validate_url_safe("favicon.svg") is True
    assert validate_url_safe("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab") is True

    # Malicious URLs
    assert validate_url_safe("javascript:alert('xss')") is False
    assert validate_url_safe("data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==") is False

def test_landing_settings_pydantic_model_valid():
    settings = LandingSettings(
        hero_title="Título Test",
        hero_subtitle="Subtítulo Test",
        contact_email="test@sgacd.gov.co",
        social_links="https://wa.me/573000000000",
        footer_copy="© 2026 Test",
        hero_video_url="assets/video/sga_cd_institutional_5min.mp4",
        logo_url="favicon.svg",
        carousel_urls="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab",
        plan_tier1_price="199",
        plan_tier2_price="29",
        plan_grace_days="5",
        seo_title="SEO Test",
        seo_description="Desc Test"
    )
    assert settings.hero_video_url == "assets/video/sga_cd_institutional_5min.mp4"

def test_landing_settings_pydantic_model_invalid_url():
    with pytest.raises(ValueError):
        LandingSettings(
            hero_title="Título Test",
            hero_subtitle="Subtítulo Test",
            contact_email="test@sgacd.gov.co",
            social_links="https://wa.me/573000000000",
            footer_copy="© 2026 Test",
            hero_video_url="javascript:alert(1)",
            logo_url="favicon.svg",
            carousel_urls="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab",
            plan_tier1_price="199",
            plan_tier2_price="29",
            plan_grace_days="5",
            seo_title="SEO Test",
            seo_description="Desc Test"
        )
