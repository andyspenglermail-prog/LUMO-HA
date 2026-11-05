# Änderungen

## 0.6.0-devices.1

- Update der bestehenden App `lumo_data`, kein zusätzlicher App-Eintrag.
- Horizontale Raum-/Geräteauswahl über dem Raumentwurf.
- Geräte als gemeinsame Kacheln; Auswahl der tatsächlichen Entitäten beim
  Bearbeiten, mit individuellen Unterkacheln und erhaltener Gerätezuordnung.
- Echte aktuelle Werte für ausgewählte Funktionen, ohne Demo-Ersatz.
- Bewusste An/Aus-Aktionen für unterstützte `light`, `switch` und
  `input_boolean`-Entitäten im Bedienmodus. Andere Domänen zunächst Werteanzeige.
- Keine Gerätebefehle beim Laden, Gestalten oder Verschieben. Einzelne
  Befehle werden nicht automatisch wiederholt; unklare Ergebnisse bleiben unklar.
- Verständliche Einrichtungshinweise statt pauschaler Bestandsfehlermeldung.
- Die vier vorhandenen Konfigurationsfelder bleiben unverändert.
- Vollständiger nativer Dashboardexport weiterhin offen.

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
