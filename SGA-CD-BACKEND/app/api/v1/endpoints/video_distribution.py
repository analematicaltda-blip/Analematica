from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.services.video_distribution_service import VideoDistributionService, get_distribution_service
from app.services.plan_capability_service import PlanCapabilityService

router = APIRouter()

class DistributionRequest(BaseModel):
    platforms: List[str]
    video_url: str
    title: str
    description: str

@router.post("/publish")
def publish_video(
    *,
    request_in: DistributionRequest,
    db: Session = Depends(deps.get_db),
    distribution_service: VideoDistributionService = Depends(get_distribution_service),
    current_user = Depends(deps.get_current_active_user),
):
    """
    Publish a video to one or more social media platforms.
    Enforces role authorization (admin_general or admin_empresa) and commercial plan capability protection
    (social_publishing) derived from the user's JWT tenant identity before invoking upload services.
    """
    # 1. Enforce Role Authorization
    deps.role_required(["admin_general", "admin_empresa"])(current_user=current_user)

    # 2. Enforce Commercial Plan Capability Protection
    deps.require_plan_capability("social_publishing")(db=db, current_user=current_user)

    # 3. Reserve monthly usage quota
    num_platforms = len(request_in.platforms) if request_in.platforms else 1
    PlanCapabilityService.check_and_consume_quota(
        db=db,
        inquilino_id=current_user.inquilino_id,
        capability_name="social_publishing",
        amount=num_platforms
    )

    results = []
    errors = []

    for platform in request_in.platforms:
        try:
            result = distribution_service.publish_video(
                platform=platform,
                video_url=request_in.video_url,
                title=request_in.title,
                description=request_in.description
            )
            results.append(result)
        except Exception as e:
            errors.append({"platform": platform, "error": str(e)})

    if errors:
        # Partial or total failure: release quota for failed platforms only
        num_failed = len(errors)
        PlanCapabilityService.release_quota(
            db=db,
            inquilino_id=current_user.inquilino_id,
            capability_name="social_publishing",
            amount=num_failed
        )

    if not results and errors:
        raise HTTPException(status_code=500, detail={"message": "All publications failed.", "errors": errors})

    return {"message": "Distribution process completed.", "successes": results, "failures": errors}
