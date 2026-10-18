FROM vllm/vllm-openai:v0.28.0
RUN pip install --no-cache-dir runpod
COPY handler.py /handler.py
ENTRYPOINT ["python3", "-u", "/handler.py"]
