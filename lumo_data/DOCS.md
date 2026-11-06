# LUMO Data · 0.11.0-native.3 · Native HA-Dashboards

LUMO ist der Designer, nicht das fertige Dashboard. Dieser Entwicklungsstand hat
nur noch den nativen HA-Arbeitsablauf. Ausgabeprofil-Auswahl und aktiver freier
Editor entfallen. Vorhandene native Browserentwürfe und Backups bleiben lesbar;
nicht abbildbare Legacy-Inhalte werden erhalten und blockieren den Export,
statt still entfernt zu werden.

## Update und Einrichtung

Die bestehende **LUMO Data** aktualisieren, keine zweite App installieren.
Im bereits eingebundenen Repository nach Updates suchen, die App aktualisieren
und die Weboberfläche neu öffnen. Slug `lumo_data`, Optionen, Schema und
Berechtigungen bleiben erhalten. Die separate ältere `lumo_preview` bleibt unverändert.
Repositoryveröffentlichung allein installiert, startet und schaltet nichts.

Die vorhandenen vier Konfigurationsfelder gelten weiter:

- `enabled`: bewusst aktivieren; deaktiviert bleiben Daten, Bedienung und Dashboardanlage gesperrt.
- `allowed_user_ids`: eigene HA-Benutzer-ID, nicht Anzeigename. Nur freigegebene Benutzer erhalten Zugriff.
- `allowed_entity_patterns`: optionale Eingrenzung. Leer erlaubt alle nicht ausgeschlossenen Entitäten.
- `denied_entity_patterns`: explizite Ausschlüsse haben Vorrang.

Nach erkannter Optionsänderung ist ein App-Neustart nötig. Die Sicherheitsgrenze
bleibt gesperrt, auch wenn die ursprünglichen Optionen danach wieder eingetragen
werden. Keine HA-Tokens in Browserfelder eintragen; Zugriff erfolgt intern über
Supervisor und vertrauenswürdigen Ingress. Direkter Portzugriff ist nicht vorgesehen.
Zum Anlegen von Dashboards muss der anfragende Benutzer zusätzlich aktuell aktiver
HA-Administrator oder Besitzer sein. Das wird unabhängig vom App-Token geprüft.

## Der Ablauf

1. **Dashboard:** neuen Entwurf beginnen oder vorhandenen Browserentwurf öffnen.
   **HA-Dashboards laden** liest ausdrücklich unterstützte HA-Dashboards;
   **Als lokale Kopie öffnen** verändert das Original nicht.
   Bestehende Entwürfe, unterstützte HA-Kopien und Backups öffnen direkt in **Dein Raumentwurf**.
2. **Raum:** Bestand laden und vorhandenen Raum wählen oder eine neue Raumansicht
   im Entwurf anlegen. Kein echter HA-Bereich wird angelegt.
3. **Design & Display:** Zielanzeige und optional CSS-Maße festlegen. Physische
   Diagonale, Auflösung, DPR und Kiosk sind Kontextangaben, keine Geräteemulation.
   Frühere Stilpräferenzen bleiben speicherbar; sie installieren/exportieren kein HA-Theme.
4. **Dein Raumentwurf:** Quellen nach Geräte-/Funktionsnamen suchen, hinzufügen,
   Darstellung bearbeiten, gruppieren, mit Maus oder Touch verschieben/vergrößern.
   Fixierungen und Rückgängig/Wiederholen bleiben verfügbar. Zurückgehen erhält den Entwurf.

Exakte Entitäts-IDs, Quellenqualität und Herkunft bleiben in Details sichtbar.
Neue Quellen beginnen als Wertanzeige; eine unterstützte native Bedien-Darstellung
wird ausdrücklich im Editor gewählt. Für Karten sind 13 MDI-Symbole lokal gebündelt;
unbekannte Symbole haben einen neutralen Ersatz. Das ist nicht der vollständige
HA-Iconkatalog. Die separate Seitenleistensymbol-Auswahl verwendet HA-Komponenten.

## Eine andere Entität auswählen

