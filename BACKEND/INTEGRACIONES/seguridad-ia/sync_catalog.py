"""Compile upstream Markdown claims into a local discovery catalog, never provider activation."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
TARGET=ROOT/'BACKEND/SGA-CD-BACKEND/app/services/resources/provider_catalog.json'
CATEGORIES={'LLM / Text Generation':'text','Image Generation':'image','Speech-to-Text':'transcription','Text-to-Speech':'speech','Embeddings':'embeddings','Image Recognition / Vision':'vision','Video Generation':'video','Music / Audio Generation':'music','Translation':'translation','Summarization / Extraction':'extraction','Code Generation':'code','Search / RAG':'search','Moderation / Safety':'moderation','Model Hosting / Inference':'hosting','Multi-Modal Aggregators':'multimodal'}

def compile_catalog():
    manifest=json.loads((Path(__file__).resolve().parents[3] / 'INTEGRACIONES/seguridad-ia/free-ai-apis-upstream.json').read_text())
    source=(ROOT/manifest['destination']/'README.md').read_text();category=None;entries=[]
    for line in source.splitlines():
        if line.startswith('## '):category=line[3:].strip()
        if category not in CATEGORIES or not re.match(r'^\|\s*\[',line):continue
        columns=[s.strip() for s in line.strip().strip('|').split('|')]
        if len(columns)!=5:raise ValueError('Upstream table format changed: '+line)
        link=re.fullmatch(r'\[(.+)\]\((https://[^\s]+)\)',columns[0]);docs=re.fullmatch(r'\[Docs\]\((https://[^\s]+)\)',columns[4])
        if not link or not docs:raise ValueError('Unsupported provider link format')
        name,url=link.groups();identifier=hashlib.sha256((category+'\0'+name+'\0'+url).encode()).hexdigest()[:20]
        entries.append({'id':identifier,'category':CATEGORIES[category],'category_label':category,'name':name,'url':url,'description':columns[1],'free_tier_claim':columns[2],'auth_claim':columns[3].strip('`'),'docs_url':docs.group(1),'local_option':'(Local)' in name or name in {'Ollama','LM Studio'},'terms_verified':False,'provider_enabled':False,'quota_verified_at':None,'zero_cost_guaranteed':False})
    if not entries or len({e['id'] for e in entries})!=len(entries):raise ValueError('Empty or duplicate catalog')
    return {'schema':'sgacd-provider-discovery-v1','source_commit':manifest['commit'],'source':'BACKEND/IA/llm/free-ai-apis/README.md','notice':'Directorio de opciones: cuotas y acceso son afirmaciones de la fuente, no verificadas con los proveedores. No activa API ni garantiza gratuidad.','categories':[{'id':value,'label':key} for key,value in CATEGORIES.items()],'entries':entries}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    content=json.dumps(compile_catalog(),ensure_ascii=False,indent=2)+'\n'
    if args.check:
        if not TARGET.exists() or TARGET.read_text()!=content:raise SystemExit('Catálogo desactualizado; ejecuta sync_catalog.py')
    else:TARGET.write_text(content)
    catalog=json.loads(content);print('Discovery catalog:',len(catalog['entries']),'entries;',len(catalog['categories']),'categories; no providers activated.')
if __name__=='__main__':main()
