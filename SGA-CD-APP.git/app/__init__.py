import os
import sys

# Puente de conexión arquitectónico: enlaza app.* con las carpetas locales
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Extender __path__ para resolver dinámicamente tools, agents y core
__path__.append(root_dir)

try:
    import tools
    import core
    import agents
    sys.modules["app.tools"] = tools
    sys.modules["app.core"] = core
    sys.modules["app.agents"] = agents
except Exception as e:
    pass