Kachel bearbeiten öffnet die Quellenauswahl mit **Suche**, **Raum** und **Typ / Domain**.
Voreingestellt ist die tatsächliche Raum-ID der aktiven Ansicht, nicht nur ein
gleichlautender Raumname. **Alle Räume** und **Ohne Raumzuordnung** sind ausdrücklich
wählbar. Weitere Ergebnisse stehen auf Folgeseiten; der Bestand wird nicht nach
den ersten 40 Quellen abgeschnitten. Geräte-/Funktionsnamen stehen im Vordergrund,
die genaue ID und Datenqualität bleiben aufklappbar.

**Ersetzen** tauscht die gesamte Auswahl. **Hinzufügen** ergänzt bei Verlaufskarten
bis zu acht Quellen; **Entfernen** und **Auswahl leeren** ändern zunächst nur die
offene Bearbeitung. Erst **Übernehmen** ändert den Entwurf; **Abbrechen** verwirft
die Bearbeitung. Filtern und laufende Wertaktualisierung löschen keine Auswahl.
Ein reiner Quellenwechsel erhält eigene Namen, Symbole, Optionen und Kartengrößen.
Passende Darstellungen werden aus tatsächlich gelesenen Fähigkeiten vorgeschlagen,
nicht automatisch umgestellt. Noch nicht gelesene Fähigkeiten bleiben unbestätigt.

## Layouttreue statt freier Pixelpositionen

Raumentwurf und Export verwenden dieselben nativen Sections-Regeln: zwölf Spalten
je Abschnitt, Kartenspannen, Abschnittsreihenfolge, native Abstände und responsive
Anordnung. `Maximale Abschnitte nebeneinander` zählt Abschnitte, nicht Kartenspalten.
Gruppen werden zu eigenen Abschnitten; aufeinanderfolgende direkte Bausteine teilen
einen Abschnitt. Das sichtbare Raster markiert diese tatsächlichen Abschnittsgrenzen,
nicht eine frei belegbare Fläche bis zum Fensterrand.

**Links / Mitte / Rechts** oder **Startspalte → Platzieren** richten eine einzelne
Inhaltskachel innerhalb ihrer 12-Spalten-Section aus. Auch horizontales Ziehen am
Griff verändert bei genau einer Inhaltskachel die Rasterposition. Breite/Höhe bleiben
erhalten. Vorhandene unfixierte Abstände in diesem Abschnitt werden dabei bewusst
ersetzt; fixierte Elemente sperren die Aktion. Bei ungerader freier Spaltenzahl
rastet Mitte links der mathematisch exakten Mitte ein, wie im Werkzeug angegeben.
Für mehrere Inhaltskacheln bleiben Reihenfolge, eigene Gruppen und explizite
Abstände verfügbar; eine Ausrichtungsaktion verschiebt nicht still die Nachbarn.

**＋ Abstand** ergänzt eine echte Layoutzelle. Über **Layoutauswahl → Abstand
bearbeiten** lassen sich Spalten, Zeilen, Gruppe, Reihenfolge und Fixierung ändern
oder der Abstand entfernen. Breitere Zellen bieten zusätzlich Maus-/Touch-Griffe;
schmale Zellen verwenden die gut erreichbaren äußeren Werkzeuge. Rückgängig,
Wiederholen, Speichern und Backups erhalten diese Angaben.

**Wichtige native Grenze:** Die Ausgabe verwendet leere native Grid-Container,
keine Geräte, erfundenen Entitäten oder Custom Cards. Im normalen HA-Dashboard
reservieren sie nur Leerraum. Öffnet man einen solchen Container später einzeln
im **HA-Karteneditor**, zeigt HA **Empty card** an. LUMO weist vor Export/Anlage
darauf hin. Maximal 256 Layoutzellen sind zusätzlich zu 128 Inhaltskacheln möglich.

**Gruppen im Entwurf** zeigt neue leere Gruppen sofort mit Namen und Werkzeugen.
Eine Kachel am Griff hineinziehen, einen vorhandenen Inhalt **Zuweisen** oder
**Quellen für …** wählen. Umbenennen, Fixieren, Entfernen und Reihenfolge bleiben
dort auch für gefüllte Gruppen erreichbar, ohne Kacheln zu verdecken. Leere Gruppen
belegen nur diesen Entwurfsbereich, keine unsichtbare Section im HA-Ergebnis.
Deshalb erhält der Browserentwurf sie, der native Export/erneute native Import nicht.

