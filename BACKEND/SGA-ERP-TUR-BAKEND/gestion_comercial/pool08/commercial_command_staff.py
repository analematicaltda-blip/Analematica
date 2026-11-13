"""Owned commercial adapters; original general sources stay in Analemática."""
class NekoConversationalGeneral:
 def __init__(self,army):self.army=army
 def prepare(self,body,**kwargs):return self.army.command(body,**kwargs)
class JarviOperationalGeneral:
 def __init__(self,army):self.army=army
 def execute_mission(self,body,**kwargs):return self.army.command(body,**kwargs)
class SoupProcessOptimizerGeneral:
 def __init__(self,army):self.army=army
 def evaluate(self,ref):return self.army.optimize(self.army.get(ref)['results'])
