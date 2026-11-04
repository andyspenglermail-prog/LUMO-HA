# Änderungen

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
