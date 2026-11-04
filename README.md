# LUMO – Home Assistant Test-Apps

**LUMO – dein Zuhause denkt mit.**

Öffentliche Repositoryquelle für die **LUMO Raumstudio (Offline-Test)** App.
Entwicklungsstand, kein fertiger KI-Hausassistent.

## Was die Testapp kann

- Zwei synthetische Beispielräume anzeigen.
- Einzelne Beispielinformationen auswählen und Vorschaukarten erzeugen.
- Einen als reine Vorschau gekennzeichneten JSON-Raumentwurf herunterladen.
- Über die Seitennavigation das **Gerätebuch** öffnen: leer starten, Geräte und
  Funktionen manuell dokumentieren, suchen, bearbeiten und JSON importieren/exportieren.

**Keine echte KI, Hausdaten, Geräteaktionen oder Sprachfunktion.**
Der JSON-Entwurf ist keine importierbare HA-Dashboardkonfiguration.

## Repository in Home Assistant hinzufügen

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
- Die App läuft als Nicht-Root-Benutzer. Das Raumstudio verwendet synthetische
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