Der native Vergleich verwendet ein tatsächlich im UI erstelltes, heruntergeladenes
Dashboard mit neun Karten, zwei Überschriften und vier Abschnitten bei identischen
Inhaltsbreiten 390/768/1024/1440. Referenz: offizielles HA-Frontend
`DEMO-20261028.4`, Commit `a67b691a451e0b3fc469679b07158f963a61842c`.
Zusätzlich wurden aus dem aktuellen UI exportierte linke/rechte Einzelkacheln
und eine mittig ausgerichtete gruppierte Kachel samt direkten Inhalten und leerer
Entwurfsgruppe bei diesen vier Breiten gegen den echten nativen Renderer geprüft.
Dies ist eine abgegrenzte Geometrieprüfung, keine Zusage für sämtliche installierten
HA-Versionen oder eigene Themes. Ein anderer nutzbarer Inhaltsbereich ordnet Sections
entsprechend neu. Identische Schrift-, Icon- und Controlgestaltung ist nicht zugesagt.

Die neutrale native Entwurfsdarstellung ist kein installiertes Noir-/Ivory-/Clean-Theme.
Gespeicherte frühere Stilpräferenzen werden nicht in native HA-Themes übersetzt.
Verlaufskarten beziehen Historie im fertigen HA-Dashboard aus HA/Recorder;
im Raumentwurf werden keine erfundenen historischen Diagramme angezeigt.

## Entwurfsmodus und Testmodus

Der Modusschalter steht unmittelbar vor dem Status des Raumentwurfs.
Start, Laden, Navigation, Trennen und Verbergen der Seite kehren sicher in den
Entwurfsmodus zurück. Dort werden keine Gerätebefehle gesendet. Ein dezentes Raster
ist im Designmodus sichtbar, im Testmodus ausgeblendet. Testmodus sperrt die
Bearbeitung; Kachelpositionen, Größen und gespeicherte Bindungen bleiben unverändert.
Werte und Bedienung befinden sich in den jeweiligen Kacheln, nicht in einer zweiten
Bedienliste unter dem Entwurf. Die lokalen Karten-Abbildungen sind weiterhin nicht
die offiziellen interaktiven HA-Karten.

Gewählte native Bedien-Darstellungen zeigen ihre Hauptfunktionen direkt, zum Beispiel
Öffnen/Stopp/Schließen oder Helligkeit. Über **⋯**, bei Ein/Aus-Kacheln über den
Kacheltitel, öffnet sich innerhalb derselben Kachel die Auswahl weiterer unterstützter
Funktionen und der Quellen-/Befehlsstatus. Kleine manuell dimensionierte Kacheln
scrollen hierfür innen; ihre gespeicherte Größe wird nicht eigenmächtig geändert.
**←** oder Escape schließt diese Ansicht. Neue reine Wertanzeigen behalten ihre
Darstellung; für ständig sichtbare Hauptbedienelemente die passende Darstellung
im Editor auswählen. Zusätzliche Quellenfunktionen im Test werden nicht automatisch
in den Export übernommen: Dieser enthält unverändert die gewählte native Darstellung.

Im verbundenen Einstieg können Testaktionen echte Geräte bedienen. Es werden nur
nachgewiesene aktuelle Fähigkeiten, Services, Wertebereiche und Optionen angeboten.
Sensoren bleiben Anzeigen; nicht gebundene Entitäten sind nicht bedienbar.
Zahlen-/Auswahländerungen allein senden nicht: die zugehörige ausdrückliche Aktion
bzw. **Senden** ist nötig. Unklare Ergebnisse bleiben unklar; kein automatischer Retry.
Stoppen ist eine bewusste eigene Aktion, keine garantierte physische Notabschaltung.
Schloss-, Alarm-, Script-, Szenen-, Update- und beliebige Serviceaktionen bleiben ausgeschlossen.
Offline wird kein Gerät geschaltet und keine erfolgreiche echte Bedienung vorgetäuscht.

## Speichern, Exportieren, Anlegen

**Dashboard speichern** sichert in localStorage dieses Browsers/Ursprungs.
Das ist kein gemeinsamer HA-Entwurfsspeicher. Browserdaten löschen kann Entwürfe
verlieren. Unter weiteren Werkzeugen Backups und Versionen verwenden.
Backups/Exporte enthalten private Entitätskennungen und Namen, keine Zugangsdaten.

