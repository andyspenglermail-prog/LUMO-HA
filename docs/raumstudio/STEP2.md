# Schritt 2 · Raum — 0.13.0

## Scope und Grenzen

Autorisierter Auftrag02, Baseline0.12.1 `ee27ba0dbf28269a0cf25ebee67006c32e8913bc`. Derselbe Slug `lumo_raumstudio`; keine Änderungen an Data/Preview. Dashboard→Raum→Design&Display→DeinRaumentwurf bleibt. Die letzten beiden Schritte enthalten keine Gestaltung oder Funktionen. Keine Geräteaktionen, Services, KI, Publikation oder automatische Installation.

Die technische Lieferung ist **nicht** Andys Abnahme. Echte HA-Bereichsschreibprobe ohne freigegebenes Testobjekt bleibt offen. Parent prüft gesondert reales HA-Lesen, Images, Veröffentlichung und exakten öffentlichen Readback. Physischer Touch, installierte App, Storeanzeige, echte HA-Sicherung und persönliche Qualitätsabnahme werden nicht durch Fixturetests ersetzt.

## Architektur und Laufzeit

`rooms.py` ergänzt den bestehenden privaten `CoreClient`-Transport. Die App lädt ihre Daten selbst, niemals aus mitgelieferten Dateien. Fest erlaubte Lesebefehle: `auth/current_user`, `config/area_registry/list`, `config/floor_registry/list`, `config/device_registry/list`, `config/entity_registry/list`, `get_states`, `get_config`; bei abweichender Upstream-Identität zusätzlich `config/auth/list` für den anfragenden Administrator. Der bestehende Dashboardimport bleibt unverändert admin-only.

Vertrauensgrenze: Ingress-Peer-IP und genau ein gültiger Userheader; allowlisted Benutzer, unveränderte Optionen, gleiche Origin und Readheader, für alle POSTs zusätzlich Actionheader und sessionspezifisches CSRF. Gleiche echte Upstream-/Ingress-ID nutzt die von HA erlaubten Reads auch für Nichtadministratoren. Supervisor-/Fremdtokenrechte werden niemals als Rechte des Anfragenden ausgegeben. Ist diese Zuordnung nicht beweisbar, werden Inventarbytes nicht weitergegeben. Lokale Verwaltung bleibt ohne HA verfügbar.

Normalisierung basiert ausschließlich auf IDs. `key=registry:<id>` ist stabil, `entityId` aktueller beobachteter Name. Reine Zustandsentitäten erhalten `key=state:<entity_id>` ohne erfundene Registry-ID. Individuelle Entity-Area hat Vorrang vor Device-Area; Herkunft `entity/device/none`, Floor nur über tatsächlich referenzierten Bereich. Alle Geräte und Registryeinträge bleiben enthalten, auch ohne Bereich/Zustand/Gerät oder mit disabled/hidden/category. State-only-Einträge werden als Vereinigung ergänzt. `available/disabled/missing_state/unavailable/unknown` sind getrennt. Geräteverfügbarkeit wird aus echten Funktionen bzw. disabled-Metadaten abgeleitet, nicht aus Namen/Icons. `viaDeviceId`/`parentDeviceId` stammen ausschließlich aus HA-Metadaten. Attribute bleiben ein Detailobjekt.

Status-/Stateaktualisierung ist ausdrücklich **Polling** alle30s bei sichtbarem Schritt2 sowie manuell/beim Eintritt. Registry und States sind einzelne aufeinanderfolgende HA-Reads, keine atomare Gesamtsnapshot-Transaktion. `fetchedAt` ist der Abschlusszeitpunkt; `lastUpdated/lastChanged` stammen pro Entity aus HA. Fehler liefert keine vermeintlich frischen Ersatzdaten; der Browser markiert den gehaltenen letzten Stand als veraltet. Werte sind observations, keine lokalen Steuerungszustände. Filter, Formfelder und Auswahl werden bei Refresh nicht mutiert.

Grenzen: Wire16MiB/2048Frames/15s pro Verbindung, bis50000 Zeilen je Register. HTTP-POST bleibt auf den bisherigen1MiB/64Ebenen/100000Werte-Vertrag begrenzt. Raumplan bis256 Ansichten, pro Ansicht10000Geräte/30000Entities, zusätzlich gesamtes HTTP-Limit. Keine stillen Kürzungen des gespeicherten Plans. Lange Namen nur bei neuem lokalem Defaulttitel auf80Zeichen begrenzt; Quellname/IDs bleiben inspizierbar.

## Persistentes Modell

SQLite bleibt **user_version2**, Dashboardhülle **schemaVersion1**. Keine Migration oder Umschreibung beim Start/Lesen. Optionales Feld wird erst bei ausdrücklichem Raum-Save hinzugefügt:

