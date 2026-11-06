# LUMO Raumstudio 0.12.1 – Einrichtung und Bedienung

0.12.1 aktualisiert die bestehende App mit unverändertem Slug `lumo_raumstudio`. Keine neue App nötig. Veröffentlichung, Aktualisierung/Installation und persönliche Abnahme bleiben getrennt. Vor einem Update sichern.

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

Die Vorschau zeigt nur den eigenen Namen, die Beschreibung, den Hintergrund und tatsächliche vorhandene Ansichtslabels. Native Karten werden als Daten erhalten, aber nicht aktiv ausgeführt. Die interne Legacy-Abbildung fixierter Hintergründe ist im Original-HA-Renderer geprüft; neue Importkopien verwenden diese Umrechnung ausdrücklich nicht; die kleine Vorschau ist bewusst kein scrollender HA-Vollbildrenderer.

## Vorhandenes HA-Dashboard übernehmen

**HA-Dashboards laden** führt einen bewussten einmaligen Leseabruf aus. Eine positive Anzeige belegt diesen Abruf, keine dauerhafte Live-Verbindung. Ohne Abruf bleibt der Status „noch nicht geprüft“.

Die Liste stammt aus `lovelace/dashboards/list`, die Ansichtenzahlen aus tatsächlich gelesenen `lovelace/config`-Antworten. Das Standarddashboard erscheint nur, wenn seine Konfiguration wirklich lesbar ist. YAML-Dashboards und automatisch erzeugte Strategy-Konfigurationen werden als die von HA gelieferte JSON-Konfiguration übernommen. Nicht vorhandene Ansichten werden nicht erfunden. YAML-Quellkommentare, Formatierung, Includes und externe Dateien lassen sich daraus nicht rekonstruieren.

**Importierbar bedeutet nicht vollständig bearbeitbar oder funktionsgeprüft.** Custom Cards (auch `custom:button-card`), `button_card_templates`, `card_mod`, beliebige weitere Schlüssel, Aktionen und externe Bild-/CSS-Hintergründe bleiben unverändert erhalten. Selbst Optionen, deren Bedeutung LUMO nicht kennt, werden nicht entfernt oder normalisiert. LUMO führt keine importierten Karten, Skripte, Templates oder Styles aus und lädt keine importierten Ressourcenadressen.

Nach der Übernahme zeigt der **Importbericht** eine verständliche Zusammenfassung. **Technische Details und Abhängigkeiten** lassen sich aufklappen. Die separat gespeicherte Ressourcenliste wird ausschließlich über den festen Lesebefehl `lovelace/resources/list` abgefragt. Scheitert dieser, lautet der Status *nicht verfügbar/unbekannt*, nicht *keine Ressourcen nötig*. Gelesene Einträge sind lediglich *registriert, ungeprüft*. Eine leere erfolgreiche Liste sagt nur, dass HA bei diesem Abruf keine Einträge geliefert hat. Weder Existenz noch Funktion der Dateien oder vollständige Zuordnung von Karten zu URLs werden behauptet. Es gibt keine HEAD-/GET-Probe der Ressourcen-URLs und keine Installation von Bibliotheken oder Themes.

**Unterstützte Elemente gezielt bearbeiten** befindet sich ausschließlich im Importdetail von Schritt 1. Wähle ein Element und eines seiner angebotenen vorhandenen Textfelder: nativer Dashboard-/Ansichtstitel, Titel/Name/Überschrift unterstützter Karten, MDI-Symbol oder Entitätskennung. Unterstützte Karten: Entity, Entities, Tile, Sensor, Gauge, History Graph, Heading und Titel bekannter Stack-Container; bekannte Grid-/Stack-Container werden rekursiv durchsucht. Nicht alle diese Typen besitzen jedes Feld. Benutzerdefinierte Kartentypen, dynamische Template-Werte und nicht angebotene Felder bleiben geschützt. Keine neuen Karten/Ansichten, Strukturänderungen, Listenumsortierung oder Raumeditoren. Symbole sind auf den lokalen MDI-Katalog beschränkt; Entitätskennungen werden syntaktisch geprüft, nicht auf Existenz oder Bedienbarkeit getestet. **Nur dieses Feld speichern** ändert genau diesen vorhandenen Pfad, nicht seine Nachbarn. Während einer offenen Feldänderung sind die anderen Einstellungen gesperrt; vor dem Wechsel speichern oder ausdrücklich verwerfen.

**Verwaltungsname ist nicht nativer HA-Titel.** Name, Beschreibung, Icon, Hintergrund und Navigation in den Dashboard-Einstellungen sind für neue Importe ausdrücklich gekennzeichnete LUMO-Verwaltung/lokale Vorschau. Sie verändern den nativen Export nicht, auch beim normalen Einstellungen-Speichern nicht. Geschützte importierte Hintergründe werden nie dadurch ersetzt oder im Editor geladen. Die kleine Vorschau ist keine Wiedergabe des importierten HA-Dashboards.

