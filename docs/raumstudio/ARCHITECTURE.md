# Auftrag 01 – Architektur und Betriebsvertrag

## Abgrenzung und Wiederverwendung

Neue App ausschließlich in `lumo_raumstudio/`; Basischeckout LUMO-HA `f3970611dfd09191975825a75d7f9639745b0bec`. Kein Lesen oder Migrieren von `lumo_preview`, keine Änderung an bestehenden Apps. Die aktuelle Auftrag-01-Freigabe ersetzt historische Entwicklungsstopps ausschließlich für Dashboardverwaltung.

Geprüfte Wiederverwendung aus `/workspace/lumo-core-usability-update/ha_app/lumo_data`:

- `client.py`: bounded RFC6455 `Wire`, duplicate-key/NaN-verweigernder JSON-Parser, authentifizierter WS-Handshake und Ergebnisvalidierung. **Nicht übernommen:** HTTP-Transport, Services, Controls, Dashboard-Create/Save oder deren Methoden. Der neue Client hat keinen solchen Codepfad.
- `policy.py`: sichere komponentenweise NOFOLLOW-Optionsdatei und unveränderlicher Optionssnapshot mit latched denial; auf `enabled` und `allowed_user_ids` angepasst.
- `bootstrap.py`: irreversible UID/GID65532-Abgabe, Gruppen-/Capability-/NoNewPrivs-Prüfung; eigenes nicht rekursiv repariertes Datenverzeichnis ergänzt.
- Server-Sicherheitsmuster: begrenzte Header, Fristwächter, ein begrenzter synchroner HTTP-Worker, quiet errors, feste Routen und Ingress-/Origin-Grenze.
- Import: native vorhandene Karten-/Ansichtsdaten bewahren statt einen neuen Raum-/Kacheleditor zu erfinden. Die bisherige Sections-only-Grammatik wurde auf konservativ typisierte einfache native Ansichten/Karten erweitert, mit konkreten Pfaddiagnosen.
- Originales `assets/lumo-logo-v1.png`, SHA256 `702cb856a72674a7f2f9214d6a9da788b87b3651208e0abeba4e8afac07fecd0`. Keine nachgezeichnete Marke.

Das alte `DashboardDocument` verlangt 1–16 Ansichten und dessen Store ist browserlokal. Es wird weder heimlich angepasst noch durch Dummyansichten vorgetäuscht. Die neue Management-Hülle besitzt **0–16 Ansichten**, Owner, stabile ID, Created/Updated, Entwurfsstatus, Datenformat1 und CAS-Revision. `native` enthält eine unabhängige geprüfte vollständige Konfiguration oder null. `views[]` enthält nur Verwaltungsbezüge `{id,title,icon,nativeIndex,backgroundOverride}`; keine neue Raum-/Kachelfunktion. Vorhandene native Inhalte bleiben bei Metadatenänderungen bytewertgleich als JSON-Daten erhalten.

## Persistenz und Revision

SQLite unter `/data/raumstudio/studio.sqlite`, Synchronous FULL, abgeschlossene Verbindungen, kein WAL-Betrieb. Tabellen `dashboards(id,owner,revision,document)` und `images(id,owner,metadata,bytes)`. Sämtliche Eigentumsabfragen enthalten Owner+ID; ausschließlich gebundene SQL-Parameter. JSON trägt `schemaVersion:1`, die DB aktuell `PRAGMA user_version=2`.

Änderungen/Duplikate/Löschen beginnen mit `BEGIN IMMEDIATE`; erwartete Revision wird innerhalb derselben Transaktion geprüft. Konflikt liefert 409. Umbenennen behält ID und Erstellzeit, Duplikate besitzen neue IDs und eigenen JSON-Inhalt. Immutable Bilder dürfen referenziert werden; keine Bildbytes-Update-Route. Bildentfernen ändert nur die Dashboardreferenz. Eigener Upload wird vollständig mit Pillow dekodiert, EXIF-Orientierung normalisiert, in RGBA-PNG ohne zusätzliche Metadaten umkodiert und mit Pixel-/Bytecaps geprüft.

Die UI bestätigt Speicherung erst nach separatem GET desselben Entwurfs und exaktem JSON-Vergleich. Bei Unterbrechung oder uneindeutiger Antwort wird kein automatischer Schreibretry ausgelöst. Auswahl-ID darf in SessionStorage stehen; Entwürfe/Bilder/Eingaben werden nicht als geräteübergreifende Speicherung im Browser ausgegeben.

## Reviewkorrekturen R1–R7

