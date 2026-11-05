# LUMO – Home Assistant Test-Apps

## Update: LUMO Data · 0.9.0-designer.3

**Das native Profil ist jetzt wieder Raumstudio:** mit zentralem **Dein Raumentwurf**,
sichtbarem **Design & Display** und einer Raumauswahl aus dem geladenen HA-Bestand.
Die drei Vorschau-Styles und Displaygrößen wirken auf den Entwurf; die Werkzeuge
bleiben neutral. Raumwechsel erhalten die jeweiligen Entwürfe. Quellen aus
anderen Räumen bleiben ausdrücklich auswählbar.

**Echte Daten statt Demo:** Räume, Gerätezuordnungen, Entitäten und aktuelle Werte
kommen zur Laufzeit über die bestehende HA-Anbindung. Ohne Verbindung keine
Ersatzdaten; fehlende, unbekannte, nicht verfügbare und veraltete Werte sind sichtbar.
Die aktuelle Ansicht liest nur ihre gebundenen Quellen. Der HTTP-Fehlerfix bleibt erhalten.

Präsentationseinstellungen werden mit dem nativen Entwurf gespeichert und sind
rückgängig machbar. Sie sind Designer-Einstellungen, kein automatisch exportiertes
HA-Theme: Home Assistant bestimmt die endgültige native Darstellung.

**Update der bereits installierten LUMO-Data-App**, keine zusätzliche App.
Im App-Store-Menü nach Updates suchen und anschließend **LUMO Data** aktualisieren.
Der Slug `lumo_data` und die vier Konfigurationsfelder bleiben unverändert.
Der Anzeigename bleibt **LUMO Data · Geräte & Bedienung**.

### Weiterhin im nativen Designer enthalten

- Ausgabeprofil **Natives HA-Dashboard** im Raumstudio: strukturiertes Modell,
  mehrere Ansichten, direkte Funktionen und optionale geräteübergreifende Gruppen.
- Verschieben und Größenänderung, Fixierungen, Rückgängig/Wiederholen sowie
  ausdrückliche Browserspeicherung, Versionen und herunterladbare Backups.
- Validierter nativer YAML-/JSON-Export für unterstützte Funktionsbausteine.
  Keine automatische Veröffentlichung produktiver HA-Dashboards.
- Freies Vorschauprofil und drei Styles bleiben erhalten; Geräteinnenraster,
  Mehrfachkacheln und begrenzte Live-Zustandsaktualisierung sind enthalten.
- Gleicher Slug, gleiche Optionen und Berechtigungen; keine zweite App.
  Die Veröffentlichung installiert und startet nichts automatisch.

**Erster Test:** LUMO Data aktualisieren, Weboberfläche neu öffnen, **Bestand laden**
und **Natives HA-Dashboard** wählen. Unter **Raum aus HA-Bestand** deinen Raum
auswählen, Funktionen hinzufügen und in **Dein Raumentwurf** gestalten.
Installation, physischer Touch und qualitative Designabnahme bleiben am eigenen
Zielsystem zu prüfen. Es werden keine produktiven Dashboards automatisch verändert.

### Bisherige Funktionen bleiben erhalten

- Horizontale Raum-/Geräteauswahl statt linker Entitätenliste.
- Geräte hinzufügen; unter **Bearbeiten** Funktionen markieren und direkt
  **Änderungen übernehmen** wählen. Der zusätzliche Verknüpfen-Klick ist optional.
- Verständliche Funktionsrollen: Hauptbedienung, Anzeigen, Einstellungen und
  Diagnose. Tatsächliche Fähigkeiten werden für das ausgewählte Gerät gelesen.
- Echte Zustandswerte und passende Bedienelemente: Jalousien/Rollläden mit
  Position und unterstützter Neigung, Licht mit unterstützter Helligkeit und
  Farbtemperatur, Klima mit Sollwert/Betriebsart, Ventilatoren, Zahlen und Auswahl.
- Nur tatsächlich unterstützte Aktionen, Grenzen und Optionen. Einfache Schalter
  bleiben Ein/Aus; nicht dimmbare Lampen bekommen keinen erfundenen Dimmer.
- Bekannte Zustände und Klimabetriebsarten auf Deutsch, Lichthelligkeit in Prozent;
  Übernehmen und Abbrechen bleiben auch im schmalen Geräteeditor erreichbar.
- Explizite Bedienaktionen nur im Bedienmodus. Keine Befehle beim Gestalten,
  beim bloßen Verschieben eines Eingabereglers oder beim Auswählen einer Funktion.
- Verständliche Hinweise für deaktivierte oder fehlende Benutzerfreigaben.

Die bisherige Offline-App `lumo_preview` bleibt unverändert. Nicht unterstützte
Fähigkeiten werden sichtbar erklärt. Schlösser, Alarme, Scripts, Szenen und
beliebige Serviceaufrufe werden nicht freigegeben.

AMD64 und ARM64 (`aarch64`); Start manuell, Datenzugriff zunächst deaktiviert.
Einrichtung und Grenzen: [LUMO-Data-Anleitung](lumo_data/DOCS.md).
LUMO ist der Designer, nicht das fertige Dashboard. Der native Export deckt den
unterstützten Funktionsumfang ab, nicht sämtliche freien Styles, Analysebausteine,
Cockpits oder Formeln. Die Editorvorschau ist kein nativer HA-Live-Renderer.

