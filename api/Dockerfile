# Build from the repo root: docker build -f api/Dockerfile .
FROM python:3.14-slim

# iputils-ping for /api/hosts/{id}/ping. Unprivileged ICMP sockets
# (net.ipv4.ping_group_range, Docker's default) let it run without root.
RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY api/requirements.txt api/requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt

RUN useradd --system --uid 10001 --no-create-home app \
    && mkdir -p /app/logs \
    && chown app:app /app/logs

COPY api/ api/

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=2)"]

# The API is only reachable through the web container; TRUST_PROXY handles X-Forwarded-For
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-proxy-headers"]
