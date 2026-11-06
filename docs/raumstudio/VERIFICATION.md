# Raumstudio – Verifikation und Abnahmegrenzen

## Aktueller Vertrag0.13.0 — Auftrag02 Raum

[STEP2.md](STEP2.md) enthält R01–R25, Modell/API und getrennte Abnahmegrenzen. Alle65 bisher vorhandenen Testmethoden bleiben aktiv. Zusätzliche Tests umfassen tatsächliche Runtime-Registry/State-Protokollreads, stabile Normalisierung, lokale Raum-Lifecycle/CAS/Owner/Backup/Upgrade, eng gebundene Bereichskorrektur einschließlich echter Fixturewrites und negative Fälle, sowie reale Browser→Backend→CoreClient→RFC6455-Peer-Workflows. Die Quelle des privaten initialen Bestands wird nur vom Parent und lokal zur Shapeprüfung verwendet, niemals als Produktionsdatenquelle oder öffentliches Fixture. Echte Liveanwendungsreads, Images und Veröffentlichung prüft Parent separat; echte HA-Schreibprobe und installierte persönliche Abnahme bleiben offen.

Isolierte RED-Kontrollkopien plus Rohlogs unter neuer Auftrag02-Evidence belegen Inventar, Persistenz, Writer, UI, Layout-/Offlinekorrekturen, Verpackung und Ablaufgrenze. Nachträge, die bestehendes Verhalten zusätzlich testen und direkt grün sind, werden nicht als test-first RED behauptet. Das vollständige Ergebnis zählt tatsächliche eindeutige Methoden, keine Subcase-/Wiederholungsaddition. Der finale Lauf wird gegen die endgültigen Quellbytes ausgeführt und auf Byteänderungen geprüft. Finales `results.json`/`manifest.json` sind maßgeblich, nicht ein historischer Zwischenlauf.

Alte Browserexpectations wurden nur für die jetzt echte Raumseite (`#room-step`/`#room-back` statt der damaligen Übergabe), Version0.13.0 und den zusätzlichen festen Registry/State-Readsatz angepasst. Nichtnative Dashboard-/Gerätewriter bleiben verboten; sämtliche Sicherheits-, Lossless-, Bild- und Legacyasserts bleiben erhalten. Die Step1-Protokollfixture liefert bei neuem Raumread ausdrücklich leere synthetische Register. Runtime verwendet nie diese Fixture.

Testdefault-Evidence ist jetzt `/workspace/lumo-auftrag02-evidence/implementation/final/browser`; die folgenden historischen Pfade und Ergebnisse bleiben unverändert historische Angaben. Physische Touchgeräte, echter Store/Installationsablauf und Andy werden nicht durch Browseremulation ersetzt.

## Historischer Vertrag 0.12.1 – verlustfreie Importkorrektur

Die 0.12.0-Basis `c1ffa3434d95a59f0538573173d8138927388811` wurde separat eingefroren. Der erste synthetische Import-/Roundtriptest wurde vor Produktänderungen gegen einen `git archive`-Kontrollcheckout ausgeführt und scheiterte an der Ablehnung opaker Schlüssel. Spätere vertikale RED/GREEN-Schritte prüfen reale HTTP-Export-/Edit-/Reportabläufe, Browserbedienung, JSON-Grenzen, Versionswert, versteckte Validierungsfelder, Legacy-Prüfung, Strategy-Darstellung, begrenzte Diagnostik und Backupintegrität. Tests installieren nichts und greifen nicht auf produktives HA zu.

Die zusätzlichen Methoden in `test_lossless.py` und `test_lossless_browser.py` prüfen:

