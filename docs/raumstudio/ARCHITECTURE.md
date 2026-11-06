# Raumstudio 0.12.1 – Architektur und Betriebsvertrag

## Abgrenzung und Wiederverwendung

Update ausschließlich in `lumo_raumstudio/`; eingefrorene 0.12.0-Basis LUMO-HA `c1ffa3434d95a59f0538573173d8138927388811`. Kein Lesen oder Migrieren von `lumo_preview`, keine Änderung an bestehenden Apps. Die aktuelle Freigabe ersetzt historische Entwicklungsstopps ausschließlich für Dashboardverwaltung und die verlustfreie Importkorrektur in Schritt 1. Keine Ausweitung auf Schritte 2–4.

Geprüfte Wiederverwendung aus `/workspace/lumo-core-usability-update/ha_app/lumo_data`:

- `client.py`: bounded RFC6455 `Wire`, duplicate-key/NaN-verweigernder JSON-Parser, authentifizierter WS-Handshake und Ergebnisvalidierung. **Nicht übernommen:** HTTP-Transport, Services, Controls, Dashboard-Create/Save oder deren Methoden. Der neue Client hat keinen solchen Codepfad.
- `policy.py`: sichere komponentenweise NOFOLLOW-Optionsdatei und unveränderlicher Optionssnapshot mit latched denial; auf `enabled` und `allowed_user_ids` angepasst.
- `bootstrap.py`: irreversible UID/GID65532-Abgabe, Gruppen-/Capability-/NoNewPrivs-Prüfung; eigenes nicht rekursiv repariertes Datenverzeichnis ergänzt.
- Server-Sicherheitsmuster: begrenzte Header, Fristwächter, ein begrenzter synchroner HTTP-Worker, quiet errors, feste Routen und Ingress-/Origin-Grenze.
- Import: native vorhandene Karten-/Ansichtsdaten bewahren statt einen neuen Raum-/Kacheleditor zu erfinden. Importierbarkeit ist jetzt sichere, endliche, begrenzte JSON-Datenhaltung. Die unterstützte Bearbeitungsgrammatik ist davon unabhängig; Unbekanntes bleibt geschützt.
- Originales `assets/lumo-logo-v1.png`, SHA256 `702cb856a72674a7f2f9214d6a9da788b87b3651208e0abeba4e8afac07fecd0`. Keine nachgezeichnete Marke.

Das alte `DashboardDocument` verlangt 1–16 Ansichten und dessen Store ist browserlokal. Es wird weder heimlich angepasst noch durch Dummyansichten vorgetäuscht. Die Management-Hülle besitzt **0 oder mehr vorhandene Ansichtsbezüge innerhalb des JSON-Limits**, Owner, stabile ID, Created/Updated, Entwurfsstatus, Datenformat1 und CAS-Revision. `native` enthält eine unabhängige geprüfte vollständige Konfiguration oder null. `views[]` enthält nur Verwaltungsbezüge `{id,title,icon,nativeIndex,backgroundOverride}`; keine neue Raum-/Kachelfunktion. Vorhandene native Inhalte bleiben bei Metadatenänderungen bytewertgleich als JSON-Daten erhalten.

## Persistenz und Revision

SQLite unter `/data/raumstudio/studio.sqlite`, Synchronous FULL, abgeschlossene Verbindungen, kein WAL-Betrieb. Tabellen `dashboards(id,owner,revision,document)` und `images(id,owner,metadata,bytes)`. Sämtliche Eigentumsabfragen enthalten Owner+ID; ausschließlich gebundene SQL-Parameter. JSON trägt `schemaVersion:1`, die DB aktuell `PRAGMA user_version=2`.

Änderungen/Duplikate/Löschen beginnen mit `BEGIN IMMEDIATE`; erwartete Revision wird innerhalb derselben Transaktion geprüft. Konflikt liefert 409. Umbenennen behält ID und Erstellzeit, Duplikate besitzen neue IDs und eigenen JSON-Inhalt. Immutable Bilder dürfen referenziert werden; keine Bildbytes-Update-Route. Bildentfernen ändert nur die Dashboardreferenz. Eigener Upload wird vollständig mit Pillow dekodiert, EXIF-Orientierung normalisiert, in RGBA-PNG ohne zusätzliche Metadaten umkodiert und mit Pixel-/Bytecaps geprüft.

Die UI bestätigt Speicherung erst nach separatem GET desselben Entwurfs und exaktem JSON-Vergleich. Bei Unterbrechung oder uneindeutiger Antwort wird kein automatischer Schreibretry ausgelöst. Auswahl-ID darf in SessionStorage stehen; Entwürfe/Bilder/Eingaben werden nicht als geräteübergreifende Speicherung im Browser ausgegeben.