**Gespeicherte HA-Kopie herunterladen · JSON** lädt die aktuelle serverseitige Konfiguration als Datei. Ohne gezielte Feldänderung bleiben alle Schlüssel, JSON-Typen, Werte und Listenreihenfolgen erhalten; nach einer Feldänderung weicht nur der ausdrücklich gespeicherte Pfad ab. Objektformatierung und Whitespace sind keine Rohtext-Garantie. Der Browser lädt originale Serverbytes, ohne große Zahlen neu zu serialisieren. Ungespeicherte Eingaben, Ressourcenregister, externe Bibliotheken, Themes und Dateien sind nicht Bestandteil dieses Konfigurationsdownloads. Die vollständige App-Sicherung enthält zusätzlich die getrennte Ressourcen-Momentaufnahme und das unveränderte Original.

**Kein Teilimport:** Nicht sichere oder zu große JSON-Daten werden vollständig abgewiesen, nicht teilweise übernommen. Grenzen: JSON-Objekt am Root, endliche Zahlen, höchstens 64 Verschachtelungsebenen, 100.000 Werte und 1 MiB bei sicherer ASCII-JSON-Serialisierung. Technische Pfadbeispiele und externe Referenzen werden im Bericht auf je 200 begrenzt; höchstens 1.000 Elemente erscheinen im Feldeditor. Überlange unbekannte Schlüssel werden nur in technischen Pfadbeispielen auf 160 Zeichen plus Auslassungszeichen verkürzt und mit `pathTruncated` markiert. Diese Anzeigegrenzen kürzen niemals den gespeicherten oder exportierten Inhalt. Es gibt weder HA-Konfiguration-speichern noch Dashboard-erstellen/-löschen noch Service-Aufrufe im ausgelieferten Backend.

## Speichern, mehrere Geräte und Konflikte

Entwürfe und Bilder liegen in `/data/raumstudio/studio.sqlite`, nicht in LocalStorage. Derselbe freigegebene HA-Benutzer sieht sie auf anderen Geräten. Ein anderer Benutzer kann sie auch mit einer geratenen ID nicht abrufen.

Revisionen werden atomar geprüft. Hat ein anderes Gerät gespeichert, bleiben Deine Eingaben im Tab erhalten und es erscheint ein Konflikt statt einer Überschreibung. Öffne den aktuellen Stand in einem zweiten Tab und übertrage die gewünschten Änderungen bewusst. Bei unklarer Schreibantwort wird nicht automatisch wiederholt und nicht Erfolg gemeldet; weitere Schreibversuche im selben Tab sind bis zur Klärung gesperrt. Ein neuer Tab kann den tatsächlichen gespeicherten Stand prüfen.

Schrittwechsel fragt bei ungespeicherten Eingaben nach Speichern, Verwerfen oder Abbrechen. Einstellungen-Tabs behalten ihre Eingaben. Beim Reload/Schließen erscheint die normale Browserwarnung. Wie bei normalen Webformularen kann ein erzwungener Browser-/Geräteabsturz ungespeicherte Eingaben verlieren; erst bestätigtes Speichern ist geräteübergreifend dauerhaft.

## Sicherung, Updates und Rückweg

Die App deklariert `backup: cold`. Für einen normalen HA-Backupvorgang diese App einschließen: Supervisor stoppt sie für die Sicherung, und das private `/data` enthält Entwürfe, Bildbytes und Optionsdatei. Sicherungen enthalten private Konfigurationen und dürfen nicht öffentlich geteilt werden. Externe Kopie der HA-Sicherung sicher verwahren.

Vor einem App-Update eine HA-Sicherung erstellen. Bei regulärem Update/Neustart bleibt dasselbe `/data` bestehen. Neue Versionen müssen bekannte Datenformate prüfen und vor einer tatsächlichen Migration sichern. Unbekannte neuere Schemata werden nicht überschrieben.

**Normaler Rückweg:** App stoppen und über HA eine passende vollständige App-Sicherung wiederherstellen; dazu die zum Datenformat passende App-Version verwenden. Nicht nur eine alte Imageversion über einen neueren Datenbestand starten. 0.12.0 versteht die zusätzliche `nativeImport`-Hülle nicht; für einen Rückweg die vollständige Vor-Update-Sicherung verwenden. Es gibt keine automatische Downmigration. Alte Entwürfe ohne diese Hülle bleiben in 0.12.1 lesbar und werden beim Update nicht umgeschrieben. `maintenance.py` bietet für Entwickler bei gestoppter App zusätzlich geprüfte SQLite-Snapshots, Restore und Schema-1→2-Rollback; Details und ausführbare Tests stehen in `docs/raumstudio/ARCHITECTURE.md`. Keine Restore-HTTP-Route und keine automatische Rücknahme fremder HA-Daten.

## Technische Grenzen

Deklarierte Architekturen: amd64 und aarch64. Python-Baseimage und Pillow-Wheels sind gepinnt. ARM-Prüfungen auf einem x86-Testhost verwenden ausdrücklich Emulation. Reales privates HA-Ingress, physische Touchgeräte, HA-Backup/Restore und persönliche Abnahme bleiben getrennt von lokalen Tests und Imageprüfungen. Kein öffentlicher Hostport, kein Host-Netzwerk, keine zusätzliche Hostinstallation erforderlich.

Bei sehr vielen oder langsam antwortenden HA-Dashboards kann der einmalige Katalogabruf länger dauern und andere Anfragen vorübergehend verzögern. Ein abgebrochener Abruf verändert keine HA-Daten. Die aktuelle Version besitzt noch kein übergreifendes Zeitbudget für den gesamten Katalogabruf.
