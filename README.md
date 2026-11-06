# LUMO – Home Assistant Dashboard-Designer

## LUMO Data · 0.11.0-native.2

**Nur noch native HA-Dashboards.** Der freie Editor und die Ausgabeprofil-Auswahl
entfallen. Bestehende native Entwürfe/Backups bleiben erhalten. Das Ziel ist:
in LUMO gestalten und das entsprechende native Layout in HA verwenden.

### Ablauf

1. **Dashboard** auswählen oder neu beginnen. Bestehende lokale Entwürfe und
   unterstützte HA-Kopien öffnen direkt in **Dein Raumentwurf**.
2. **Raum** auswählen oder eine neue Raumansicht im Entwurf anlegen.
3. **Design & Display**: Zielanzeige und optionale CSS-Maße prüfen.
4. **Dein Raumentwurf**: Quellen hinzufügen, bearbeiten, gruppieren,
   verschieben/vergrößern, speichern, exportieren oder in HA anlegen.

Die native Sections-Geometrie wurde mit einem tatsächlichen UI-Export aus neun
Karten, zwei Überschriften und vier Abschnitten bei vier gleichen Inhaltsbreiten
gegen das offizielle HA-Frontend geprüft. Das ist Layouttreue im geprüften Profil,
nicht identische Theme-/Schrift-/Icon-Darstellung aller HA-Versionen. Frühere
Stilpräferenzen installieren oder exportieren weiterhin keine HA-Themes.

**Entwurfsmodus/Testmodus:** Im Designmodus ist ein dezentes Raster sichtbar;
Gestalten schaltet nicht. Im Testmodus bleiben Werte und Bedienung in derselben
Kachel, ohne Positions- oder Größensprung und ohne separaten Bedienbereich darunter.
Gewählte Bedien-Darstellungen zeigen ihre Hauptfunktionen direkt. Weitere Funktionen
und Status sind über ⋯ bzw. den Kacheltitel erreichbar; kleine Kacheln scrollen innen.
Verbunden sind das echte, fähigkeitsgeprüfte Geräteaktionen. Parameteränderungen
allein senden nichts: ausdrücklich **Senden / ✓** drücken. Unklare Befehle werden
nicht wiederholt. Zusätzliche Testfunktionen ändern nicht die exportierte Darstellung.

**Dashboard anlegen** neben Exportieren fragt Titel, originales HA-Seitenleistensymbol,
URL-Name, Nur Administratoren und In der Seitenleiste anzeigen ab. Erst die ausdrückliche
Bestätigung legt ein neues Storage-Dashboard an. Aktive Adminidentität wird geprüft;
bestehende Pfade werden abgewiesen. Metadaten und Konfiguration werden zurückgelesen.
Bei Teilfehlern kann ein bereits angelegtes Dashboard zurückbleiben: prüfen statt
blind erneut versuchen. Keine automatische Löschung oder Aktualisierung bestehender
Dashboards. HA bietet hierfür keine atomare Create-and-Save-Transaktion gegen
parallele externe Schreiber.

**Speichern** bleibt Browserspeicherung; **Exportieren** lädt YAML/JSON herunter.
HA-Import ist weiterhin eine ausdrückliche lokale Kopie des unterstützten Subsets,
keine universelle verlustfreie Bearbeitung beliebiger Dashboards. Nicht unterstützte
Inhalte werden abgelehnt statt still entfernt. Aktuelle Quellen stammen zur Laufzeit
aus HA; ohne Verbindung gibt es keinen Demoersatz.

### Update derselben App

Im bestehenden App-Repository nach Updates suchen und **LUMO Data** aktualisieren,
danach die Weboberfläche neu öffnen. Slug `lumo_data`, Optionen und Berechtigungen
bleiben erhalten; keine zweite App und keine automatische Installation.
Die separate ältere Offline-App bleibt unverändert.

[Einrichtung, Bedienung und genaue Grenzen](lumo_data/DOCS.md).
AMD64 und ARM64/aarch64; Start manuell, Zugriff zunächst deaktiviert.
Tests nutzen synthetische HA-Gegenstellen, nicht produktive Geräte. Installierte
HA-Kompatibilität, physischer Touch und qualitative Nutzerabnahme bleiben separat.

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
