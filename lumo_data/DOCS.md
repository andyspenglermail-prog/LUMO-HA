# LUMO Data · 0.10.0-studio.1 · Geführtes Raumstudio

Der verbundene Einstieg führt durch vier Schritte: **Dashboard → Design & Display →
Raum → Dein Raumentwurf**. Quellen haben suchbare Geräte-/Funktionsnamen und lokale
MDI-Symbole; ihre exakten Entitätskennungen bleiben prüfbar. Räume und aktuelle Werte
kommen aus der bestehenden HA-Verbindung, ohne eingebettete Hausdaten oder Demoersatz.

**Update für die bestehende LUMO-Data-App; Installation durch den Benutzer.**
Diese v1.5-Zwischenversion entwickelt das native Dashboard-Profil im bestehenden
Raumstudio: strukturiertes Modell, direkte Funktionen/optionale Gruppen, Rasterbearbeitung,
lokale Browserversionen/Backups und validierten YAML/JSON-Export.
Der Designer wird direkt über die bestehende App in Home Assistant geöffnet.
Es gibt keine automatische native HA-Dashboardanlage und keinen HA-Rollback.
Die Gestaltungsvorschau und Konfigurationsprüfung sind kein nativer Live-Renderer.

Die Veröffentlichung ersetzt Version 0.9.0-designer.3 im bestehenden Repository.
Sie löst selbst keine Installation, keinen Neustart und keine Geräteaktion aus.
Slug, Optionen, Schema und Berechtigungen wurden für diese Zwischenversion nicht erweitert.

LUMO ist ein Home-Assistant-Dashboard-Designer. Dieser Entwicklungsstand
verbindet den Designer generisch mit Home Assistant. Neben echten Zustandswerten
sind bewusst ausgelöste Aktionen passend zu den tatsächlichen Gerätefähigkeiten möglich.
Er ist nicht selbst das fertige native HA-Dashboard.

## Bestehende LUMO-Data-App aktualisieren

Im bereits eingebundenen LUMO-Repository im Store-Menü **Nach Updates suchen**
ausführen. Anschließend die bereits installierte **LUMO Data** aktualisieren.
Der Slug bleibt `lumo_data`; der neue Name lautet **LUMO Data · Geräte & Bedienung**.
Keine Deinstallation und keine zweite LUMO-Data-Installation erforderlich.
Die bestehende `lumo_preview` wird weder ersetzt noch umkonfiguriert.

Falls das Repository noch fehlt, unter **Einstellungen → Apps → App-Store →
Menü ⋮ → Repositories** `https://github.com/andyspenglermail-prog/LUMO-HA`
hinzufügen. Ältere HA-Oberflächen nennen Apps noch Add-ons.

## Einrichtung

1. Die bestehende LUMO-Data-App aktualisieren; bei Erstnutzung installieren.
   Die Veröffentlichung allein startet oder installiert nichts. Die bisherigen
   Konfigurationsfelder bleiben erhalten.
2. In ihrer Konfiguration `allowed_user_ids` mit der eigenen HA-Benutzer-ID
   befüllen. Die Benutzer-ID steht in der HA-Benutzerverwaltung bei aktivem
   erweitertem Modus. Gemeint ist die ID, nicht Anzeigename oder Benutzername.
3. `enabled` bewusst auf `true` setzen. Mit `false` bleiben Datenabrufe und
   Schaltaktionen gesperrt. Freigegebene Benutzer können in dieser Version
   unterstützte Funktionen im Bedienmodus ausdrücklich schalten.
4. `allowed_entity_patterns` bei Bedarf eingrenzen, z. B. `sensor.*`.
   Eine leere Erlaubnisliste lässt alle nicht ausgeschlossenen Entitäten zu.
   `denied_entity_patterns` kann zusätzliche Ausschlüsse enthalten.
