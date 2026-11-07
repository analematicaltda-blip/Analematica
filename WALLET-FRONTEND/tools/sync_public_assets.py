"""Only public role/readiness metadata; never exports a private workspace."""
import argparse,json
from pathlib import Path
from sgacd_wallet_offline.army import catalog
from sgacd_wallet_offline.readiness import all_items
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
for name,data in [('team.json',catalog()),('pending.json',all_items())]:
    content=json.dumps(data,ensure_ascii=False,indent=2)+'\n';target=ROOT/'web'/name
    if args.check:
        if not target.exists() or target.read_text()!=content:raise SystemExit('Public asset is stale: '+name)
    else:target.write_text(content)