- vollständiges Original mit `custom:button-card`, `button_card_templates`, `card_mod`, verschachtelten unbekannten Daten, `__proto__`/`constructor`, ungewöhnlichen Feldtypen, großen Integern und geordneten Listen;
- Import → persistierte SQLite-Hülle → tatsächlicher UI-Download → JSON-Vergleich; unverändert nach Verwaltungsname, Hintergrund-/Navigationssettings, Reload und Duplikat;
- genau einen erlaubten Pfad ändern, alle anderen Pfade erhalten; geschützte Pfade, gemischte Editbatches und direkte Source-Manipulation verweigern;
- echte Ressourcen-Registryantwort getrennt erhalten; fehlender Abruf bleibt unbekannt; Strategy ohne erfundene Views;
- echter Browser → Ingress-Testproxy → HTTP → Store mit wirklichem CoreClient/RFC6455-Peer, ohne Fetch-Erfolgsmocks; keine externen Requests oder Script-/Templateausführung;
- Owner404, CAS409, CSRF403; Browserkonflikt und verlorenes Bestätigungs-GET erhalten Eingaben und sperren automatische Wiederholung;
- echte SQLite-Sicherung/Restore, erneutes Öffnen, vollständige Legacy-Hülle und Ablehnung beschädigter Importmarker/geschützter Editledger;
- endliche/gebundene JSON-Daten getrennt von unterstützter Grammatik; lange opake Schlüssel bleiben im Export vollständig, werden aber in technischen Pfadbeispielen begrenzt.

Die bisherige Raumstudio-Suite bleibt aktiv. Bewusst geänderte Importerwartungen: Custom Cards, fremde Icons, Badges, ungewöhnliche Feldtypen und Strategy sind jetzt importierbar statt pauschal 422. Das ist der freigegebene neue Vertrag, kein geschwächter Schutz erlaubter Schreibfelder. Die ursprüngliche konservative Grammatik und ihre 219 rekursiven Typmutationen bleiben als `validate_supported_configuration` für Legacy-Prüfung erhalten. Hintergrund-/Originalrenderer-Tests verwenden ausdrücklich Legacy-Hüllen ohne `nativeImport`; sie behaupten keine Neunormalisierung neuer Importe. Versionsasserts erwarten 0.12.1; der zulässige feste WS-Lesesatz enthält zusätzlich `lovelace/resources/list`.

Aktuelle maschinenlesbare Ergebnisse und Quellhashes entstehen in `results.json` und `manifest.json` neben dem konfigurierten Browser-Evidenceordner. Der finale Lauf zählt tatsächlich ausgeführte eindeutige Methoden; Wiederholungen/Subcases zählen nicht zusätzlich. Einzelne REDs und zwischenzeitliche Regressionen sind historische Nachweise, keine finalen Fehlerbehauptungen. Die unveränderte Sourceclosure während des Laufs wird geprüft.

Die nachfolgende 48-Methoden-/Imagebeschreibung ist **historisch für 0.12.0**. Sie ist kein Image-/Veröffentlichungsnachweis für die geänderten 0.12.1-Bytes. Für 0.12.1 bleiben unabhängiger Review, aktuelle amd64/aarch64-Imageprüfung, reale private HA-Referenzabnahme, Repositoryveröffentlichung/Remote-Readback und persönliche Abnahme getrennte Parent-Gates. Private Referenzen werden nicht in Tests oder öffentliche Evidence kopiert. Die Implementierung hat verfügbare private Referenzen nur lokal im Speicher auf Datenübernahme/Berichterstellung geprüft; keine privaten Datenbank- oder HA-Schreibvorgänge.

## Historischer technischer Stand 0.12.0

Der abschließende Parent-Lauf hat **48 von 48 eindeutigen Testmethoden**
erfolgreich ausgeführt, ohne Skips. Die sieben ursprünglichen Reviewbefunde
besitzen gezielte RED/GREEN-Regressionen. Wiederholte Läufe und die 219
rekursiven Import-Typmutationen sind keine zusätzlichen Testmethoden.

Die korrigierten Runtimebytes einschließlich der lokalen MDI-Assets wurden in
beiden Images tatsächlich gestartet: **amd64** und **aarch64 unter Emulation**.
Geprüft wurden Defaultstart, Rechteabgabe auf UID/GID 65532, leere effektive
Capabilities, gesperrter direkter Ingresszugriff, echte HTTP-Entwurfs-/Bildabläufe,
Benutzerisolation, Neustart, Containerersatz mit demselben privaten Testvolume und
Offline-Backup/Restore. Alle 20 ausgelieferten Runtime-Dateien stimmten mit den
gepinnten Quellbytes überein. Kein produktiver HA-Zugriff, kein öffentlicher Port.