## Reviewkorrekturen R1–R7

- Listen- und Verwaltungsaktionen halten Ziel-ID und erwartete Revision vor dem Dirty-Guard fest. Nur dessen eigener bestätigter Save desselben Ziels **und derselben Ausgangsrevision** darf die Revision ersetzen; kein Fetch-latest um fremde 409-Konflikte zu übergehen. Eine parallel gespeicherte Neuanlage ändert das Aktionsziel nicht.
- Lokaler vollständiger MDI-SVG-Katalog **7.4.47**, 7447 Namen aus `Templarian/MaterialDesign-SVG` Commit `9e04201d4557e729822fb57f62a316c3dea1d4a8`. `mdi.json` enthält ausschließlich unveränderte Pfaddaten, keine ausführbare SVG-Quelle; Darstellung per festem SVG/viewBox und `createElementNS`. Gleiches JSON ist serverseitige Namens-Allowlist und Clientkatalog. Suchbare bebilderte Auswahl, keine Unicode-Ersatzsymbole für gewählte Icons. Unbekannte Namen/neuere Versionen/Aliasse werden bei Verwaltung und gezielter Symbolbearbeitung ehrlich abgelehnt; im importierten Original bleiben sie unangetastet. Leeres Verwaltungsicon bleibt optional. Lizenztexte und sämtliche Ursprungshashes in `mdi-LICENSE`, `mdi-APACHE-2.0.txt`, `mdi-provenance.json`. MDI-JSON-SHA256: `3f719999c5f613801f790283b86056e723c6fa1667dcf033371499727decd858`. Nur zusätzlicher ingressgeschützter statischer Assetpfad, keine öffentliche Route, kein externes Iconladen, unveränderte CSP.
- Kanonischer API-Versionswert rechts im Header, Original-Logo unverändert.
- Settings verwenden `novalidate` ausschließlich für die explizite vollständige HTML-Validity-Prüfung: ersten ungültigen Control ermitteln, zugehörigen Tab öffnen, fokussieren und `reportValidity()` ausführen. Servervalidierung unverändert aktiv.
- Erfolgreicher Upload/Delete-POST mit fehlgeschlagenem Bestätigungs-GET sperrt alle weiteren Writes im Tab, hält Ziel-ID und Eingaben und fordert bewusste Prüfung in einem neuen Tab. Kein Wiederholungs-/Freigabeautomatismus.
- Historische 0.12.0-Grammatik und ihre rekursiven Typregressionen bleiben für Legacy-Datenprüfung erhalten. Neue Importe prüfen stattdessen ausschließlich JSON-Sicherheit. Unbekannte Symbole, Badges, Feldtypen und Actions bleiben inerte Daten, keine Importblocker.

Nicht Bestandteil dieser Korrektur: N1-Gesamtabrufbudget, Speicherarchitektur oder zusätzliche Produktfunktionen.

## Sicherheit

- Laufzeit-Listener 8099 nur im App-Netz, keine `ports`, kein Hostnetz. Unmittelbarer Peer ausschließlich `172.30.32.2`; zusätzlich Loopback für den nicht privaten Healthcheck. API/Assets erfordern genau einen gültigen `X-Remote-User-Id`. Forwarded-For beweist keine Identität.
- Der Python-Konstruktor akzeptiert einen Test-Peer und eine Test-HA-Adresse. **Keine** solche Option, Umgebungsvariable oder HTTP-Route im Produktionsstart.
- Supervisor-Token vor Privilegabgabe aus der offiziellen Umgebung nehmen; niemals Browsertransport. Fehlender Token erlaubt lokale Verwaltung, HA-Lesen bleibt nicht verfügbar.
- Herkunftsprüfung, Sec-Fetch-Site, `X-LUMO-Read`, bei Writes Origin + `X-LUMO-Action` + ownergebundener HMAC-CSRF-Token. Token stirbt beim Neustart. Keine CORS-Freigabe.
- Optionsdatei vor Privilegabgabe sicher lesen. Eigenes `/data/raumstudio` mit NOFOLLOW öffnen und ausschließlich bei Neuanlage auf65532 setzen; vorhandene falsche Eigentümer/Modi, Symlinks, Hardlinks und fremde Unterverzeichnisse verursachen sicheren Startabbruch. Keine rekursiven Chowns und kein fremder Datenzugriff.
- Nur feste WS-Kommandos: `config/auth/list`, `lovelace/dashboards/list`, `lovelace/config`, `lovelace/resources/list`. Aktiver Owner oder `system-admin` der **angeforderten Ingress-HA-ID**, nicht des Connector-Users, ist Voraussetzung für jeden Import/Liste-Abruf. Das ist eine bewusst admin-only Anfangsgrenze für die HA-Entityrechte. Lokale Entwürfe anderer erlaubter Benutzer bleiben unabhängig nutzbar.
- Importierte Karten sind inert: niemals HTML/JS oder aktive native Karten im Editor. CSP begrenzt Ressourcen auf self/data/blob, kein beliebiges CSS/URL-Feld. Fehlermeldungen enthalten keine Tokens, Rohtransportfehler oder private Requestlogs.

