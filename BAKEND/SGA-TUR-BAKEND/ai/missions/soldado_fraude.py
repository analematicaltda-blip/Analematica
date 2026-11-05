import logging
class FraudSoldier:
    async def execute(self, mission_data):
        data = mission_data.get("data", {})
        if data.get("amount", 0) > 10000000:
            return {"status": "blocked"}
        return {"status": "success"}
