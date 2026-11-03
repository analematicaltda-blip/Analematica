"""
SkyReelsV2Service — Distributed AI Video Generation Adapter for SGA-CD.
Supports async job management, remote worker delegation (Server 3 Video AI),
file existence/size validation, tenant isolation, cancellation handling,
and integrated GPU Lifecycle & 20-Hour Plan Full Quota Control.
"""
import logging
import uuid
import time
import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

from app.services.gpu_lifecycle_service import gpu_lifecycle_service

logger = logging.getLogger(__name__)

class SkyReelsV2Service:
    def __init__(self, endpoint_url: str = "http://localhost:8090", storage_dir: str = "SGA-CD-WEB.git/assets/generated"):
        self.endpoint_url = endpoint_url.rstrip('/')
        self.storage_dir = storage_dir
        self._jobs: Dict[str, Dict[str, Any]] = {}
        os.makedirs(self.storage_dir, exist_ok=True)

    def check_prerequisites(self) -> Dict[str, Any]:
        """
        Validates hardware and environment prerequisites for SkyReels-V2 (CUDA, PyTorch, VRAM).
        """
        has_cuda = False
        vram_gb = 0
        try:
            import torch
            has_cuda = torch.cuda.is_available()
            if has_cuda:
                vram_gb = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
        except ImportError:
            logger.info("PyTorch not installed in global environment.")

        # Check remote worker availability
        remote_worker_online = False
        try:
            req = urllib.request.Request(f"{self.endpoint_url}/health", headers={"User-Agent": "SGA-CD-SkyReels/2.0"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    remote_worker_online = True
        except Exception:
            pass

        return {
            "adapter": "SkyReels-V2",
            "cuda_available": has_cuda,
            "vram_gb": vram_gb,
            "min_required_vram_gb": 12,
            "ready_for_local_inference": has_cuda and vram_gb >= 12,
            "remote_worker_endpoint": self.endpoint_url,
            "remote_worker_online": remote_worker_online
        }

    def submit_video_job(
        self,
        prompt: str,
        format_type: str = "reel_9_16",
        inquilino_id: Optional[int] = None,
        duration_seconds: int = 5,
        fps: int = 30,
        plan_type: str = "full",
        api_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submits a video job with 20-hour quota verification and On-Demand GPU activation.
        """
        if not prompt or not prompt.strip():
            return {"status": "error", "error": "Prompt no puede estar vacío."}

        # 1. Quota Check for Tenant
        tenant_id = inquilino_id or 1
        quota_check = gpu_lifecycle_service.check_tenant_quota(tenant_id, plan_type)
        if not quota_check["authorized"]:
            return {
                "status": "quota_exceeded",
                "reason": quota_check["reason"],
                "error": quota_check["message"]
            }

        # 2. Reserve Quota
        reserved = gpu_lifecycle_service.reserve_quota(tenant_id, estimated_seconds=300.0)
        if not reserved:
            return {"status": "error", "error": "No se pudo reservar la cuota GPU para este trabajo."}

        # 3. Request GPU On-Demand Activation
        activation = gpu_lifecycle_service.request_gpu_activation(f"tenant_{tenant_id}")

        job_id = f"skyreels_{uuid.uuid4().hex[:12]}"
        created_at = time.time()
        output_filename = f"video_{job_id}.mp4"
        local_output_path = os.path.join(self.storage_dir, output_filename)

        job_info = {
            "job_id": job_id,
            "status": "queued",
            "prompt": prompt.strip(),
            "format": format_type,
            "inquilino_id": tenant_id,
            "duration_seconds": duration_seconds,
            "fps": fps,
            "created_at": created_at,
            "progress_pct": 0,
            "local_file_path": local_output_path,
            "output_url": f"/assets/generated/{output_filename}",
            "file_size_bytes": 0,
            "error": None
        }

        # Register Active Job in GPU Manager
        gpu_lifecycle_service.register_active_job(job_id)

        # Attempt delegation if remote worker is active
        prereqs = self.check_prerequisites()
        if prereqs["remote_worker_online"]:
            try:
                payload = json.dumps({
                    "job_id": job_id,
                    "prompt": prompt,
                    "format": format_type,
                    "duration_seconds": duration_seconds,
                    "fps": fps,
                    "inquilino_id": tenant_id
                }).encode('utf-8')
                headers = {"Content-Type": "application/json", "User-Agent": "SGA-CD-SkyReels/2.0"}
                if api_token:
                    headers["Authorization"] = f"Bearer {api_token}"

                req = urllib.request.Request(f"{self.endpoint_url}/v1/generate", data=payload, headers=headers)
                with urllib.request.urlopen(req, timeout=5) as resp:
                    if resp.status in (200, 202):
                        job_info["status"] = "processing"
                        logger.info(f"Job {job_id} delegated successfully to remote Server 3 worker")
            except Exception as e:
                logger.warning(f"Could not delegate job {job_id} to remote worker: {e}")

        self._jobs[job_id] = job_info
        logger.info(f"SkyReels-V2 job {job_id} registered for tenant {tenant_id}")

        return {
            "status": job_info["status"],
            "job_id": job_id,
            "estimated_completion_seconds": 15,
            "format": format_type,
            "output_url": job_info["output_url"],
            "gpu_activation_status": activation["status"]
        }

    def get_job_status(self, job_id: str, requester_inquilino_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Retrieves job status, validating tenant isolation and committed GPU consumption.
        """
        if job_id not in self._jobs:
            return {"status": "not_found", "job_id": job_id, "error": "Job ID no reconocido."}

        job = self._jobs[job_id]

        # Multi-tenant isolation check
        if requester_inquilino_id is not None and job["inquilino_id"] is not None:
            if job["inquilino_id"] != requester_inquilino_id:
                return {
                    "status": "forbidden",
                    "job_id": job_id,
                    "error": "Acceso denegado: El trabajo pertenece a otra organización."
                }

        # Check physical output file if completed or processing
        filePath = job.get("local_file_path")
        if filePath and os.path.exists(filePath):
            size = os.path.getsize(filePath)
            if size > 0:
                if job["status"] != "completed":
                    job["status"] = "completed"
                    job["progress_pct"] = 100
                    job["file_size_bytes"] = size

                    # Unregister active job and commit quota consumption (e.g. actual duration 15s)
                    gpu_lifecycle_service.unregister_active_job(job_id)
                    gpu_lifecycle_service.commit_quota_consumption(job["inquilino_id"], actual_seconds=15.0, reserved_seconds=300.0)

                return job

        # If no GPU and no remote worker, fail gracefully unless simulated test file exists
        prereqs = self.check_prerequisites()
        if not prereqs["ready_for_local_inference"] and not prereqs["remote_worker_online"]:
            if job["status"] not in ("completed", "failed", "cancelled"):
                job["status"] = "failed"
                job["error"] = "Servidor de IA Audiovisual (Servidor 3 GPU / SkyReels-V2) no disponible."

                # Unregister job and release reserved quota
                gpu_lifecycle_service.unregister_active_job(job_id)
                gpu_lifecycle_service.release_reserved_quota(job["inquilino_id"], reserved_seconds=300.0)

        return job

    def cancel_job(self, job_id: str, requester_inquilino_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Cancels an active or queued job and releases reserved quota.
        """
        if job_id not in self._jobs:
            return {"status": "not_found", "job_id": job_id, "error": "Job ID no encontrado."}

        job = self._jobs[job_id]
        if requester_inquilino_id is not None and job["inquilino_id"] != requester_inquilino_id:
            return {"status": "forbidden", "error": "Acceso denegado."}

        if job["status"] in ("completed", "failed", "cancelled"):
            return {"status": job["status"], "message": f"El trabajo ya está {job['status']}."}

        job["status"] = "cancelled"
        job["error"] = "Trabajo cancelado por el usuario."

        # Unregister active job and release quota
        gpu_lifecycle_service.unregister_active_job(job_id)
        gpu_lifecycle_service.release_reserved_quota(job["inquilino_id"], reserved_seconds=300.0)

        return {"status": "cancelled", "job_id": job_id, "message": "Trabajo cancelado exitosamente."}

skyreels_service = SkyReelsV2Service()