## Verlustfreier Import- und Exportvertrag 0.12.1

`native` ist die serverseitig gehaltene Originalkonfiguration. Neue Imports besitzen zusätzlich `nativeImport = {version:1, sourcePath, capturedAt, resources, edits}`. Management-Einstellungen bleiben strikt getrennt. Die SQLite-Tabellen/DB-Version2 und äußere `schemaVersion:1` bleiben unverändert; der Marker trennt den neuen Vertrag von bestehenden Legacy-Hüllen. Alte Dateien werden beim Lesen/Update nicht migriert. 0.12.0 kann die erweiterte Hülle nicht lesen: Rollback nur mit passender vollständiger Sicherung.

`imported.py` validiert Bearbeitbarkeit unabhängig von Datenübernahme. Nur vorhandene skalare Textfelder an bekannten nativen Positionen sind erlaubt: Root-Titel, Titel/Icon bekannter Ansichten sowie ausdrücklich definierte Felder bekannter Karten. Rekursion ausschließlich über bekannte `views/cards/sections`-Strukturen und bekannte Grid/Stack-Container; niemals durch unbekannte Custom-Card-/Template-/Style-Daten. Kein generisches JSON-Patch, Deep-Merge, Delete, Insert, Move oder Array-Reordering. Pfadsegmente sind exakt Strings bzw. echte Ganzzahlen (keine Booleans, keine numerischen Strings). Eine Änderung enthält `path` als Segmentliste und `value` als Text. Maximal 32 Änderungen pro Transaktion und 1000 verschiedene gespeicherte Pfade. Originalwerte werden nicht getrimmt. Alle nicht adressierten Daten bleiben unverändert; Transaktionen sind atomar.

Neue HTTP-Routen sind owner-/Ingress-/Origin-geschützt:

| Route | Vertrag |
|---|---|
| `POST /api/ha/import` | Unverändert `{path,name}`. Adminprüfung, echte Config-Lesung, separate feste Ressourcenlesung, unabhängiger lokaler Import. Keine vom Browser vorgelegte Originalkonfiguration. |
| `GET /api/dashboards/<id>/report` | Aktuelle Revision, verständliche Zusammenfassung, erlaubte Felder samt exakten Pfaden, geschützte Pfadbeispiele, Quellen-/Exporthashes, Abhängigkeiten und getrennte Ressourcen-Momentaufnahme. Nur neue Importhüllen. |
| `POST /api/dashboards/<id>/native-edit` | `{revision,edits:[{path:["views",0,"cards",0,"name"],value:"Neuer Name"}]}`. CAS409, fremder Owner404, CSRF/Origin403, geschützter/ungültiger Pfad422. Gesamten Batch prüfen, dann Ledger aktualisieren. Kein Source-Overwrite. |
| `GET /api/dashboards/<id>/export` | Aktuell gespeicherte native JSON-Konfiguration als Attachment mit ID/Revision im Dateinamen. Nur neue Importhüllen. Authentifizierter Fetch mit `X-LUMO-Read:1`; UI lädt rohe Bytes als Blob. Kein Parse/Stringify großer Zahlen im Downloadpfad. |

`POST .../save` bleibt geschlossen auf `name/icon/description/settings`; `native`, `nativeImport` und `views` sind nicht schreibbar. Die öffentliche Import-Exportfunktion ignoriert Settings vollständig: keine Standardtitel, Hintergründe, hinzugefügten Pfade, `show_icon_and_title` oder Umsortierungen. UI markiert diese Settings als reine Verwaltung/lokale Vorschau; native Änderungen gibt es nur im importbezogenen Feldeditor in Schritt 1. Dirty-Guard, Busy-Sperre, verlorene Bestätigungslesung und CAS bleiben wirksam. Export enthält den aktuellen gespeicherten Stand, niemals ungespeicherte Formulare.

