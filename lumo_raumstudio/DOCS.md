# LUMO Raumstudio – Einrichtung und Bedienung

## Einmalige Einrichtung für Andy

1. **Einstellungen → Apps → App-Store** öffnen, gegebenenfalls über Menü ⋮ nach Updates suchen, dann die **neue App LUMO Raumstudio** aus dem bestehenden Repository `https://github.com/andyspenglermail-prog/LUMO-HA` auswählen und einmalig installieren. Nicht LUMO Data und nicht die ältere Offline-Test-App auswählen. Die bisherigen Apps bleiben unverändert; eine Installation erfolgt ausschließlich durch Dich.
2. App starten und **Weboberfläche öffnen**. Mit den Standardoptionen startet sie bereits sicher, zeigt aber nur Einrichtung statt erfundener Verbindung. Dort steht die eigene, durch HA-Ingress übermittelte **HA-Benutzer-ID**. Sie ist keine Anmeldung und kein Zugriffstoken.
3. In der HA-App-Konfiguration `enabled` aktivieren und diese ID als Eintrag von `allowed_user_ids` speichern. Keine Token, Passwörter, Upstream-Adressen oder Portfreigaben eintragen.

   ```yaml
   enabled: true
   allowed_user_ids:
     - "HIER_DIE_IN_RAUMSTUDIO_ANGEZEIGTE_HA_BENUTZER_ID"
   ```

   Der Platzhalter ist kein gültiger echter Benutzer. Er muss durch die eigene angezeigte ID ersetzt werden. Weitere Benutzer nur bewusst freigeben; jeder sieht ausschließlich seine eigenen Entwürfe und Bilder.
4. Die App nach einer Optionsänderung neu starten und die Weboberfläche neu öffnen. Raumstudio verweigert nach erkannter Änderung weitere Datenzugriffe bis zum Neustart. Es gibt keine stille Rechteerweiterung.

Für lokale Entwürfe genügt ein freigegebener HA-Benutzer. **HA-Dashboard-Import erfordert zusätzlich einen tatsächlich aktiven HA-Administrator.** Raumstudio prüft den angemeldeten Benutzer serverseitig mit HA, unabhängig vom privilegierten Supervisor-Token. `panel_admin` und die Benutzer-Allowlist sind kein Ersatz für diesen Nachweis.

## Dein erstes Dashboard

- Einen Namen (1–80 Zeichen, nicht nur Leerzeichen) eingeben; optional ein echtes MDI-Icon über die bebilderte Suche wählen oder eine unterstützte Kennung wie `mdi:home` eingeben. Der lokale Katalog enthält MDI 7.4.47; unbekannte Kennungen werden abgewiesen, nicht durch Ersatzzeichen verschleiert.
- **Dashboard erstellen** speichert zuerst auf dem App-Server, liest den Stand zurück und öffnet dann die Raum-Übergabe. Der neue Entwurf hat **null Ansichten**. Es werden keine Räume oder Geräte erfunden.
- **Zurück zum Dashboard** führt zu Einstellungen und Vorschau in Schritt 1.
- Gespeicherte Entwürfe bieten Öffnen, Umbenennen, Duplizieren, Einstellungen und bestätigtes Löschen. Löschen betrifft nie ein HA-Dashboard. Duplikate haben eigene IDs; unveränderliche Bildbytes dürfen sicher geteilt werden.
- Allgemein: Name, Beschreibung und Icon. Technische Metadaten befinden sich unter Verwaltung.
- Hintergrund: PNG/JPEG/WebP hochladen, aus der eigenen Bibliothek wählen, ersetzen oder aus dem Entwurf entfernen. Bilder werden vollständig dekodiert und ohne Metadaten als PNG gespeichert. Maximal 8 MiB, 4096 Pixel je Seite und 8 Millionen Pixel; keine Animation/SVG oder externen Bild-URLs. Bibliothek: maximal 100 Bilder beziehungsweise 128 MiB je Benutzer. Entfernen vom Hintergrund löscht keine Bibliotheksdatei.
- Farbe, neun Positionen, Einpassen, Fläche füllen, Originalgröße, Skalierung 10–300 %, Deckkraft 0–100 % und Scroll-/Fixierungsabsicht sind einstellbar. Einstellungen speichern ist nach dem Upload noch notwendig. Die Vorschau reagiert unmittelbar; der Editor selbst bleibt neutral hell.
- Navigation: Icon und Titel, Startansicht bei vorhandenen Ansichten sowie Absichten für spätere HA-Seitenleiste und Administratorbeschränkung. Die letzten beiden Optionen ändern **jetzt keine HA-Rechte**. Ausblenden ist kein Zugriffsschutz.

Die Vorschau zeigt nur den eigenen Namen, die Beschreibung, den Hintergrund und tatsächliche vorhandene Ansichtslabels. Native Karten werden als Daten erhalten, aber nicht aktiv ausgeführt. Die fixierte Hintergrunddarstellung ist im Original-HA-Renderer geprüft; die kleine Vorschau ist bewusst kein scrollender HA-Vollbildrenderer.

## Vorhandenes HA-Dashboard übernehmen

**HA-Dashboards laden** führt einen bewussten einmaligen Leseabruf aus. Eine positive Anzeige belegt diesen Abruf, keine dauerhafte Live-Verbindung. Ohne Abruf bleibt der Status „noch nicht geprüft“.