5. Konfiguration speichern, App starten und **Weboberfläche öffnen** wählen.
6. Der Designer beginnt mit der Dashboardauswahl. Dem Ablauf unten folgen.
   Das bisherige freie Vorschauprofil bleibt über die Profilauswahl erreichbar;
   dort zunächst **Bestand laden**, dann einen Raum und ein Gerät auswählen.
   Unter **Bearbeiten** Funktionen mit ihren Bedienmöglichkeiten prüfen,
   die gewünschten Funktionen markieren und direkt
   **Änderungen übernehmen** wählen. Der zusätzliche Knopf **Gewählte Funktionen
   verknüpfen** ist nur nötig, wenn die Unterkacheln schon vor dem Übernehmen
   weiter bearbeitet werden sollen.
   Aktuelle Werte werden für die eingebundenen Funktionen automatisch nachgeführt,
   solange die verbundene Ansicht sichtbar ist. **Werte aktualisieren** bleibt als
   manueller Abruf verfügbar; **Verlauf laden** liest Historie ausdrücklich.
   Es werden keine Hausdaten mitgeliefert oder automatisch vorbelegt.

Nach einer Optionsänderung die App neu starten: Eine erkannte Änderung sperrt
weitere Datenabrufe und Bedienaktionen bis zum Neustart. Keine HA-Tokens in Browserfelder eintragen.
Die App erhält ihren Zugriff intern über den Supervisor und prüft zusätzlich
Ingress und die freigegebenen Benutzer-IDs. Direkter Portzugriff ist nicht vorgesehen.

## Der geführte Ablauf

1. **Dashboard auswählen oder neu:** Gespeicherte LUMO-Entwürfe dieses Browsers
   öffnen oder neu beginnen; der Name ist optional. **HA-Dashboards laden** liest
   die freigegebene Liste ausdrücklich. **Als lokale Kopie öffnen** übernimmt nur
   vollständig unterstützte native Sections als neues Dokument, ohne das Original
   zu ändern. Keine erfundene Standard-Dashboardliste. Admin-only-Dashboards werden
   nicht angeboten; Custom Cards, unbekannte Aktionen, Styles und nicht abbildbare
   automatische Größen führen zu einer vollständigen Ablehnung statt Datenverlust.
2. **Design & Display:** Einen der drei umgesetzten Styles wählen. Displayprofil,
   Orientierung und CSS-Maße sind optional. Die übrigen Styles bleiben als geplant
   markiert. Werkzeuge bleiben neutral, Entitäten und Messwerte unverändert.
3. **Raum:** Für vorhandene HA-Räume **Bestand laden**, dann Raum auswählen und
   **Raum öffnen**. Alternativ eine neue Raumansicht im Entwurf anlegen. Es wird
   kein realer HA-Bereich erstellt. Bereits gestaltete Räume bleiben erhalten.
4. **Dein Raumentwurf:** **＋ Quellen** öffnet die suchbare Geräte-/Funktionsauswahl.
   Namen und Symbole stehen im Vordergrund; **Details** zeigt exakte IDs/Herkunft.
   Neue Quellen sind zunächst reine Wertanzeigen und schalten nichts. Über die
   Bearbeitung eine tatsächlich unterstützte Darstellung wählen. Am Griff ziehen,
   an der Ecke vergrößern: Die Zielvorschau rastet im 12-Spalten-Raster ein.
   Darunter **Dashboard speichern** oder **Dashboard exportieren** wählen.

**Speichern** sichert ausschließlich in diesem Browser. Zusätzlich ein Backup
unter **Weitere Werkzeuge · Funktionen, Gruppen & Sicherungen** herunterladen;
Browserdaten sind kein gemeinsamer HA-Speicher. **Exportieren** prüft die Konfiguration
und bietet YAML/JSON als Download, nicht als automatische HA-Veröffentlichung.
Fehler sperren den Export; Warnungen vor Verwendung prüfen.
Unter **Quellen & Datenqualität prüfen** bleiben Herkunft, Zuordnung und Abrufzeiten
einsehbar. Unbekannte oder veraltete Werte werden nicht als gültige frische Werte ausgegeben.
Zurückgehen zwischen den Schritten erhält den aktuellen Entwurf. Eine andere
Dashboardauswahl schützt ungespeicherte Änderungen durch eine Rückfrage.

13 MDI-Symbole sind lokal gebündelt, ohne CDN-Abruf. Bekannte Metadaten werden
bevorzugt; unbekannte/custom Symbole haben einen sichtbaren neutralen Ersatz.
Native Tile-Karten können gültige MDI-Icons übernehmen. Icons für Gauge/History
bleiben Vorschauoptionen mit Exportwarnung. Es gibt keine vollständige Icon-Paritätszusage.