Original und Ressourcen bleiben getrennt. `resources={status:"captured",items:[...],verification:"unverified",message:...}` bewahrt die gelesene Registryliste exakt. Bei Lesefehler/Limit: `status:"unavailable",items:null`, keine fälschlich erfolgreiche leere Liste. Nur der feste Lesebefehl `lovelace/resources/list`; keine Legacy-Fallback-Probe, keine Ressourcen-URL-Aufrufe, kein Fetch/HEAD und keine Installation. Registrierung ist kein Funktionsnachweis. Abhängigkeitssuche nennt erkannte Custom-Typen, Template-/Style-Präsenz, Themes und URL-/Dateireferenzen ohne vollständige semantische Zuordnung zu versprechen.

Finite JSON-Sicherheit: Root-Objekt, endliche Zahlen, 64 Ebenen, 100.000 Werte, 1 MiB ASCII-JSON. Doppelte Schlüssel und NaN werden schon vom Parser abgewiesen. Opaque Schlüssel wie `__proto__`, `constructor`, `prototype` bleiben erlaubt; der Browser führt niemals Merge/Assignment importierter Objekte durch. Daten gelangen nur in `textContent`, feste Select-Optionen und unveränderte Downloadbytes, nie in `innerHTML`, CSS, `eval` oder dynamische Scripts. JSON-ASCII-Transport bewahrt auch escaped Unicode-Codeunits. Technische Detailbeispiele/Referenzen sind auf je 200, UI-Elementauswahl auf 1000 begrenzt; überlange unbekannte Schlüssel werden ausschließlich in Diagnosepfaden auf 160 Zeichen plus Auslassungszeichen gekürzt (`pathTruncated`), die vollständigen Quelldaten bleiben ungekürzt.

Legacy-Hüllen ohne `nativeImport` behalten bei Start und Backup/Restore die Größenregel aus 0.12.0: höchstens 1 MiB UTF-8 der JSON-Serialisierung ohne ASCII-Escaping sowie die konservative unterstützte Grammatik. Unicode wird dafür weder normalisiert noch gekürzt; gespeicherte Dokumentbytes bleiben unverändert. Neue Importe einschließlich ihrer erneuten Datenbankprüfung, Ressourcen und Editmaterialisierung bleiben dagegen auf 1 MiB ASCII-JSON begrenzt. Die gemeinsame Prüfung endlicher Werte, Tiefe und Wertezahl wird nicht gelockert. `test_legacy_unicode.py` erzeugt hierfür eine echte Datenbank mit dem Store aus einem isolierten lokalen `git archive` des Pins `c1ffa3434d95a59f0538573173d8138927388811` (Git und dieser Commit müssen für den Test verfügbar sein).

Backup/Restore prüft Original, Importmarker, Ressourcenliste und jedes gespeicherte Edit erneut gegen die serverseitige Allowlist. Duplizieren kopiert Source/Ledger/Registry unabhängig; Nameänderung/Settings ändern den nativen Titel oder Export nicht. Neue Module sind explizit im Dockerfile enthalten; keine neuen Pakete oder HA-Rechte.

## Historische native Hintergrund- und Navigationsabbildung

`native.py` hat zwei explizite Zweige: Neue verlustfreie Importe werden ausschließlich aus Original plus autorisierten Feldänderungen exportiert. Die folgende interne Hintergrundabbildung bleibt nur für unveränderte Legacy-Hüllen ohne `nativeImport` erhalten. Sie wird nicht auf neue Importe angewandt und ist kein öffentlicher Legacy-Export. Es gibt weiterhin kein HA-Schreiben.

Aus ausschließlich validierten Einstellungen wird ein CSS-Background-String erzeugt. Bildbytes sind eigenständig `data:image/png;base64,…`; gewünschte Deckkraft wird in den PNG-Alphakanal gerechnet. Damit funktionieren **0 %** trotz der Truthiness-Grenze des nativen Background-Objektfelds und freie %-Skalierung trotz dessen beschränktem `size`-Typ. Farbe bleibt eine echte separate Grundfarbe. Positionen, cover/contain/auto, `% auto`, no-repeat und fixed/scroll sind generiert, kein freier CSS-Text. Spätere native Ausgabe benötigt damit weder Ingressassetlinks noch laufendes LUMO.

Priorität: zukünftiges validiertes `backgroundOverride` der Ansicht → vorhandener nativer Ansichtshintergrund → globaler Hintergrund. Aktuell gibt es keinen UI-Editor für View-Overrides. Globale Änderungen überschreiben vorhandene native View-Farben nicht. Vorschau kennzeichnet diesen Fall.

