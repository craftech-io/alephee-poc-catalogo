import base64
import hashlib
import hmac
import json
import os
import time
from pathlib import Path

import httpx
import pytest

pytestmark = pytest.mark.e2e
ROOT = Path(__file__).resolve().parents[3]


def _b64(obj) -> str:
    return base64.urlsafe_b64encode(json.dumps(obj, separators=(",", ":")).encode()).rstrip(b"=").decode()


def _token(user_id: str, secret: str, ttl: int = 600) -> str:
    """Same token as apps/web/sign.mjs: HS256 over base64url header and body."""
    now = int(time.time())
    body = _b64({"alg": "HS256", "typ": "JWT"}) + "." + _b64({"sub": user_id, "iat": now, "exp": now + ttl})
    signature = base64.urlsafe_b64encode(hmac.new(secret.encode(), body.encode(), hashlib.sha256).digest()).rstrip(b"=")
    return f"{body}.{signature.decode()}"


def _api_url() -> str | None:
    outputs = ROOT / ".sst/outputs.json"
    if os.environ.get("API_URL"):
        return os.environ["API_URL"]
    return json.loads(outputs.read_text()).get("Chat") if outputs.exists() else None


def test_deployed_chat_maps_a_sku_with_v2():
    base, secret = _api_url(), os.environ.get("CHAT_HMAC_SECRET")
    if not base or not secret:
        pytest.skip("no deployed chat URL or CHAT_HMAC_SECRET")
    headers = {"authorization": f"Bearer {_token('warroom-e2e', secret)}"}
    thread = f"e2e-{int(time.time())}"
    posted = httpx.post(f"{base.rstrip('/')}/mensajes", json={"texto": "Mapea el SKU 94701411 con la V2", "hilo": thread},
                        headers=headers, timeout=30)
    assert posted.status_code == 200
    deadline = time.time() + 120
    while time.time() < deadline:
        time.sleep(4)
        got = httpx.get(f"{base.rstrip('/')}/mensajes", params={"hilo": thread}, headers=headers, timeout=30).json()
        messages = got if isinstance(got, list) else got.get("mensajes") or got.get("items") or []
        answers = [m for m in messages if m.get("rol") in ("assistant", "error")]
        if answers:
            text = " ".join(str(m.get("texto", "")) for m in answers)
            assert answers[-1]["rol"] == "assistant", text
            assert "Calotas" in text
            return
    pytest.fail("the deployed chat did not answer in 120 s")