Die native Ausgabe verwendet das HA-Sections-Raster, nicht freie Pixelpositionen.
Die drei freien Ausgabestile werden nicht unverändert in native HA-Themes übersetzt.
Nicht alle Analyse-, Formel- oder Cockpitdarstellungen sind nativ exportierbar.
Es gibt keine automatische Übernahme in ein produktives HA-Dashboard.
Das bisherige freie Vorschauprofil bleibt getrennt erhalten; ein Legacyimport
übernimmt freie Geometrie nicht stillschweigend als natives Layout.

## Gerätekacheln im Innenraster gestalten (freies Vorschauprofil)

- **Gerät hinzufügen** legt eine neue Kachel an, auch wenn für dieses Gerät schon
  eine Kachel vorhanden ist. Jede Kachel hat ihren eigenen Namen und ihre eigene
  Auswahl/Anordnung. Dieselbe Entität darf in mehreren Kacheln vorkommen.
- Unter **Bearbeiten** die Funktionen auswählen. **Gewählte Funktionen verknüpfen**
  macht die Bausteine bereits innerhalb des offenen Editors gestaltbar; direktes
  **Änderungen übernehmen** bleibt ebenfalls möglich.
- Unter **Funktionen frei platzieren** den Griff eines Bausteins zum Verschieben
  und den Eckgriff zum Vergrößern/Verkleinern ziehen. Pfeiltasten an den Griffen
  sowie Zahlenfelder sind die Alternative. Ungültige Platzierungen werden abgewiesen.
- Gemeinsames Raster: sechs Spalten, Zellen 96 × 80 CSS-Pixel, Abstand 8 Pixel.
  Die Darstellung bestimmt die Mindestgröße. **Nur Wert** kann ein einzelnes Feld
  belegen; **Bedienung** benötigt mehr Platz. **Beschriftung anzeigen** ist optional.
- Bis zu 32 Funktionen pro Gerätekachel; bestehende andere Kompositionen behalten
  ihre Grenzen. Freie Lücken bleiben erhalten. Auf schmalen Bildschirmen scrollt
  das Innenraster lokal, statt die gespeicherte Anordnung ungefragt zu verändern.
- Erst **Änderungen übernehmen** speichert in den aktuellen Tab-Entwurf.
  **Abbrechen** verwirft die offenen Änderungen. Das ist keine dauerhafte Speicherung.
- **Quelldetails** zeigt IDs und Herkunft gemeinsam für die Gerätekachel als
  Momentaufnahme beim Öffnen. Die normale Kachel braucht keine technischen ID-Titel.

## Automatische Zustandsaktualisierung

Nach **Bestand laden** werden die eingebundenen Funktionen der aktuellen sichtbaren
Raumansicht automatisch gelesen: etwa zwei Sekunden nach Abschluss des vorherigen
Abrufs, in Paketen von höchstens 32 unterschiedlichen Entitäten. Doppelte Ansichten
teilen sich die Beobachtungen. Dies ist begrenztes Polling, keine Push-Verbindung.
Verbindungsfehler markieren alte Werte und verlängern den Leseabstand. Trennen oder
Verbergen der Seite pausiert die Abrufe. Ein bereits im Backend laufender Abruf
kann noch auslaufen; eine Bedienaktion kann hinter diesem begrenzten Abruf warten.

Automatische Lesevorgänge verändern weder Rasterpositionen noch ungesendete Eingaben
und wiederholen keine Befehle. Unklare Ergebnisse bleiben unklar. Die ausdrückliche
Schaltaktion bzw. **Senden** bleibt erforderlich; **Werte aktualisieren** erlaubt
weiterhin die bewusste erneute Zustandsprüfung vor einer neuen Bedienaktion.
Auch größere aktuelle Auswahlen werden dabei in 32er-Paketen gelesen; eine
unvollständige oder fehlgeschlagene Prüfung hebt keine unklare Bediensperre auf.
Historie wird nicht automatisch nachgeladen; deren bestehende Grenze bleibt
32 Entitäten je manuellem Verlaufsabruf.

## Funktionsumfang und Grenzen

- Geräteorientierte Auswahl, horizontale Werkzeugleiste und zusammengehörige
  Unterkacheln. Funktionen ohne Gerätezuordnung bleiben auswählbar.