`show_icon_and_title` wird auf vorhandene Ansichten abgebildet; Startansicht wird vorangestellt, zuvor fehlende native Pfade bekommen ihren ursprünglichen Index als stabilen Pfad. Sidebar-/require_admin-Werte sind klar bezeichnete Ausgabeabsichten außerhalb der Lovelace-Konfiguration, derzeit ohne HA-Wirkung. `visible` verbirgt Tabs, ist kein Zugriffsschutz.

**Runtime-Gate:** `test_native_runtime.py` lädt unveränderte original gespeicherte offizielle Frontendassets `DEMO-20261028.4`, korrespondierender Frontend-Quellpin `a67b691a451e0b3fc469679b07158f963a61842c`. Realer `hui-root` samt `hui-view-background`, nur selbst gebautes synthetisches hass, keine echte Auth-/Hausstruktur. Native CSS/Pixelprüfungen für cover, contain, 137 %/0 %/fixed und 75 %/fixed sowie wirkliche Root-Viewpriorität; alle Netzabrufe ausschließlich aus SHA-geprüftem Assetcache, alle WebSockets blockiert. Das ist mehr als ein Sourceassert oder nachgebautes CSS, aber keine Installation auf Andys HA.

## Sicherung / Migration / Rückkehr

Normale HA-Sicherung: `backup: cold`, vollständiges privates `/data`, zuvor App stoppen lassen. Update auf denselben Datenträger, keine Migration anderer Apps.

`maintenance.py` arbeitet nur offline und hat keine Webroute. `backup(source,destination)` verwendet SQLite Backup API, prüft Integrität, Tabellen, vollständige Hülle, Verweise und Bilddecoder; Ziel exklusiv neu, fsync. `restore` validiert zuerst, erzeugt eine geprüfte temporäre Datei im Zielordner und ersetzt erst danach atomar, einschließlich Verzeichnis-fsync. Vorhandene Journale/WAL verweigern Restore. Fremde/nicht unterstützte Schemata werden nicht ersetzt.

Reale vorbereitete Migration 1→2 fügt den Owner-Index hinzu. Vor **jeder** solchen Migration wird `studio.sqlite.pre-v1-<UUID>.sqlite` erzeugt. Exklusive Transaktion; Fehler führt nach Rollback zu atomarer validierter Wiederherstellung der Schema1-Sicherung. Für einen Versionsrollback muss diese passende Sicherung zusammen mit einer passenden App-Version zurückgespielt werden. Keine Downmigration durch blindes Herabsetzen einer Versionsnummer. Tests verwenden dieses Herabsetzen nur zur kontrollierten Herstellung einer synthetischen Schema1-Vorlage mit passender Tabelle/fehlendem Index.

Entwicklerbefehle bei **gestoppter** App und passendem Dateieigentümer (normaler Nutzerweg bleibt HA-Backup/Restore):

```sh
python maintenance.py inspect /data/raumstudio/studio.sqlite
python maintenance.py backup /data/raumstudio/studio.sqlite /data/raumstudio/manuelle-sicherung.sqlite
python maintenance.py restore /data/raumstudio/manuelle-sicherung.sqlite /data/raumstudio/studio.sqlite
```

Sicherung ist keine Verschlüsselung; eine vollständige Sicherung enthält alle Nutzerbereiche und muss wie die HA-Sicherung geschützt werden.

## Abhängigkeiten und Nachweisgrenzen

`config.json` ist kanonischer Versionswert. Dockerlabels verwenden Supervisor-Buildargs `BUILD_VERSION` / `BUILD_ARCH`. Baseimage: `python:3.13-alpine@sha256:7984cf56ceaddebe4fefeb75d64000b9f45d8b77b11a09b24524da6cdc3af0c8`. Pillow12.3.0, ausschließlich hashgeprüfte CPython3.13-musllinux-Wheels für amd64/aarch64; kein zur Laufzeit nachinstalliertes Paket. Pi-/Host-Images prüft der Parent unabhängig, lokale Tests allein beweisen keine Architektur-Runtime.

Offizielle Quellen: `contributors.home-assistant.io/apps/reference/configuration/`, `/apps/guides/ingress/`, `www.home-assistant.io/dashboards/views/`. HTML-Abrufe waren hier teilweise blockiert; erneut gelesene offizielle GitHub-Dokumentationsquellen (`home-assistant/developers.home-assistant/docs/apps/{configuration,security,communication,presentation}.md`), Supervisor-Ingressquelle und gepinnte Frontend-Dateien sind separat im Evidence-Ordner gesichert. Keine Behauptung, dass blockierte HTML-Seiten erfolgreich erneut geladen wurden.