```json
{
  "roomPlan": {
    "schemaVersion": 1,
    "views": [{
      "id": "32 lowercase hex characters",
      "title": "Lokaler Titel",
      "icon": "mdi:home",
      "visible": true,
      "areaId": null,
      "source": "virtual",
      "nativeViewId": null,
      "deviceIds": [],
      "entityRefs": []
    }]
  }
}
```

`views`-Arrayposition ist Reihenfolge. `source` ist `virtual`, `ha-area` oder `native`; nativeViewId referenziert ausschließlich die getrennten ursprünglichen Step1-Metadaten. `entityRefs=[{key,entityId}]`. Geräteauswahl ist separat von der expliziten Entityliste: UI-Auswahl eines ganzen Geräts kopiert den **aktuellen** Bestand, wählt später hinzugekommene Funktionen nicht automatisch. Entfernen einer Funktion löscht weder Gerät noch andere Funktionen. Gleiche Referenzen in mehreren Views zeigen denselben Runtimezustand, besitzen aber eigene Viewzugehörigkeit.

`get_plan` erzeugt für bestehende native Views zunächst nur lokale Verwaltungsreferenzen, ohne DB-Write und ohne unbekannte Custom-Card-Semantik zu erfinden. Keine automatische Extraktion fremder Scripts/Templates. Übernommene native Funktionen bleiben im unveränderten Original; die neue Auswahl ist separat zu bearbeiten. `native`, `nativeImport`, alte `views`, Settings, Bilder und der bestehende öffentliche Export werden von Raum-Saves nicht verändert. Step1 zählt lokale und native Ansichten getrennt. Dashboard-Duplikat übernimmt den lokalen Plan unabhängig; View-IDs sind innerhalb eines Dashboards stabil, nicht globale HA-IDs.

CAS erfolgt `BEGIN IMMEDIATE` im bestehenden Ownerdatensatz. Keine Fetch-latest-Konfliktumgehung. Jede entfernte View-ID braucht eine explizite Bestätigung. Neue Geräte-/Area-/Entityreferenzen brauchen den erfolgreich autorisierten echten aktuellen Bestand; bereits gespeicherte fehlende Referenzen bleiben erhalten. Bei erfolgreichem Save werden aktuelle Entity-IDs anhand stabiler Registry-ID nachgeführt. Nur Anzeige aktueller Runtimewerte ist kein Hintergrund-DB-Write. Serverrevision und eigener Reload bestätigen Persistenz. Unklarer POST oder Bestätigungs-GET sperrt weitere Schreibversuche im Tab.

Bestehende0.12.1-Datenbanken werden mit dem **tatsächlichen** Store des Gitpins erzeugt und nach neuer Initialisierung/Backup/Restore auf unveränderte Dokument- und Bildbytes geprüft. Bestehende0.12.0-Legacy-/Unicode-Migrationsregressionen bleiben aktiv. `maintenance.inspect` validiert die optionale Hülle, Backup/Restore behalten sie. Rückweg zu0.12.1 benötigt die vollständige Vor-Update-Sicherung; die alte App versteht roomPlan nicht. Keine automatische Downmigration.

## HTTP-Vertrag

Alle Pfade liegen hinter bestehenden Ingress-/Origin-/Ownergrenzen. Kein öffentlicher beliebiger Origin-/Token-/Commandparameter.

| Route | Vertrag |
|---|---|
| `GET /api/ha/inventory` | `{areas,floors,devices,entities,fetchedAt,status:"fresh",version,canCorrect,permission}`. Frischer autorisierter HA-Abruf. |
| `GET /api/dashboards/<id>/rooms` | `{dashboardId,revision,plan}`; keine Änderung beim Lesen. |
| `POST /api/dashboards/<id>/rooms` | `{revision,plan,confirmedDeletes:[viewId]}`; ganze Dashboardhülle zurück, anschließend separater GET. CAS409, Owner404, ungültige neue Referenz400. |
| `POST /api/dashboards/<id>/area-correction/preview` | `{revision,kind:"device"|"entity",targetId,areaId}`; Entitytarget ist Registry-ID, nicht frei vorgegebener Entityname. Zielarea null erlaubt. Servervorschau enthält zufällige previewId, before/after, Identität, Auswirkungen, betroffene Entity-IDs, Rechte und90s Gültigkeit. |
| `POST /api/dashboards/<id>/area-correction/confirm` | `{previewId,confirm:true}`; ausschließlich gespeichert gebundenes Ziel. Frische Rechte-/Objektprüfung, dann einmaliger Write und echtes Readback. `status:"confirmed"` nur bei bestätigter Zielzuordnung. |

