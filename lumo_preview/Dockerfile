FROM python:3.13-alpine@sha256:7984cf56ceaddebe4fefeb75d64000b9f45d8b77b11a09b24524da6cdc3af0c8

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /opt/lumo
COPY bootstrap.py server.py bridge.py validation.py index.html devicebook.html ./
# Root only reads fixed Supervisor options and drops all identities/caps before serving.
USER 0:0
EXPOSE 8099
# The pinned base has no healthcheck; omit HEALTHCHECK NONE because Supervisor
# treats its nonempty Docker metadata as a check and waits for absent health events.
# No recurring privileged helper; ingress and post-drop /health remain unchanged.
CMD ["python", "bootstrap.py"]