Auf dem x86-Testhost wurde ausschließlich der fremde ARM-Paketinstallations-RUN
mit einem temporären, SHA-geprüften QEMU-Adapter ausgeführt, einschließlich der
echten musl-Loadererkennung von Pip. Wheel-/Hashprüfung blieb aktiv. Das
ausgelieferte Dockerfile blieb unverändert; kein Emulator im Image und keine
Host-binfmt-Installation. Das ist kein nativer ARM-/Supervisor-Installationsnachweis.

Diese Dokumentation ersetzt weder den exakten Repository-Readback noch private
HA-Installation, physische Endgeräteprüfung oder Andys persönliche Endabnahme.

## Ausführen

Ausschließlich neue App und neue Tests:

```sh
./scripts/run_tests.sh
```

Kein pytest vorausgesetzt, keine alten Suiten/Builds. Der Runner verwendet unittest, echte temporäre SQLite-Dateien, einen synthetischen RFC6455-HA-Peer, die wirkliche App über HTTP sowie einen isolierten Test-Ingressproxy. Browser: vorhandenes Playwright unter `/workspace/jarvis-voice-prototype/.test-deps`, Chromium unter `/opt/playwright`; kein Hostbrowser, kein Profil, keine Zugangsdaten. Bootstrap-Test läuft in einem separaten **Container**-Root-Prozess und gibt dort irreversibel Rechte ab; für diesen Test ist Sandbox-Root Voraussetzung.

Überschreibbare reine **Test**-Umgebung:

- `PYTHONPATH`: Verzeichnis mit dem vorhandenen Playwright-Pythonpaket.
- `PLAYWRIGHT_BROWSERS_PATH`: vorhandene Browserbins.
- `RAUMSTUDIO_EVIDENCE`: Ausgabeordner der Tests, Standard für 0.12.1 `/workspace/lumo-import-evidence/implementation/final/browser`; frühere Evidence wird nicht überschrieben.
- `HA_NATIVE_CACHE`: SHA-gepinnter offizieller Assetcache, Standard `/workspace/lumo-core-usability-evidence/native-feasibility`. Er enthält `asset-pins.json` und `assets/<sha256>`. Dieser Testcache gehört **nicht** zur produktiven App. Fehlt er, schlägt das Native-Gate fehl statt einen Pass zu erfinden. Tests installieren keine Abhängigkeiten.

Der Runner schreibt neben dem Browserordner `results.json` und `manifest.json`, zählt **eindeutige tatsächlich gestartete Methoden** und prüft sämtliche neuen Quell-/Test-/Dokumentbytes vor und nach dem Lauf. Einzelne Subcases oder wiederholte RED/GREEN-Läufe erhöhen diese Zahl nicht. Inkrementelle historische Logs sind separat nummeriert; sie ersetzen nicht den finalen Lauf.

## D01–D22-Matrix

„Lokal geprüft“ bezeichnet synthetische/in-container Ausführung, nicht Veröffentlichung oder HA-Installation. Konkrete Ergebniswerte und Hashes stehen in der jeweiligen `results.json`; fehlgeschlagene historische REDs sind keine finalen Ergebnisse.