Die Liste stammt aus `lovelace/dashboards/list`, die Ansichtenzahlen aus tatsächlich gelesenen `lovelace/config`-Antworten. Das Standarddashboard erscheint nur, wenn seine konkrete Konfiguration wirklich lesbar ist. YAML-Dashboards können übernommen werden, soweit die lesbare Konfiguration innerhalb der unterstützten Grammatik liegt; ihre YAML-Datei wird nicht verändert. Automatisch generierte Strategy-Dashboards ohne konkrete unterstützte Ansichten können nicht übernommen werden.

Unterstützt sind konservativ geprüfte native Masonry-/Panel-/Sections-Ansichten und einfache Entity-, Entities-, Tile-, Sensor-, Gauge-, History-Graph-, Heading-, Grid- und Stack-Karten mit dokumentierten Standardoptionen. Nicht unterstützte Typen/Felder werden mit **genauem Konfigurationspfad und Grund** gezeigt. Custom Cards, Templates, beliebige Aktionen, Badges sowie externe Bild-/CSS-Hintergründe werden nicht ungeprüft geladen. Vorhandene einfache Hex-Farbhintergründe bleiben erhalten.

**Kein stiller Teilimport:** Wenn ein Bestandteil nicht unterstützt wird, wird der gesamte Import abgelehnt und nichts gespeichert. Ein erfolgreicher Import enthält die vollständig geprüfte unabhängige Konfiguration. Es gibt weder HA-Konfiguration-speichern noch Dashboard-erstellen/-löschen noch Service-Aufrufe im ausgelieferten Backend.

## Speichern, mehrere Geräte und Konflikte

Entwürfe und Bilder liegen in `/data/raumstudio/studio.sqlite`, nicht in LocalStorage. Derselbe freigegebene HA-Benutzer sieht sie auf anderen Geräten. Ein anderer Benutzer kann sie auch mit einer geratenen ID nicht abrufen.

Revisionen werden atomar geprüft. Hat ein anderes Gerät gespeichert, bleiben Deine Eingaben im Tab erhalten und es erscheint ein Konflikt statt einer Überschreibung. Öffne den aktuellen Stand in einem zweiten Tab und übertrage die gewünschten Änderungen bewusst. Bei unklarer Schreibantwort wird nicht automatisch wiederholt und nicht Erfolg gemeldet; weitere Schreibversuche im selben Tab sind bis zur Klärung gesperrt. Ein neuer Tab kann den tatsächlichen gespeicherten Stand prüfen.

Schrittwechsel fragt bei ungespeicherten Eingaben nach Speichern, Verwerfen oder Abbrechen. Einstellungen-Tabs behalten ihre Eingaben. Beim Reload/Schließen erscheint die normale Browserwarnung. Wie bei normalen Webformularen kann ein erzwungener Browser-/Geräteabsturz ungespeicherte Eingaben verlieren; erst bestätigtes Speichern ist geräteübergreifend dauerhaft.

## Sicherung, Updates und Rückweg

Die App deklariert `backup: cold`. Für einen normalen HA-Backupvorgang diese App einschließen: Supervisor stoppt sie für die Sicherung, und das private `/data` enthält Entwürfe, Bildbytes und Optionsdatei. Sicherungen enthalten private Konfigurationen und dürfen nicht öffentlich geteilt werden. Externe Kopie der HA-Sicherung sicher verwahren.

Vor einem App-Update eine HA-Sicherung erstellen. Bei regulärem Update/Neustart bleibt dasselbe `/data` bestehen. Neue Versionen müssen bekannte Datenformate prüfen und vor einer tatsächlichen Migration sichern. Unbekannte neuere Schemata werden nicht überschrieben.

**Normaler Rückweg:** App stoppen und über HA eine passende vollständige App-Sicherung wiederherstellen; dazu die zum Datenformat passende App-Version verwenden. Nicht nur eine alte Imageversion über einen neueren Datenbestand starten. `maintenance.py` bietet für Entwickler bei gestoppter App zusätzlich geprüfte SQLite-Snapshots, Restore und Schema-1→2-Rollback; Details und ausführbare Tests stehen in `docs/raumstudio/ARCHITECTURE.md`. Keine Restore-HTTP-Route und keine automatische Rücknahme fremder HA-Daten.

## Technische Grenzen

Deklarierte Architekturen: amd64 und aarch64. Python-Baseimage und Pillow-Wheels sind gepinnt. ARM-Prüfungen auf einem x86-Testhost verwenden ausdrücklich Emulation. Reales privates HA-Ingress, physische Touchgeräte, HA-Backup/Restore und persönliche Abnahme bleiben getrennt von lokalen Tests und Imageprüfungen. Kein öffentlicher Hostport, kein Host-Netzwerk, keine zusätzliche Hostinstallation erforderlich.

Bei sehr vielen oder langsam antwortenden HA-Dashboards kann der einmalige Katalogabruf länger dauern und andere Anfragen vorübergehend verzögern. Ein abgebrochener Abruf verändert keine HA-Daten. Die aktuelle Version besitzt noch kein übergreifendes Zeitbudget für den gesamten Katalogabruf.
