from django.core.management.base import BaseCommand
import time
from ...pool08.inbox_worker import run_once
class Command(BaseCommand):
    help='Process the owned local inbox reply queue; explicit worker opt-in required.'
    def add_arguments(self,parser):parser.add_argument('--watch',action='store_true');parser.add_argument('--limit',type=int,default=10)
    def handle(self,*args,**options):
        while True:
            self.stdout.write(str(run_once(options['limit'])))
            if not options['watch']:break
            time.sleep(5)
