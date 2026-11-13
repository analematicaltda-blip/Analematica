from .army import Army
from .army_store import Store
from .commercial_command_staff import NekoConversationalGeneral,JarviOperationalGeneral,SoupProcessOptimizerGeneral
def service(crm):return Army(Store(crm.store),crm)
def command(crm,body):
 army=service(crm);operation=body.get('operation') if isinstance(body,dict) else None
 if operation=='prepare':return NekoConversationalGeneral(army).prepare(body)
 if operation=='run':return JarviOperationalGeneral(army).execute_mission(body)
 return army.command(body)
def soup(crm,ref):return SoupProcessOptimizerGeneral(service(crm)).evaluate(ref)
