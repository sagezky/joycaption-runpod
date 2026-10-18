import os, shlex, subprocess, sys, time

import aiohttp
import requests
import runpod

BASE = "http://127.0.0.1:8000"

# ponytail: all vLLM flags come from env, so one image serves any model
proc = subprocess.Popen(
    ["vllm", "serve", os.environ["MODEL_NAME"],
     "--host", "127.0.0.1",
     "--served-model-name", os.environ.get("SERVED_MODEL_NAME", "joycaption"),
     *shlex.split(os.environ.get("VLLM_ARGS", ""))]
)

for _ in range(900):
    if proc.poll() is not None:
        sys.exit(f"vllm exited with code {proc.returncode}")
    try:
        if requests.get(f"{BASE}/health", timeout=2).ok:
            break
    except requests.RequestException:
        pass
    time.sleep(1)
else:
    sys.exit("vllm did not become healthy in 15 min")


ROUTES = {"/v1/chat/completions", "/v1/completions", "/v1/models", "/v1/embeddings"}


async def handler(job):
    # same input shape as runpod's worker-vllm, so /openai/v1/* routes keep working
    route = job["input"]["openai_route"]
    body = job["input"].get("openai_input") or {}
    if route not in ROUTES:
        yield {"error": f"route not allowed: {route}"}
        return
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=None)) as s:
        if route == "/v1/models":
            async with s.get(BASE + route) as r:
                yield await r.json()
        else:
            async with s.post(BASE + route, json=body) as r:
                if body.get("stream"):
                    async for line in r.content:
                        if line.strip():
                            yield line.decode().strip() + "\n\n"
                else:
                    yield await r.json()


runpod.serverless.start({
    "handler": handler,
    "concurrency_modifier": lambda _: int(os.environ.get("MAX_CONCURRENCY", "4")),
    "return_aggregate_stream": True,
})
