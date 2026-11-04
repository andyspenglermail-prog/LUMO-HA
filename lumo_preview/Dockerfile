FROM python:3.13-alpine@sha256:7984cf56ceaddebe4fefeb75d64000b9f45d8b77b11a09b24524da6cdc3af0c8

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /opt/lumo
COPY bootstrap.py server.py bridge.py validation.py index.html devicebook.html ./
# Root only reads fixed Supervisor options and drops all identities/caps before serving.
USER 0:0
EXPOSE 8099
# Docker health checks inherit USER 0; disable recurring privileged helpers.
# Supervisor ingress and the constant /health endpoint remain available post-drop.
HEALTHCHECK NONE
CMD ["python", "bootstrap.py"]
