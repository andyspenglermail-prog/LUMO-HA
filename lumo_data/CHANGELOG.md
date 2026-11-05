# Änderungen

## 0.5.0-data.1

- Erste Veröffentlichung der separaten LUMO-Data-Entwicklungsapp im HA-Repository.
- Generische, rein lesende HA-Anbindung des Dashboard-Designers: Bestand,
  aktuelle Zustände und verfügbare Historie; ohne eingebettete Hausinventur.
- Vorhandene Editor-, Theme-, Kachel- und Analysefunktionen übernommen.
- Historieneinheiten, Zeitfenster, numerische/statusbezogene Darstellung,
  getrennte Zeitangaben und HTTP-Annahmegrenzen korrigiert.
- AMD64 und ARM64 (ARM-Start emuliert geprüft).
- Datenzugriff zunächst deaktiviert; explizite Benutzerfreigabe erforderlich.
- Vorhandene Offline-App unverändert; kein automatischer Ersatz und keine Migration.
- Vollständiger nativer Dashboardexport und native HA-Betriebsabnahme weiterhin offen.