**Dashboard exportieren** prüft und lädt native YAML-/JSON-Konfiguration herunter.
Fehler blockieren vollständig; Warnungen prüfen. Native Ausgabe benötigt danach
keinen laufenden LUMO- oder KI-Backenddienst. HA liefert Zustände, Dienste und Historie.
Nicht jeder Analyse-, Formel-, Cockpit- oder Custom-Card-Inhalt ist nativ abgebildet.

**Dashboard anlegen** öffnet einen Dialog neben Exportieren:

- **Titel:** vorbelegt aus dem aktuellen Dashboard, vor dem Anlegen änderbar.
- **Seitenleistensymbol:** originale HA-Symbolauswahl; zulässig sind MDI-Symbole.
- **URL-Name:** Leerzeichen/Sonderzeichen werden durch Bindestriche ersetzt.
  HA verlangt mindestens einen Bindestrich; ein einzelnes Wort erhält `dashboard-`.
  Der endgültige Name bleibt sichtbar und überprüfbar.
- **Nur Administratoren:** ausdrücklich Ja/Nein; sichere Voreinstellung Ja.
- **In der Seitenleiste anzeigen:** ausdrücklich Ja/Nein; Voreinstellung Ja.

Erst **Jetzt in Home Assistant anlegen** sendet den Auftrag. Öffnen, Abbrechen,
Speichern, Exportieren und Moduswechsel legen kein HA-Dashboard an.
Titel, Symbol, URL und beide Schalter werden ausdrücklich übertragen. Nur ein neues
Storage-Dashboard wird angelegt. Erkannte bestehende URL-Pfade werden abgewiesen;
kein Update-, Lösch- oder automatischer Wiederholungsweg ist enthalten.
Die App liest Metadaten, neue Dashboard-ID und komplette Konfiguration zurück,
bevor sie Erfolg meldet.

Bei fehlender nativer HA-Symbolauswahl bleibt Anlegen gesperrt. Die Meldung nennt
den erforderlichen HA-Kontext; eine synthetische Ersatzliste wird nicht als HA-Picker
angeboten. Tatsächliche Kompatibilität der installierten HA-Oberfläche bleibt zu prüfen.

**Teilweise/unklare Ergebnisse:** HA legt Dashboard und Inhalt in getrennten Schritten
an. Nach einem Verbindungsabbruch kann ein leeres oder bereits gefülltes Dashboard
vorhanden sein. Zielpfad in HA prüfen, nicht blind erneut versuchen. LUMO löscht nicht
automatisch. Die HA-Speicherschnittstelle bietet keinen atomaren Versionsvergleich;
das neue Ziel während des Anlegens nicht parallel in HA bearbeiten, löschen oder
ersetzen. Prüfungen erkennen bekannte Konflikte, garantieren aber keine atomare
Transaktion gegenüber gleichzeitigen externen Schreibern.

## Daten, Import und Nachweisgrenzen

Bestand und aktuelle Werte kommen zur Laufzeit aus der bestehenden HA-Verbindung,
nicht aus eingebetteten Hausdaten. Fehlende, unbekannte, ungültige, nicht verfügbare
und veraltete Werte bleiben unterscheidbar. Begrenztes Polling liest die aktive
sichtbare Ansicht in Paketen bis 32 unterschiedlichen IDs; Trennen/Verbergen pausiert.
Es werden keine Bewegungszwischenwerte erfunden. Historie bleibt ausdrücklich und begrenzt.

Der HA-Import ist konservativ: vollständig unterstützte native Sections als lokale
Kopie. Custom Cards, unbekannte Aktionen/Styles und nicht abbildbare automatische
Größen werden vollständig abgelehnt, nicht still weggelassen. Admin-only-Dashboards
werden über den bestehenden Nur-Lese-Import nicht angeboten. Dashboardanlage hebt
diese Importgrenze nicht auf. Zum erneuten Bearbeiten den Browserentwurf aufbewahren.

Tests verwenden synthetische HA-Gegenstellen und offizielle Frontend-Referenzen,
keine produktiven Hausbefehle. Zielarchitekturen: amd64/aarch64. Installation,
physischer Touch, tatsächliche Gerätewirkung und qualitative Designabnahme bleiben
separate Prüfungen am eigenen Zielsystem. Es gibt keine automatische Endabnahme.
