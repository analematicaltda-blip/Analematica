"""Local API operation does not depend on an optional provider credential."""
import asyncio
import unittest
from unittest.mock import patch
from fastapi import HTTPException
from app.api.v1.endpoints import agent, sales_agent

class OptionalProviderTests(unittest.TestCase):
    def test_culture_agent_reports_unavailable_without_provider(self):
        with patch.object(agent, 'cultura_colonel_agent', None):
            with self.assertRaises(HTTPException) as caught:
                asyncio.run(agent.run_agent('Local test', 'test-thread', 'Cultura'))
            self.assertEqual(caught.exception.status_code, 503)

    def test_sales_agent_reports_unavailable_without_provider(self):
        with patch.object(sales_agent, 'sales_agent_executor', None):
            with self.assertRaises(HTTPException) as caught:
                asyncio.run(sales_agent.invoke_sales_agent(sales_agent.SalesAgentInput(query='Local test')))
            self.assertEqual(caught.exception.status_code, 503)

if __name__ == '__main__':
    unittest.main()
