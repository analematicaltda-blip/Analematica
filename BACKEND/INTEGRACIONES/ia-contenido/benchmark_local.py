"""Opt-in local model comparison. Records metrics, never prompts or output text."""
import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'BACKEND/SGA-CD-BACKEND'))
from fastapi import HTTPException
from app.services.assistance.content import generate

async def run(models):
    # Same public, synthetic task for each model. No account or customer data.
    brief = ('Escribe un guion de 30 segundos sobre turismo responsable. '
             'No inventes precios, certificaciones ni estadísticas. Incluye un llamado a revisar fuentes oficiales.')
    results = []
    for model in models:
        try:
            text, source = await generate(brief, model, True)
            results.append({**source, 'status':'generated', 'characters':len(text),
                            'output_sha256':hashlib.sha256(text.encode()).hexdigest(),
                            'human_quality_score':None})
        except HTTPException as error:
            results.append({'model':model, 'status':'unavailable', 'http_status':error.status_code})
    return {'schema':'sgacd-local-content-benchmark-v1', 'synthetic_public_brief':True,
            'quality_verified':False, 'hardware_comparison_validated':False,
            'results':results}

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', action='append', required=True)
    parser.add_argument('--authorize-local-inference', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args=parser.parse_args()
    if not args.authorize_local_inference:
        parser.error('Se requiere --authorize-local-inference para consumir recursos del modelo local.')
    if args.output.exists():
        parser.error('El archivo de evidencia ya existe; utiliza otra ruta.')
    result=asyncio.run(run(args.model))
    # Exclusive/private artifact, no credentials or content.
    fd=os.open(args.output, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
    with os.fdopen(fd,'w') as stream:
        json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    sys.exit(0 if all(item['status']=='generated' for item in result['results']) else 1)
