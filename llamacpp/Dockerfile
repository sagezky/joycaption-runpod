FROM ghcr.io/ggml-org/llama.cpp:server-cuda-b9002
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && (pip3 install --no-cache-dir --break-system-packages runpod requests aiohttp \
        || pip3 install --no-cache-dir runpod requests aiohttp)
COPY handler.py /handler.py
ENTRYPOINT ["python3", "-u", "/handler.py"]