## Bisherige Offline-Test-App (unverändert)

**LUMO – dein Zuhause denkt mit.**

Öffentliche Repositoryquelle für die **LUMO Raumstudio (Offline-Test)** App.
Entwicklungsstand, kein fertiger KI-Hausassistent.

## Was die Testapp kann

- Zwei synthetische Beispielräume anzeigen.
- Einzelne Beispielinformationen auswählen und Vorschaukarten erzeugen.
- Einen als reine Vorschau gekennzeichneten JSON-Raumentwurf herunterladen.
- Über die Seitennavigation das **Gerätebuch** öffnen: leer starten, Geräte und
  Funktionen manuell dokumentieren, suchen, bearbeiten und JSON importieren/exportieren.

**Privater Kandidat 0.1.0-dev.5; nicht veröffentlicht oder für HA freigegeben.**
„LUMO fragen“ ist im Gerätebuch integriert und lokal gegen echtes HTTPS, den
LUMO-Kern und Chromium geprüft; nur das native SDK und die Ingress-Identität
werden dabei durch ausdrücklich synthetische Fixtures ersetzt. Kein echter
Modellaufruf oder Hauszugriff gehört zu dieser Kandidatenprüfung.

**Reparierter privater Kandidat:** Ein kurzer Root-Bootstrap liest ausschließlich
die feste eigene Supervisor-Optionsdatei (0600), ohne ihre Rechte zu ändern.
Vor jedem Listener/Netzzugriff werden alle UIDs/GIDs auf 65532 gesetzt,
Zusatzgruppen entfernt und wirksame Fähigkeiten abgegeben; die Web-App läuft
anschließend ausschließlich als Nicht-Root. Jede beobachtete Optionsänderung
sperrt KI bis zum App-Neustart. Keine zusätzlichen API-Rechte oder Secretkanäle.
Die echte neue Host-Brücke mit SQLite-Journal wurde lokal gekoppelt geprüft.
Unabhängiges Review, Image- und native HA-/Modellabnahme stehen weiterhin aus.
Nicht als bereits abgenommene HA-KI installieren.
Der JSON-Entwurf bleibt keine importierbare HA-Dashboardkonfiguration.

## Repository in Home Assistant hinzufügen – erst nach separater Freigabe

Voraussetzung: Home Assistant OS mit App-Store und Architektur `aarch64` oder `amd64`.

1. **Einstellungen → Apps → App-Store → Menü ⋮ → Repositories** öffnen.
2. Diese Repository-URL hinzufügen:

   `https://github.com/andyspenglermail-prog/LUMO-HA`

3. **LUMO Raumstudio (Offline-Test)** auswählen.
4. Nach Prüfung eventuell vorhandener älterer Testinstanzen **Installieren** und anschließend **Starten** wählen.
5. **Weboberfläche öffnen** und die Beispielauswahl sowie den JSON-Download testen.
   Über **Gerätebuch** zur zweiten Seite wechseln; **Raumstudio** führt zurück.

Bei einer bereits vorhandenen Instanz erfolgt ein später freigegebenes Update
normal über die Repositoryaktualisierung und **Aktualisieren** auf der HA-App-Seite.
Dieser Quellstand allein installiert, veröffentlicht oder aktualisiert nichts.

Kein Terminal, kein Einfügen von Code und kein GitHub-Token erforderlich.
Der Supervisor baut die App aus diesem Repository. Dabei muss das fest gepinnte
öffentliche Python-Basisimage erreichbar oder bereits im Cache sein.

## Grenzen

- Manueller Start; keine automatische Aktivierung durch das Paket.
- Nur Ingress, keine veröffentlichten Host-Ports oder angeforderten Host-Mounts.
- Kein angeforderter Home-Assistant-/Supervisor-API-Zugriff, keine Modellschlüssel.
- Nach dem begrenzten Root-Bootstrap läuft die App als UID/GID65532. Das Raumstudio verwendet synthetische
  Beispiele; das Gerätebuch wird ohne Geräte oder Belege ausgeliefert.
- Gerätebuchänderungen bleiben zunächst nur in der geöffneten Seite. „Lokal
  speichern“ ist standardmäßig aus und aktiviert nur eine browserlokale Arbeitskopie,
  keinen gemeinsamen Hauswissensspeicher und keine verlässliche Sicherung.
- JSON-Exporte eigener Metadaten sind unverschlüsselt und können sensible Angaben
  enthalten. Keine Zugangsdaten eintragen oder private Dateien veröffentlichen.
- Quellcodeprüfung, Containerlauf und tatsächliche HA-/Clientabnahme sind getrennte Nachweise.
- Bei abgebrochenen früheren Installationsversuchen zuerst den Zustand prüfen; nicht blind erneut installieren oder Dateien löschen.

Weitere Bedien- und Berechtigungsdetails: [App-Dokumentation](lumo_preview/DOCS.md).
Keine Zugangsdaten, Hausinventuren oder privaten Protokolle in öffentliche Issues stellen.
Eine Open-Source-Lizenz ist derzeit nicht festgelegt.
