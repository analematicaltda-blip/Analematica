"""Offline provider errors cannot be represented as generated content."""
import unittest
from unittest.mock import patch
from app.services.ai_router import AIRouterService
class Checks(unittest.TestCase):
 def test_offline_text_is_explicitly_unavailable(self):
  router=AIRouterService()
  with patch.object(router,'check_ollama_health',return_value={'status':'offline'}),patch.object(router,'check_colibri_health',return_value={'status':'offline'}):
   value=router.generate_text('PRIVATE_PROMPT');self.assertEqual(value['status'],'unavailable');self.assertIsNone(value['text']);self.assertFalse(value['content_generated']);self.assertNotIn('PRIVATE_PROMPT',str(value))
 def test_offline_image_has_no_invented_asset_path(self):
  router=AIRouterService()
  with patch.object(router,'check_open_gen_ai_health',return_value={'status':'offline'}):
   value=router.generate_image_via_open_gen_ai('PRIVATE_PROMPT');self.assertEqual(value['status'],'unavailable');self.assertIsNone(value['image_url']);self.assertFalse(value['content_generated'])
if __name__=='__main__':unittest.main()