## HA-Schreibgrenze

`area_corrections.py` besitzt allein den eng begrenzten Writer. Keine Create/Delete-/Floor-/Servicepfade. Previewcache ist begrenzt, serverintern, owner-/dashboard-/revisionsgebunden, kurzlebig und beim Neustart leer. Confirmation verbraucht den Token **vor** möglicherweise dispatchendem Code; Rechte werden neu geprüft, frische Registrydaten einschließlich betroffener Funktionen/Bereiche/Etagen gehasht und verglichen. Ablauf wird vor Dispatch nochmals geprüft. Bei geändertem Objekt/Area/Dashboard kein Versand. Browser kann keine neue Ziel-ID oder Area in Confirm einschleusen.

Exakt gesendete Felder neben WS-ID: `type=config/device_registry/update, device_id, area_id` oder `type=config/entity_registry/update, entity_id, area_id`. Der aktuelle Entityname kommt aus dem frisch geprüften Registryeintrag, nie aus dem Confirmpayload. Danach werden Register frisch gelesen und stabile Identität/Entityname/Zielarea verifiziert. Antwortverlust oder abweichendes Readback ist **unklar502**, keine falsche „nichts geändert“-Meldung, kein Retry/Rollback. Vorschauen verschiedener Benutzer/Dashboards sind nicht austauschbar.

**Keine absolute atomare External-CAS-Garantie:** HA bietet keine Revisionsbedingung für Registryupdate. Die externe Lücke zwischen frischem Vergleich und Write bleibt; sie wird UI und Docs offengelegt. LUMO behauptet keine atomare Konkurrenzsperre gegen HA oder andere Integrationen. Teständerungen erfolgen ausschließlich in isolierter Protokollfixture. Reales Haus wurde vom Implementierer weder kontaktiert noch beschrieben.

## UI und Testpfade

`room.js`/`room.css` werden wie die bisherigen Assets same-origin aus der ausgelieferten App geladen und im Dockerfile explizit kopiert. Original-Logo unverändert. Keine lokalen Haushalt-Seeds, externen Skripte, HTML-Injektion, importierten Ressourcen oder neue Bibliothek. Nicht-geheime View-IDs mit `crypto.getRandomValues`, auch normale nicht-sichere LAN-HTTP-Origin getestet.

Tests `test_room_browser.py` und `test_room_lifecycle_browser.py` starten die tatsächliche App/Store/CoreClient mit synthetischer RFC6455-Gegenstelle, keine Fetch-Erfolgsmocks. Sie bedienen Maus/Tastatur und tatsächliche Playwright-Taps, prüfen Desktopspaltengeometrie, Phone/Tablet-Sequenz, Kontextwerte, Refresh, Crossroom, fehlende Entities, Disconnect, Reihenfolge/Duplikat/Confirmeddelete, Dirty-Guard, CAS, separaten Browser, verzögerte Writes und verlorene Readbackantwort. Screenshots sind synthetische Testdaten, keine fertige native Dashboardausgabe.

## R01–R25 Evidenzmatrix

„Lokal“ bedeutet tatsächlich ausgeführte Produkt-/Browser-/Protokollfixturetests, nicht echte HA-Installation. Finale eindeutige Test-IDs, Exitstatus und Bytebindung stehen in `results.json`/`manifest.json` der finalen Evidence. Parent liefert eigene echte Read-only-Belege getrennt.

