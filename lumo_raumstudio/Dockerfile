FROM python:3.13-alpine@sha256:7984cf56ceaddebe4fefeb75d64000b9f45d8b77b11a09b24524da6cdc3af0c8
ARG BUILD_VERSION
ARG BUILD_ARCH
LABEL io.hass.version="${BUILD_VERSION}" io.hass.type="app" io.hass.arch="${BUILD_ARCH}"
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /opt/lumo_raumstudio
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --only-binary=:all: --require-hashes -r requirements.txt
COPY bootstrap.py server.py client.py policy.py store.py settings.py images.py maintenance.py dashboard_reads.py native.py imported.py rooms.py room_store.py area_corrections.py config.json index.html style.css app.js room.js room.css lumo-logo.png ./
COPY mdi.json mdi-LICENSE mdi-APACHE-2.0.txt mdi-provenance.json ./
USER 0:0
EXPOSE 8099
# Bootstrap owns only /data/raumstudio, then drops to UID/GID 65532 before listen.
CMD ["python", "bootstrap.py"]