| ID | Lokaler Nachweis | Extern offen / Grenze |
|---|---|---|
| D01 Erstellen | StoreTests `test_create_persistent_empty_owned_dashboard`; HTTPTests `test_create_readback_owner_and_restart`; BrowserTests `test_create_settings_reload_second_device`; 0 Ansichten, echtes Save vor Schritt2 | Persönliche Bedienabnahme |
| D02 Ungültige Namen | StoreTests `test_validation_and_revision_lifecycle`, `test_invalid_text_never_commits`; BrowserTests `test_rename_validation_stays_visible_in_dialog`; SecurityTests malformed | Browserwarnungen sind systemsprachabhängig; Servertexte deutsch |
| D03 Browserneustartpersistenz | Browser-Reload und frische Kontexte, SQLite-Neuöffnung, HTTP-Neustart | Kein physischer Geräte-Neustart |
| D04 Geräteübergreifend/Rechte | Zwei getrennte Browserkontexte desselben Benutzers; fremder Benutzer leer/404; HTTP-Bildrechte | Zwei physische Endgeräte offen |
| D05 Rename stabile ID | Store-Lifecycle, reale UI-Umbenennung mit Fehlerkorrektur | Keine |
| D06 Unabhängige Kopie | Store-Lifecycle, ImportTests, Workflow-Duplikat; native Daten nicht gemeinsam mutierbar | Immutable Bildreferenzen bewusst gemeinsam |
| D07 Confirmdelete | Store verweigert fehlendes Confirm; Workflow Cancel + bestätigte Löschung mit Readback | Kein HA-Löschcode vorhanden |
| D08 Echte Ermittlung | HATests + SecurityTests: echte App-WS-Frames gegen synthetischen HA-Peer, Liste/config/auth und echte Config-Ansichtenzahl | Reale HA-Version/privater Ingress noch nicht geprüft |
| D09 Unabhängiger Import | ImportTests und Wire+Browser-Workflow erhalten geprüfte Konfiguration; HA-Peer vorher/nachher gleich | Kein beliebiger Fremddashboard-Editor |
| D10 Nicht unterstützt | Genaue Pfade/Typen im UI und HTTP422; gemischte/unsupported Konfiguration atomar abgewiesen | Kein Teilimport, keine still verworfenen Felder |
| D11 Upload | ImageTests, SecurityTests echte Decoder für PNG/JPEG/WebP, SVG/truncated/pixel/bytes denied; UI-Fileupload | Physische Dateiauswahl nur browseremuliert |
| D12 Wechsel/Entfernen | Workflow: zweites Bild, Bibliotheksauswahl, Reload, Entfernen, ursprüngliche Bildbytes erhalten | Bibliothek wird nicht durch Entwurfslöschung gelöscht |
| D13 Farbe/Darstellung | Store settings, NativeTests, Original NativeRuntimeTests, Browser-Einstellungen | Private HA-Ausgabe nicht publiziert |
| D14 Sofortvorschau | Browser computed styles und neutralweißer Editor; echte Daten/Ansichtslabels; native Runtime mit Pixelprobe 0 % | Vorschau führt keine importierten Karten aus; kein HA-Vollbildrenderer |
| D15 Updatepersistenz | Gleicher SQLite-Bestand nach Server-/Store-Neustart; Schema1→2-Lauf; finale Images auf beiden Architekturen neu gestartet und Container mit demselben Testvolume ersetzt, Entwürfe/Bilder/Einstellungen erhalten | Reales privates HA-Update separat |
| D16 Keine stillen Eingabeverluste | Workflow dirtyguard Save/Cancel, Tabwechsel, Reload-Beforeunload-Dismiss, CAS, zwei begonnene Formulare, Start-/Laderace | Erzwungener Browserabsturz kann ungespeicherte Formulare verlieren |
| D17 Rechte/Fehler | Origin/CSRF/duplicate headers/deep JSON/denied user/active admin geprüft; unklare POST-Antwort nach tatsächlichem Commit im Proxy verloren, kein Retry | Reale HA-Rechteumgebung separat |
| D18 Geräte/UI | 1440×900, 1280×720, 768×1024, 1024×768, 390×844, 844×390, 320×640; echte Playwright taps + Tastatur; sichtbarer Modalfooter/Fehler; Screenshots angesehen, keine normalen horizontalen Überläufe | Physischer Touch und Andys Qualitätsabnahme offen |
| D19 Version | config.json0.12.0, PackageTests, API, Header rechts und Image-Buildlabel mit Supervisor-Args geprüft | Keine |
| D20 HA-App | Vollständige neue App, Dockerfile/COPY/Hashwheel/Config/Docs; amd64 und emuliertes aarch64 gebaut und tatsächlich gestartet, Defaultsetup und sichere UID geprüft | Repository-Readback separat; private Store-Sichtbarkeit und Installation nicht durch uns geprüft |
| D21 HA unverändert | Peer-Configs bytewertgleich vor/nach Aktionen; WS-Allowlist; AST: kein HA-Writer im ausgelieferten Client | Keine produktiven HA-Daten abgerufen oder geändert |
| D22 Backup/Migration/Rückweg | MaintenanceTests: echte SQLite-Snapshots, Decoder-/Datensatzprüfung, atomarer Restore, corrupted/newer refused, Migrationbackup und Fehlerrollback | Tatsächliches HA-Coldbackup/Restore auf privatem System offen |

## Weitere ausgeübte Grenzen

