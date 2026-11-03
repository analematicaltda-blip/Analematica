import os
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="SGA-CD Media AI Worker", version="1.0.0")

class ReelRenderRequest(BaseModel):
    titulo: str
    duracion: int = 4
    color_fondo: str = "0x0D1424"

@app.get("/health")
def health():
    return {"status": "online", "engine": "FFmpeg Native"}

@app.post("/render/reel")
def render_reel(req: ReelRenderRequest):
    output_dir = "/app/assets/generated"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"reel_{abs(hash(req.titulo)) % 100000}.mp4"
    output_path = os.path.join(output_dir, filename)

    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"color=c={req.color_fondo}:s=1080x1920:d={req.duracion}",
        "-vf", f"drawtext=text='{req.titulo[:40]}':fontcolor=white:fontsize=44:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return {
            "status": "success",
            "filename": filename,
            "url": f"assets/generated/{filename}",
            "dimensions": "1080x1920"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallo en renderizado FFmpeg: {e}")