| ID | Implementierter Nachweis | Offener externer Anteil |
|---|---|---|
| R01 Bereiche | InventoryTests Runtime-Listen + Browser Quellen | Parent reales Anwendungslesen |
| R02 Etagen | ID-basierte Floorzuordnung + Browser Herkunft | Parent echte Flooranzeige |
| R03 vollständige Zuordnung | InventoryTests; private Shapeprüfung aller initialen Einträge nur lokal/aggregiert | Snapshot ist kein Livebeweis |
| R04 Entityoverride | reg2 Vorrang gegenüber Devicearea, Crossroomtest | Parent Livebestand |
| R05 ohne Bereich | Device ohne Entities, gerätelose/state-only Entities; Nichtzugeordnetfilter | Parent Livebestand |
| R06 vorhandene Ansicht | native Overlaytests + zweiter Browser öffnet gespeicherte View | Persönliche Bedienabnahme |
| R07 virtuell | UI Neue Ansicht und HTTP-Persistenz | Persönliche Bedienabnahme |
| R08 Rename | ID/Referenzen bleiben, Readback/Restart | Keine zusätzliche technische Lücke |
| R09 Duplikat | eigene lokale ID, gleiche stabile Quellen, unabhängiger Titel | Persönliche Bedienabnahme |
| R10 Entfernen | UI Cancel/Confirm, serverseitige removed-ID-Bestätigung, Undo | Kein HA-Delete |
| R11 Gerät hinzufügen | tatsächliche vollständige Deviceentityliste, separate Geräte-ID | Parent echte Auswahl |
| R12 einzelne Entity | Check/Uncheck/Undo, stabile Referenz, state-only | Parent echte Auswahl |
| R13 Multi-Entity | Licht/Sensor/deaktivierter Schalter eines Geräts bleiben separat | Keine erfundenen Attributentities |
| R14 Crossroom | dieselbe Entity in zwei Views, identischer frischer Wert, HA-Area unverändert | Parent echte Referenzprobe |
| R15 Suche/Filter | Bereich, Name/ID/Domain, sichtbare Mehrfachauswahl; explizit Außentreffer | Parent reale Namen/Größe |
| R16 HA vs lokal | separate Herkunft/Properties/Referenzen und Nativeexportgleichheit | Persönliche Verständlichkeit |
| R17 HA-Korrektur | echter Fixture-WS-Write+Readback, Stale/Expiry/Uncertain/No-retry | **Echte Schreibprobe OFFEN**, kein autorisiertes Testobjekt |
| R18 Rechte | Same-user-Nichtadmin liest, fremder Token kein Rechtebeweis; Korrektur403 | Parent echte Nichtadmin-/Ingressprüfung |
| R19 Disconnect | API kein Fakebestand; UI veraltet hält Eingaben; missing/disabled/unknown | Reale Netzwerkstörung nicht provoziert |
| R20 Save/Open | HTTP/SQLite+Readback, Browserreload/Öffnen | Persönliche Bedienabnahme |
| R21 Geräte/Update | zweiter Browser, Serverrestart, echtes0.12.1-DB-Upgrade, Backup/Restore | Installiertes HA-Update/Coldbackup offen |
| R22 Schrittwechsel | Save/Discard/Cancel und erhaltene Auswahl | Schritte3/4 nur Übergabe |
| R23 responsiv | 1480×960 Desktop,820×1080 Tablet,390×844 Phone, echte emulierte Taps | Physische Geräte/Andy offen |
| R24 Haus unverändert | Fixture-Commandlisten/HA-Konfiggleichheit; keine neuen Aktionen, Nativeexport gleich | Parent read-only Live-Allowlist/Belege |
| R25 Updateweg | gleicher Slug0.13.0, DockerCOPY/Version/Docs/alte Tests | Parent Images/Publikation; Storeanzeige/Installation/Abnahme offen |

## Primärquellen

Offizielle HA-Core-Quellen des tatsächlich gemeldeten Versionspins **2026.11.0**, vom Parent in Evidence/research bereitgestellt und vor Writerbau gelesen. `HA-CORE-SOURCES.json` hält öffentliche Quell-URLs und SHA256 ohne private Dateipfade. Relevant: area/floor/device/entity registry list, admin-required device/entity area update, config/auth/list und get_states-Berechtigungsfilter. Keine unsupported arbitrary Proxyroute. Live `auth/current_user`-Feldformen wurden zusätzlich am privaten initialen Snapshot ausschließlich auf Struktur geprüft; keine Inhalte in Fixtures/Repo.

## Ausführen / Übergabe

`./scripts/run_tests.sh` (bestehendes Playwright/Chromium und offizieller Assetcache erforderlich; keine Installation durch Tests). Standard-Evidence unter `/workspace/lumo-auftrag02-evidence/implementation/final/browser`, ältere Evidence bleibt unberührt. Alle65 vorhandenen Testmethoden bleiben erhalten; ausschließlich0.13.0-Version, tatsächliche neue Schritt2-Navigation und zusätzliche feste Readkommandos wurden in alten Browser-/Packageerwartungen angepasst. Keine alten Sicherheits-/Losslessasserts entfernt. Pro materialem Slice isolierte RED-Kopie vor Produktänderung; weitere bestehendes Verhalten bestätigende Tests werden nicht nachträglich als RED behauptet.

Live-Harness: bestehender privater CoreClient-Konstruktor für direkten Diagnosehost oder regulärer Supervisorstart, temporärer owner-scoped Store und Optionssnapshot, echte Ingress-ID, tatsächlicher Appserver und Browser. Kein neues Login-/Token-/Originfeld. Parent injiziert Credentials nur ephemer; um `_ws_reads` eine read-only-Allowlist erzwingen, keine Livekorrektur dispatchen. Private Screenshots/Responses bleiben privat. Detaillierte Route-/Selektorübergabe liegt zusätzlich in Evidence/implementation/LIVE-HANDOFF.md.
