# Änderungen

## 0.9.0-designer.3 — natives Raumstudio mit HA-Daten

- Vertraute Raumstudio-Oberfläche im nativen Profil: zentriertes „Dein Raumentwurf“,
  breite Arbeitsfläche, sichtbares Design & Display und Raumauswahl aus dem HA-Bestand.
- Raumwechsel wählen oder ergänzen die passende Ansicht; bestehende Entwürfe,
  Bindungen und manuelle Anpassungen bleiben erhalten. Raumübergreifende Quellen
  einschließlich Quellen ohne Raumzuordnung bleiben ausdrücklich auswählbar.
- Drei Vorschau-Styles und Display-/Größeneinstellungen wirken auf den nativen
  Entwurf. Neutrale Editorwerkzeuge; Darstellungseinstellungen im strukturierten
  Dokument mit Undo/Redo, Speicherung und Backup. Alte Dokumente bleiben lesbar.
- Reale Räume, Gerätezuordnungen, Entitäten und aktuelle Werte über den bestehenden
  Laufzeitweg zu HA, keine eingebetteten Hausdaten und kein Demoersatz.
  Herkunft, Abrufzeit und Datenqualität sind prüfbar; ungültige oder nicht verfügbare
  Werte werden nicht als gültige Messwerte ausgegeben.
- Desktop-, Tablet- und Smartphone-Layout, Maus und emulierter Touch sowie HTTP/HTTPS
  geprüft. Separater Test des vollständigen Browser→App→CoreClient-Datenwegs gegen
  eine lokale HA-Testgegenstelle. Keine behauptete Abnahme der Hausinstallation.
- Native HA-Themes/Pixelgeometrie werden nicht gleichgesetzt; Vorschau ist kein
  nativer HA-Live-Renderer. Kein automatisches Veröffentlichen produktiver Dashboards.
- Bestehender HTTP-Fix, freies Profil und Bediengrenzen erhalten. Backend,
  Berechtigungen, Optionen und App-Slug unverändert; Installation durch den Benutzer.

## 0.9.0-designer.2 — nativer Designer über HTTP

- Fehler behoben: Beim Zugriff über eine gewöhnliche HTTP-Adresse blieb nach
  Auswahl von „Natives HA-Dashboard“ die bisherige Ansicht stehen.
- Gemeinsame ID-Erzeugung aus kryptografischen Zufallsbytes statt direkter
  `randomUUID()`-Aufrufe; gilt für Dashboards, Ansichten, Gruppen und Bausteine.
- Bestehende Dokument-IDs und Speicherformate bleiben unverändert; keine Migration.
- HTTP- und HTTPS-Browserregressionen in einer synthetischen Iframe-Einbettung:
  Profilwechsel, Anlegen, Rückgängig/Wiederholen, Speicherung, Neuladen und Export.
- Keine Änderung an Backend, Berechtigungen, Optionen, Netzwerk oder TLS.
  Installation und Neustart bleiben beim Benutzer; keine neuen Funktionen.

## 0.9.0-designer.1 — erste Designer-Zwischenversion

- Update derselben LUMO-Data-App; Slug, Konfigurationsschema und Berechtigungen unverändert.
- Strukturiertes Dashboardmodell mit Ansichten, direkten Funktionsbausteinen und
  optionalen geräteübergreifenden Gruppen. Verschieben/Größenänderung, Fixierungen,
  Rückgängig/Wiederholen und explizite Browserspeicherung mit Versionen/Backups.
- Validierter nativer HA-Sections-Export als YAML/JSON für unterstützte Bausteine.
  Warnungen/Grenzen bleiben sichtbar; kein automatisches Anlegen produktiver Dashboards.
- Freies Vorschauprofil und drei Ausgabestile erhalten. Geräteinnenraster,
  Mehrfachkacheln und begrenzte Zustandsaktualisierung aus dem unveröffentlichten
  0.8-Entwicklungsstand enthalten; Analytics-Livepainting zusätzlich korrigiert.
- Native Ansichten lesen ihre eigenen Bindungen; die Quellenauswahl wird auch
  beim Bestandsladen nach bereits ausgewähltem nativem Profil aktualisiert.
- Technische Zwischenprüfung: 207 Haupttests plus drei Unterfälle vor dem letzten
  Discovery-Fix; danach drei gezielte Regressionen bestanden und unabhängiges
  statisches Nachreview bestanden. Kein vollständiger Gesamtsuite-Neulauf danach.
- Echter UI-Export in einem nativen HA-Vollview mit synthetischen Daten geprüft.
  Installierte HA-Kompatibilität, physischer Touch und qualitative Nutzerabnahme offen.
- Keine vollständige native Style-/Analytics-/Formelparität, keine KI und keine
  automatische Installation. Installation und Neustart bleiben beim Benutzer.

## 0.8.0-grid-live.1 — unveröffentlichter Entwicklungsstand

- Geräte als frei bestückbare Kacheln mit dimensioniertem Innenraster;
  Funktionsbausteine lassen sich positionieren und in ihrer Größe ändern.
- Kompakte Messwerte und größere Bedienbausteine innerhalb derselben Kachel;
  optionale Beschriftungen statt verpflichtender technischer Entitätsnamen.
- Mehrere unabhängige Kacheln für dasselbe Gerät, auch mit denselben Entitäten.
  Gestaltung bleibt getrennt, gelesene Zustände und Bedienstatus bleiben gemeinsam.
- Automatische, begrenzte Zustandsabrufe für die verbundenen Entwurfsansichten.
  Positions- und Messwertänderungen werden ohne manuellen Aktualisierungsklick
  nachgeführt, soweit Home Assistant neue Werte meldet. Keine erfundene Interpolation.
- Automatische Leseabrufe lösen keine Gerätebefehle aus; bewusstes Senden bleibt
  erforderlich. Keine zusätzlichen Berechtigungen und keine automatische Installation.
- Vollständiger nativer Dashboardexport und physische Touchabnahme bleiben offen.

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
