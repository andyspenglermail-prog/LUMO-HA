FROM python:3.13-alpine@sha256:7984cf56ceaddebe4fefeb75d64000b9f45d8b77b11a09b24524da6cdc3af0c8

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /opt/lumo
COPY server.py index.html devicebook.html ./
USER 65532:65532
EXPOSE 8099
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD ["python", "-c", "import http.client,sys; c=http.client.HTTPConnection('127.0.0.1',8099,timeout=2); c.request('GET','/health'); r=c.getresponse(); status=r.status; r.read(64); c.close(); sys.exit(0 if status==200 else 1)"]
CMD ["python", "server.py"]
