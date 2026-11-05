FROM python:3.13-alpine@sha256:7984cf56ceaddebe4fefeb75d64000b9f45d8b77b11a09b24524da6cdc3af0c8
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /opt/lumo
COPY bootstrap.py server.py client.py policy.py data.py control.py capabilities.py index.html ./
# Fixed options read as root, irreversible privilege drop before any listening socket.
USER 0:0
EXPOSE 8099
# No Docker healthcheck metadata: Supervisor otherwise waits on absent health events.
CMD ["python", "bootstrap.py"]
