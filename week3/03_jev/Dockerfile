# tau-4b System One server, with the model weights baked into the image.
#
# Build (from this folder, takes a while: ~9 GB of weights are downloaded):
#     docker compose build
# Run:
#     docker compose up -d
#
# CPU-only image. Layers are ordered so that editing tau_server.py does not
# re-download anything: dependencies first, then the weights, the code last.

FROM python:3.12-slim

# Keep the Hugging Face cache in a fixed place inside the image
ENV HF_HOME=/opt/hf \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1

# CPU build of torch is ~5x smaller than the CUDA build
RUN pip install torch==2.9.1 --index-url https://download.pytorch.org/whl/cpu \
 && pip install "transformers==5.20.2" "fastapi==0.156.8" "uvicorn==0.40.0" "huggingface_hub==2.2.0"

# Download the weights and the model's own code at build time (one 9 GB layer)
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download('cisimcik/tau-4b')"

# From here on, never touch the network for the model
ENV HF_HUB_OFFLINE=1 \
    TAU_HOST=0.0.0.0

WORKDIR /app
COPY tau_server.py .

EXPOSE 8000
CMD ["python", "tau_server.py"]