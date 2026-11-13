"""Legacy service entrypoints must fail before network or placeholder publication."""
import ast,unittest
from pathlib import Path
class Checks(unittest.TestCase):
 def test_all_legacy_publication_entrypoints_fail_closed_without_importing_sdks(self):
  base=Path(__file__).resolve().parents[1]/'app/services'
  for filename,names in [('video_distribution_service.py',('publish_video','publish_video_to_youtube','_publish_video_to_meta')),('meta_uploader.py',('upload_video','_make_request','_finish_upload_session'))]:
   tree=ast.parse((base/filename).read_text())
   for node in ast.walk(tree):
    if isinstance(node,ast.FunctionDef) and node.name in names:
     # Execute the real method AST with no network modules in its globals.
     module=ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[]));namespace={'Dict':dict,'Any':object};exec(compile(module,str(base/filename),'exec'),namespace)
     import inspect
     func=namespace[node.name];args=[None for parameter in inspect.signature(func).parameters.values() if parameter.kind not in (parameter.VAR_POSITIONAL,parameter.VAR_KEYWORD)]
     with self.assertRaisesRegex(RuntimeError,'LEGACY_PUBLISH_DISABLED'):func(*args)
if __name__=='__main__':unittest.main()
