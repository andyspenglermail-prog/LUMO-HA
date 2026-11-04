# Änderungen

## 0.1.0-dev.5 – privater, nicht ausgelieferter Textpilot-Kandidat

- „LUMO fragen“ innerhalb des Gerätebuchs: Frage und ausdrücklich ausgewählte
  aktuelle Gerätemetadaten, einzelne Funktionen und zugehörige Belege. Standard:
  keine Auswahl. Exakter Sendeumfang ist prüfbar, keine Ganzbuchübertragung.
- Reale relative API-Anbindung über den App-Server an eine fest konfigurierte
  HTTPS-Brücke, geprüftes Zertifikat und Hostname, kein direkter Browserzugang.
  Leere Benutzerfreigabe und leere Brückeneinstellungen sperren Modelloperationen.
- Begrenzter Textvertrag mit Gespräch, idempotenten Anfragekennungen, Status,
  ausdrücklichem Stopp-/Löschwunsch und wörtlicher Textausgabe. Keine Geräteaktion.
- Fehler halten den Zustand unbekannt; keine automatische neue KI-Anfrage.
  8 KiB Text / 16 KiB Anfrage werden abgewiesen statt still gekürzt.
- Lokale TLS-/Core-/Chromium-Prüfung ist keine native Modell- oder HA-Abnahme.
- Gezielte Reparatur des belegten 0600-Optionsfehlers: kurzer Root-Bootstrap
  liest nur die feste eigene Optionsdatei und gibt vor Listener/Netzwerk alle
  UIDs/GIDs auf 65532 und alle wirksamen Fähigkeiten ab. Keine Rechteänderung
  an Optionen, kein Ersatztransport und kein Root-Webbetrieb. Docker-Healthcheck
  deaktiviert, damit kein wiederkehrender Root-Helfer entsteht; `/health` bleibt.
- Jede beobachtete Optionsänderung sperrt KI bis zum bewussten App-Neustart;
  Dateimetadaten werden vor Zulassung und Ergebnisfreigabe geprüft.
- Echte lokale Kopplung an neue Host-Brücke, Journal/Core/Executor und TLS;
  nur SDK/Ingress sind Fixtures. 64 KiB rohes Antwort-JSON bei weiterhin
  8 KiB dekodiertem UTF-8-Text, keine Trunkierung oder zusätzlichen Header.
- Unabhängiges Review, gepinnter Image-Build und native HA-/Modellabnahme offen.

## 0.1.0-dev.4

- Leeres Offline-Gerätebuch als zweite Seite neben dem unveränderten Raumstudio-Kern.
- Sichtbare, tastaturbedienbare Navigation mit relativen Seitenpfaden für Ingress.
- Geräte und Funktionen manuell dokumentieren, bearbeiten, suchen und per JSON
  importieren/exportieren; keine vorinstallierte Inventur und keine Belege.
- Optionale browserlokale Arbeitskopie standardmäßig aus. Kein gemeinsames Backend;
  JSON-Exporte eigener Metadaten sind unverschlüsselt.
- Beide Seiten werden vor Serverstart begrenzt eingelesen und über dieselbe
  Ingress-Prüfung geschützt. Health bleibt öffentlich; keine zusätzlichen Rechte.
- Keine Hausverbindung, KI, aktive Beobachtung, Dashboardgenerierung oder Geräteaktion.

Lokale Kandidatenprüfung ist kein Image-Build, keine Veröffentlichung und keine
native HA-/Clientabnahme. Updates erfolgen erst nach gesonderter Freigabe über HA.

## 0.1.0-dev.3

- Separate öffentliche HA-Repositoryquelle mit direktem App-Ordner.
- Normale Installation über den HA-App-Store, ohne Terminal-Installer.
- Unterstützung für `aarch64` und `amd64`.
- Server, Oberfläche, Dockerfile und Laufzeitberechtigungen unverändert zur
  zuvor isoliert geprüften Offline-Testhülle.
- Dokumentation auf die öffentliche Testapp begrenzt.

Keine echte KI- oder Hausverbindung. Eine erfolgreiche Repositoryabfrage ersetzt
keine tatsächliche HA-/Ingress-/Clientabnahme.
