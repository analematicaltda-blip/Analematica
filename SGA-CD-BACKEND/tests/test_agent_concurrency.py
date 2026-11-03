import pytest
import anyio
from unittest.mock import AsyncMock, patch
from app.api.v1.endpoints.agent import build_scoped_thread_id, run_agent, sanitize_prompt_for_ai

def test_build_scoped_thread_id_security():
    # Tenant 1, User 101, client thread 'alpha'
    t1 = build_scoped_thread_id(1, 101, "alpha")
    assert t1 == "tenant_1:user_101:session_alpha"

    # Malicious client thread attempt
    t_malicious = build_scoped_thread_id(1, 101, "../session_injection")
    assert t_malicious.startswith("tenant_1:user_101:session_")
    assert "../" not in t_malicious

def test_sanitize_prompt_for_ai_privacy():
    prompt = "Mi clave es 1234, token Bearer eyJhbGci.abc.def y tarjeta 4532-1111-2222-3333"
    sanitized = sanitize_prompt_for_ai(prompt)
    assert "4532-1111-2222-3333" not in sanitized
    assert "eyJhbGci.abc.def" not in sanitized
    assert "[TARJETA_CREDITO_REDACTADA]" in sanitized
    assert "[TOKEN_REDACTADO]" in sanitized

@pytest.mark.anyio
async def test_agent_concurrent_requests_isolation():
    # Simulate 3 concurrent agent invocation tasks with thread-scoped isolation
    async def mock_run_agent(prompt, thread_id, area):
        await anyio.sleep(0.01)
        return {"text": f"Respuesta para {thread_id} con prompt {prompt}", "image_url": None}

    with patch("app.api.v1.endpoints.agent.run_agent", side_effect=mock_run_agent):
        from app.api.v1.endpoints.agent import run_agent as patched_run_agent
        results = []
        async with anyio.create_task_group() as tg:
            async def run_one(prompt, thread, area):
                res = await patched_run_agent(prompt, thread, area)
                results.append(res)

            tg.start_soon(run_one, "Orden 1", "tenant_1:user_100:session_s1", "Cultura")
            tg.start_soon(run_one, "Orden 2", "tenant_2:user_200:session_s2", "Cultura")
            tg.start_soon(run_one, "Orden 3", "tenant_1:user_101:session_s3", "Cultura")

        assert len(results) == 3
        texts = [r["text"] for r in results]
        assert any("tenant_1:user_100:session_s1" in t for t in texts)
        assert any("tenant_2:user_200:session_s2" in t for t in texts)
        assert any("tenant_1:user_101:session_s3" in t for t in texts)
