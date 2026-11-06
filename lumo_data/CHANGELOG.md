# Änderungen

## 0.11.0-native.3 — Raster, Ausrichtung, Gruppen und Entitätswechsel

- Dauerhaft sichtbares 12-Spalten-Abschnittsraster mit erkennbaren Arbeitsgrenzen.
  Echte Layoutabstände, Links/Mitte/Rechts und horizontales Ziehen für eine einzelne
  Inhaltskachel je Section; keine bloße CSS-Verschiebung im Designer.
- Layoutzellen mit eigener Größe, Reihenfolge, Gruppenzuordnung und Fixierung;
  durchgehend in Verlauf, Browserspeicherung, Backup, Export und unterstütztem Import.
  Bestehende Dokumente werden nicht automatisch umgeordnet oder neu dimensioniert.
- Neue leere Gruppen sofort sichtbar: benannte Ablageziele, Quellen direkt zur
  Gruppe hinzufügen, vorhandene Inhalte zuweisen, umbenennen und entfernen.
  Gruppenwerkzeuge liegen außerhalb der nativen Kachelgeometrie und verdecken
  auch am Smartphone nicht die Kachelbearbeitung.
- Kacheleditor mit Raum-/Typfilter, Suche nach Funktion/Gerät/ID, vollständiger
  paginierter Auswahl und explizitem Ersetzen/Hinzufügen/Entfernen. Eigene Einstellungen
  und ausgewählte Quellen bleiben bei Filtern, laufenden Werten und Abbrechen erhalten.
- Darstellungsvorschläge anhand gelesener Fähigkeiten, ohne automatische Umstellung
  oder Geräteaktionen. In-Tile-Bedienung und bestehende Freigabegrenzen erhalten.
- Begrenzte native Validierungsgrammatik um kanonische leere Grid-Container ergänzt;
  keine neuen App-Berechtigungen, Services, Optionen oder automatische Installation.
- Grenzen: Ausrichtung innerhalb der Section, nicht am Fensterrand. HA zeigt für
  leere Grid-Container nur im einzelnen Karteneditor „Empty card“; normale native
  Darstellung ist leer. Leere Entwurfsgruppen werden nicht exportiert. Themeexport,
  installierte HA-Kompatibilität und physische/qualitative Abnahme bleiben offen.

## 0.11.0-native.2 — Raster und Bedienung innerhalb der Kacheln

- Dezentes sichtbares Designraster wiederhergestellt, auch für leere Entwürfe;
  dunklen Restbereich aus alten Stilregeln entfernt. Im Test bleibt das Raster aus.
- Ausgelagerte Test-Bedienliste entfernt. Werte und echte freigegebene Bedienung
  stehen in ihrer jeweiligen Kachel; Moduswechsel verändert weder Position noch Größe.
- Hauptfunktionen gewählter Bedien-Darstellungen direkt erreichbar. Zusätzliche
  Fähigkeiten und Status über die kacheleigene Funktionsauswahl; kompakte Kacheln
  scrollen innen, ohne gespeicherte manuelle Maße zu überschreiben.
- Explizites Senden, 44-Pixel-Ziele, gemeinsame Zustände mehrfacher Bindungen,
  Lift/Lamellen-Stopp, Quellenqualität und Schutz gegen verspätete Freigaben erhalten.
- Keine neuen Berechtigungen, Backendänderungen oder automatische Installation.
  Themeexport und physische/qualitative Abnahme sind damit nicht erledigt.

## 0.11.0-native.1 — nur native HA-Dashboards

- Ausgabeprofil-Auswahl und aktiven freien Editor entfernt. Native Dokumente,
  Backups, Rückgängig/Wiederholen und nicht abbildbare Legacy-Inhalte bleiben erhalten.
- Neuer Ablauf Dashboard → Raum → Design & Display → Dein Raumentwurf.
  Bestehende lokale Entwürfe und unterstützte HA-Kopien öffnen direkt im Raumentwurf.
- Sections-Geometrie an das offizielle HA-Frontend angeglichen: Abschnittsbreiten,
  responsive Spaltenzahl, Abstände, Überschriften und Kartenspannen. Tatsächlicher
  gemischter UI-Export gegen natives Vollview geprüft, nicht nur YAML validiert.
- Entwurfs-/Testmodus mit expliziter gebundener Gerätebedienung und sicherer
  Rückkehr zum Entwurfsmodus bei Navigation, Laden, Trennen oder Verbergen.
- Dashboard anlegen mit Titel, originaler HA-Symbolauswahl, URL-Namen und expliziten
  Admin-/Seitenleistenflags. Eigener einmaliger Token, tatsächliche Adminprüfung,
  Konfliktverweigerung sowie vollständiger Metadaten-/Konfigurations-Readback.
- Nur neue Dashboards nach Benutzerbestätigung; kein automatisches Update/Delete/Retry.
  Teilfehler bleiben sichtbar. Keine atomare HA-Transaktion gegen parallele Schreiber.
- Keine zusätzlichen App-Berechtigungen, Optionen, Installation oder zweite App.
  Layoutnachweis bedeutet keine universelle Theme-/Icon-/Schriftparität; frühere
  Stilpräferenzen sind keine nativen HA-Themes. Physische und installierte Abnahme offen.

## 0.10.0-studio.1 — geführtes Raumstudio

- Vier Schritte beim Öffnen: Dashboard auswählen/neu, Design & Display,
  Raum auswählen/neu im Entwurf, großer Raumentwurf mit Speichern/Exportieren darunter.
- Bestehende Browserentwürfe und Backups bleiben lesbar. Zusätzlicher ausdrücklicher
  Nur-Lese-Abruf vorhandener HA-Dashboards; unterstützte Sections werden als neue
  lokale Kopie geöffnet. Unvollständig abbildbare Konfigurationen werden abgelehnt.
- Suchbare Quellen nach Gerät/Raum mit freundlichen Namen und prüfbaren Entitäts-IDs.
  13 lokal gebündelte MDI-Symbole mit vollständigen Lizenztexten; unbekannte Symbole
  erhalten einen neutralen Ersatz. Unterstützte MDI-Kartenicons werden exportiert.
- Große 12-Spalten-Arbeitsfläche mit echter Maus-/Touch-Verschiebung, Größenänderung,
  Einrastvorschau, Abbruch, Fixierungen und Rückgängig/Wiederholen.
- Aktuelle HA-Werte, Quellenqualität, manuelle Entwurfsänderungen und das freie
  Vorschauprofil bleiben erhalten. Keine zusätzlichen App-Berechtigungen oder Optionen.
- Speichern bleibt Browserspeicherung, Export bleibt Dateidownload. Keine produktive
  Dashboard-/Bereichsänderung, keine neue App und keine automatische Installation.
- Sections sind Reihenfolge und Spans, keine freien Pixelpositionen. Vorschau-Styles
  sind weiterhin keine nativen HA-Themes. Physischer Touch und Nutzerabnahme offen.

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