- Neutrales Editor-UI, drei vorhandene Ausgabestile, veränderbare Kachelmaße,
  Mehrfachbindungen und die vorhandenen Designer-/Analysekacheln.
- Bereiche, Geräte, Entitäten, aktuelle Zustände und begrenzte historische
  Abfragen aus der laufenden HA-Instanz. Aktuelle Werte werden in der sichtbaren,
  verbundenen Ansicht automatisch und begrenzt abgefragt. Verdeckte/getrennte
  Ansichten werden nicht dauerhaft gepollt; Historie bleibt ein manueller Abruf.
  Es werden nur tatsächlich von HA gemeldete Werte angezeigt, keine errechneten
  Bewegungszwischenstände. Die Anzeige kann nicht häufiger neue Messwerte liefern
  als das Gerät und seine HA-Integration.
- Fehlende oder nicht verfügbare Zustände und leere Historien werden angezeigt;
  vorhandener Recorder-Verlauf wird weder erzeugt noch garantiert.
- Historische Einheiten bleiben an ihren Beobachtungen. Gemischte oder unbekannte
  Einheiten werden nicht still als gemeinsame numerische Reihe ausgegeben.
- Im Modus **Gestalten** werden keine Gerätebefehle ausgelöst. Im Bedienmodus
  bestimmen tatsächliche HA-Fähigkeiten, Services, Wertebereiche und aktuelle
  Verfügbarkeit die Bedienbarkeit. Nicht jede Entität eines Typs kann alles:
  - Jalousien/Rollläden: Öffnen, Schließen, Stoppen, Position und Lamellenneigung,
    jeweils nur bei gemeldeter Unterstützung.
  - Licht: Ein/Aus, Helligkeit und Farbtemperatur, sofern unterstützt.
  - Klima/Heizung: gemeldete Betriebsarten und unterstützte Zieltemperatur.
  - Ventilatoren: Ein/Aus, Geschwindigkeit und angebotene Voreinstellungen.
  - Zahlen- und Auswahlfunktionen: tatsächliche Grenzen, Schritte und Optionen.
  - Schalter/virtuelle Schalter: Ein/Aus. Sensoren bleiben Anzeigen.
  Fehlende Fähigkeiten werden erläutert statt durch funktionslose Knöpfe ersetzt.
- Zahlen- und Auswahleingaben senden nicht beim Verschieben oder Auswählen,
  sondern erst durch die zugehörige ausdrückliche Bedienaktion.
- Jede Aktion betrifft genau eine freigegebene Entität. Kein generischer
  Serviceproxy, keine automatische Wiederholung. Ein angenommener Befehl ist
  noch keine bestätigte Zustandsänderung; fehlende Bestätigung bleibt sichtbar.
- Schloss-, Alarm-, Script-, Szenen-, Update- und beliebige Serviceaktionen
  bleiben ausgeschlossen. Kein Speichern produktiver Dashboards in HA und keine KI.
- Position und Lamellenneigung sind getrennte Zustände. Ein HA-Zustand „offen“
  bedeutet nicht automatisch 100 Prozent Öffnung. Stoppen ist eine bewusste
  eigene Aktion; Netzwerkbedienung ersetzt keine physische Notabschaltung.
- Validierter nativer YAML-/JSON-Export für den unterstützten Funktionsumfang,
  aber keine vollständige Abdeckung aller freien Darstellungen. Berechnete
  Runtime-Kennzahlen sind semantisch noch nicht allgemein freigegeben.
- Das native Modell unterstützt ausdrückliche Browserspeicherung, Versionen und
  Backups; kein gemeinsamer serverseitiger Entwurfsspeicher. Freie Tab-Entwürfe
  sind dadurch nicht automatisch dauerhaft gespeichert.
- Native Installation, echter Ingress, Touch- und qualitative Designabnahme
  müssen am eigenen Zielsystem noch geprüft werden.

## Plattform und Nachweisgrenzen

Zielarchitekturen sind `amd64` und `aarch64`. Lokale Prüfungen verwenden
synthetische HA-Gegenstellen und keine echten Gerätebefehle. Sie ersetzen
keine Bestätigung der physischen Gerätewirkung am eigenen Zielsystem.
Die App bleibt ein Entwicklungsstand; native Ausgabe und physische
Touch-/Designabnahme sind davon getrennt.
