"""Explicit trusted-operator provisioning. Dry-run; never discovers/picks identities."""
import argparse,sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
def main():
    parser=argparse.ArgumentParser(description='Review corporate/ledger identity binding; no credentials stored. Default: dry-run.')
    for name in ['owner-id','reviewer-id']:parser.add_argument('--'+name,type=int,required=True)
    for name in ['ledger-actor-id','provider-id','tenant-id','evidence-digest','valid-until']:parser.add_argument('--'+name,required=True)
    parser.add_argument('--initialize-table',action='store_true',help='Explicitly create only the binding table if missing; no other migrations.')
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    from app.db.session import SessionLocal,engine
    from app.models.corporate import CorporateLedgerBinding
    from app.models.user import Usuario
    from app.services.corporate_ledger import review_binding
    from sqlalchemy.exc import SQLAlchemyError
    from fastapi import HTTPException
    try:
        if args.initialize_table:
            if not args.apply:raise ValueError('DDL requires explicit apply.')
            CorporateLedgerBinding.__table__.create(engine,checkfirst=True)
        with SessionLocal() as db:
            operator=db.get(Usuario,args.reviewer_id)
            if operator is None:raise ValueError('Unknown operator.')
            row=review_binding(db,operator=operator,owner_id=args.owner_id,ledger_actor_id=args.ledger_actor_id,provider_id=args.provider_id,tenant_id=args.tenant_id,evidence_digest=args.evidence_digest,valid_until=datetime.fromisoformat(args.valid_until),apply=args.apply)
            print('APPLIED' if args.apply else 'DRY_RUN: no binding saved')
    except (HTTPException,SQLAlchemyError,ValueError,TypeError):
        print('Binding not saved: verify operator, schema, identity evidence and validity.',file=sys.stderr);return 2
    return 0
if __name__=='__main__':raise SystemExit(main())
