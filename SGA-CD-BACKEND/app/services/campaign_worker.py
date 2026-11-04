"""Dedicated durable scheduler; never use browser timers for actual dispatch."""
import logging
import os
from pathlib import Path
import signal
import time
from app.db.session import SessionLocal
from app.models.campaigns import CampaignScheduler
from app.services import campaign_service as campaigns

log=logging.getLogger('sgacd.campaigns')
stop=False

def shutdown(*args):
    global stop
    stop=True

def pulse(db):
    row=db.get(CampaignScheduler,'node6-campaigns')
    if row is None:row=CampaignScheduler(id='node6-campaigns');db.add(row)
    row.last_seen=campaigns.now();db.commit()
    Path('/tmp/sgacd-campaign-heartbeat').touch()

def main():
    signal.signal(signal.SIGTERM,shutdown);signal.signal(signal.SIGINT,shutdown)
    logging.basicConfig(level=logging.INFO)
    interval=max(2,min(60,int(os.getenv('CAMPAIGN_POLL_SECONDS','10'))))
    while not stop:
        try:
            with SessionLocal() as db:
                pulse(db);processed=campaigns.tick(db,limit=1);pulse(db)
            if processed:continue
        except Exception:
            # Never dump requests, payloads, credentials or signed provider URLs.
            log.error('No se completó el ciclo del calendario; los envíos iniciados requieren conciliación, no reenvío automático.')
        deadline=time.monotonic()+interval
        while not stop and time.monotonic()<deadline:time.sleep(min(1,max(0,deadline-time.monotonic())))
if __name__=='__main__':main()
