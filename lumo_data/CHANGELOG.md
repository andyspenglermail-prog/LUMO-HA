# Änderungen

## 0.7.0-capabilities.1

- Geräteauswahl und Bedienung allgemein überarbeitet, nicht nur ein einzelnes
  Jalousienmodell: tatsächliche Fähigkeiten bestimmen die erzeugten Bedienelemente.
- Verständliche Funktionsrollen und getrennte Hauptfunktionen, Anzeigen,
  Einstellungen und Diagnose. Auswahl bleibt überprüfbar und korrigierbar.
- Fähigkeitsabhängige Cover-, Licht-, Klima-, Ventilator-, Zahlen- und
  Auswahlbedienung; vorhandene Schalter bleiben erhalten.
- Position und Lamellenneigung separat, mit expliziter Stoppbedienung.
- Parameter werden gegen aktuelle HA-Grenzen/Optionen geprüft; keine Befehle
  allein durch Sliderbewegung, Funktionsauswahl oder Gestalten.
- Bestätigt, ausstehend und unklar bleiben getrennt; kein automatischer Retry.
- Update derselben App mit unverändertem Konfigurationsschema. Kein vollständiger
  nativer Dashboardexport, keine automatische Installation oder physische Abnahme.

## 0.6.0-devices.2

- Fehler behoben: markierte Gerätefunktionen werden direkt durch
  **Änderungen übernehmen** verknüpft. Der zusätzliche Verknüpfen-Klick
  ist nicht mehr erforderlich, bleibt zum vorherigen Bearbeiten aber möglich.
- Bestehende Beschriftungen und Unterkacheln bleiben erhalten; Abbrechen
  verwirft weiterhin die nicht übernommene Auswahl.
- Bei mehr als acht Funktionen bleibt der Dialog mit verständlichem Hinweis
  offen; es wird keine Teilauswahl still übernommen oder verworfen.
- Keine Änderungen an Backend, Schaltberechtigungen oder Konfigurationsschema.

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