- Listen- und Verwaltungsaktionen halten Ziel-ID und erwartete Revision vor dem Dirty-Guard fest. Nur dessen eigener bestätigter Save desselben Ziels **und derselben Ausgangsrevision** darf die Revision ersetzen; kein Fetch-latest um fremde 409-Konflikte zu übergehen. Eine parallel gespeicherte Neuanlage ändert das Aktionsziel nicht.
- Lokaler vollständiger MDI-SVG-Katalog **7.4.47**, 7447 Namen aus `Templarian/MaterialDesign-SVG` Commit `9e04201d4557e729822fb57f62a316c3dea1d4a8`. `mdi.json` enthält ausschließlich unveränderte Pfaddaten, keine ausführbare SVG-Quelle; Darstellung per festem SVG/viewBox und `createElementNS`. Gleiches JSON ist serverseitige Namens-Allowlist und Clientkatalog. Suchbare bebilderte Auswahl, keine Unicode-Ersatzsymbole für gewählte Icons. Unbekannte Namen/neuere Versionen/Aliasse werden ehrlich abgelehnt; leeres Verwaltungsicon bleibt optional. Lizenztexte und sämtliche Ursprungshashes in `mdi-LICENSE`, `mdi-APACHE-2.0.txt`, `mdi-provenance.json`. MDI-JSON-SHA256: `3f719999c5f613801f790283b86056e723c6fa1667dcf033371499727decd858`. Nur zusätzlicher ingressgeschützter statischer Assetpfad, keine öffentliche Route, kein externes Iconladen, unveränderte CSP.
- Kanonischer API-Versionswert rechts im Header, Original-Logo unverändert.
- Settings verwenden `novalidate` ausschließlich für die explizite vollständige HTML-Validity-Prüfung: ersten ungültigen Control ermitteln, zugehörigen Tab öffnen, fokussieren und `reportValidity()` ausführen. Servervalidierung unverändert aktiv.
- Erfolgreicher Upload/Delete-POST mit fehlgeschlagenem Bestätigungs-GET sperrt alle weiteren Writes im Tab, hält Ziel-ID und Eingaben und fordert bewusste Prüfung in einem neuen Tab. Kein Wiederholungs-/Freigabeautomatismus.
- Import prüft auch Root-Titel, Entities-Zeilenname/-icon sowie den Typ leerer Badgelisten. Alle erlaubten verschachtelten Feldtypen werden gezielt negativ geprüft; Actions bleiben inerte Daten.

Nicht Bestandteil dieser Korrektur: N1-Gesamtabrufbudget, Speicherarchitektur oder zusätzliche Produktfunktionen.

## Sicherheit

- Laufzeit-Listener 8099 nur im App-Netz, keine `ports`, kein Hostnetz. Unmittelbarer Peer ausschließlich `172.30.32.2`; zusätzlich Loopback für den nicht privaten Healthcheck. API/Assets erfordern genau einen gültigen `X-Remote-User-Id`. Forwarded-For beweist keine Identität.
- Der Python-Konstruktor akzeptiert einen Test-Peer und eine Test-HA-Adresse. **Keine** solche Option, Umgebungsvariable oder HTTP-Route im Produktionsstart.
- Supervisor-Token vor Privilegabgabe aus der offiziellen Umgebung nehmen; niemals Browsertransport. Fehlender Token erlaubt lokale Verwaltung, HA-Lesen bleibt nicht verfügbar.
- Herkunftsprüfung, Sec-Fetch-Site, `X-LUMO-Read`, bei Writes Origin + `X-LUMO-Action` + ownergebundener HMAC-CSRF-Token. Token stirbt beim Neustart. Keine CORS-Freigabe.
- Optionsdatei vor Privilegabgabe sicher lesen. Eigenes `/data/raumstudio` mit NOFOLLOW öffnen und ausschließlich bei Neuanlage auf65532 setzen; vorhandene falsche Eigentümer/Modi, Symlinks, Hardlinks und fremde Unterverzeichnisse verursachen sicheren Startabbruch. Keine rekursiven Chowns und kein fremder Datenzugriff.
- Nur feste WS-Kommandos: `config/auth/list`, `lovelace/dashboards/list`, `lovelace/config`. Aktiver Owner oder `system-admin` der **angeforderten Ingress-HA-ID**, nicht des Connector-Users, ist Voraussetzung für jeden Import/Liste-Abruf. Das ist eine bewusst admin-only Anfangsgrenze für die HA-Entityrechte. Lokale Entwürfe anderer erlaubter Benutzer bleiben unabhängig nutzbar.
- Importierte Karten sind inert: niemals HTML/JS oder aktive native Karten im Editor. CSP begrenzt Ressourcen auf self/data/blob, kein beliebiges CSS/URL-Feld. Fehlermeldungen enthalten keine Tokens, Rohtransportfehler oder private Requestlogs.

## Native Hintergrund- und Navigationsabbildung

`native.py` ist eine interne Mappingfunktion für Tests und die spätere Ausgabe, **keine freigegebene Export-/Publikationsfunktion**. Kein HTTP-Export-Endpoint, kein HA-Schreiben.

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