- Wechselnde echte Proxy-Prefixe und normale nicht-sichere `http://studio.invalid`-Browserorigin, nur über isolierten Resolver an die Loopback-Fixture gebunden. Keine Umgehung einer privaten HA-Netzsperre.
- Verlust einer HTTP-Schreibantwort wird **nach echter App-Persistierung** im Testproxy erzeugt; keine fetch-Mock-Erfolgsdaten.
- Native Root-/Backgroundprobe nutzt unveränderte gecachte offizielle JS-Assets; kein kopierter Nachbau der CSS-Komponente. Vier Hintergrundfälle und View-Overridepriorität.
- Keine Versions-/Quellpins historischer Alt-Apps neu generiert; keine bestehenden Suites ausgeführt.

## Gezielte Reviewregressionen

`test_review_browser.py` und `test_review_backend.py` ergänzen ausschließlich R1–R7. Evidence dieser Korrektur liegt neu unter `/workspace/lumo-auftrag01-evidence/fix-1/`; frühere Nachweise bleiben unverändert. Pro Blocker echte beobachtete REDs vor dem jeweiligen Fix, danach gleiche GREEN-Testmethoden. Die zusätzlichen Methoden prüfen Own-save-Revisionen, stabiles Verwaltungsziel trotz zweier begonnener Formulare, Cancel/fremde 409, SVG-Pfaddaten/Picker/Serverallowlist, Headergeometrie mit Touch und Tastatur an sieben Viewports, verborgene ungültige Settingsfelder ohne Konsolenfehler, **erst nach erfolgreichem POST verlorene GET-Antworten**, sowie vollständige rekursive Import-Feldtypen und atomare HTTP-Verweigerung.

Der vollständige neue App-Runner bleibt unverändert. Der erste Korrekturlauf umfasste 32 bisherige Methoden plus 15 Regressionen; die letzte Busy-Sperren-Regression ergänzt eine weitere Methode mit drei Transportphasen. Alle **48 Methoden** wurden nach der letzten Runtimekorrektur vollständig erfolgreich ausgeführt. Wiederholungen werden nicht addiert. Bild-/Native-/Originalasset-Prüfungen bleiben vollständig aktiv. Maschinenlesbare Parentnachweise: `parent-final-2/results.json`, `parent-final-2/manifest.json` und `final-image-receipt-2.json` im getrennten Entwicklungs-Evidenceverzeichnis. Der öffentliche Quellstand enthält keine privaten Testprotokolle.

Der zusätzliche Reviewbefund R8 wurde tatsächlich reproduziert: Eine verzögerte erfolgreiche Speicherantwort oder Bestätigungsleseantwort ließ die Skalierung wieder bearbeiten und verwarf die neue Eingabe danach still. `preview()` und `fill()` respektieren jetzt die laufende Busy-Sperre. `test_busy_write.py` hält echte POST-, Bestätigungs-GET- und Listen-GET-Antworten nach erfolgter App-Verarbeitung zurück. In allen drei Phasen bleiben Skalierung und Startansicht gesperrt; Tastatureingaben werden nicht angenommen. Nach Abschluss lassen sich neue Änderungen normal eingeben und speichern. RED und GREEN liegen getrennt unter `fix-2/`. Die finale Imageprüfung wurde mit diesen korrigierten Bytes wiederholt.

Historische Imageprüfungen vor den Korrekturen bleiben separat. Die oben genannten finalen Imageprüfungen beziehen sich auf die korrigierten Runtimebytes einschließlich MDI-Assets. Keine Crosscompile-/Hoständerung im Kandidaten.

## Externe Gates des Parent

1. Unabhängiger Security-/Code-/UX-Review exakt des finalen Hashmanifests.
2. Images für deklarierte Architekturen bauen/starten, echte Container-UID/Rechte/Capabilities und statische Assets prüfen; erneut starten/updaten auf demselben eigenen Datenvolume, Defaultoptionen und persistierte Entwürfe/Bilder lesen.
3. Nur nach Freigabe Veröffentlichung auf dem bestehenden Repository, anonymer exakter Readback.
4. Private Installation/Ingress/HA-Coldbackup und physische Geräte-/Nutzerabnahme getrennt behandeln.

Kein Taskstatus, Auftrag oder Abnahmepunkt wird durch dieses Dokument als extern abgeschlossen erklärt.
