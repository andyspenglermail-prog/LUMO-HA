# Änderungen

## 0.12.1 – Verlustfreie HA-Übernahme in Schritt 1

- Update derselben App und desselben Slugs `lumo_raumstudio`.
- Verfügbare HA-JSON-Konfiguration vollständig übernehmen: Custom Cards, Templates, Styles, unbekannte Schlüssel, ungewöhnliche Typen und Strategies bleiben Daten. Keine Ausführung und keine Ressourcen-URL-Abfragen.
- Server hält das Original unverändert. Nur ausdrücklich autorisierte bestehende Textfelder unterstützter Elemente können revisionsgebunden geändert werden; alle übrigen Pfade und Listenreihenfolgen bleiben erhalten.
- Klarer Importbericht, einklappbare technische Details und getrennte Ressourcen-Momentaufnahme aus festem `lovelace/resources/list`. Nicht verfügbar bleibt unbekannt; registriert bedeutet nicht funktionsgeprüft.
- Echter JSON-Download über die Oberfläche, ohne Rundung großer Zahlen im Browser. Verwaltungsname und native Titel bleiben unabhängig; bestehende Settings wirken bei neuen Importen ausschließlich als gekennzeichnete lokale Vorschau/Verwaltung.
- Alter Entwurfsbestand und interne Legacy-Hintergrundabbildung bleiben kompatibel. Duplikat, Neustart, Backup und Restore bewahren auch geschützte Daten und Änderungen.
- Synthetische TDD-, HTTP- und Browserregressionen; keine privaten Konfigurationen im Repository. Keine HA-Schreibroute, Veröffentlichung oder Installation durch diese Änderung. Schritte 2–4 unverändert.

## 0.12.0 – Auftrag 01, neuer Raumstudio-Kandidat

- Eigenständige App `lumo_raumstudio`, keine Änderung oder Migration bestehender Apps.
- Deutsche Dashboardverwaltung mit vier Schritten und ehrlichen Übergabeseiten für Schritte 2–4.
- Serverpersistenz, HA-Benutzereigentum, Transaktionen und Revisionskonflikte.
- Eigene persistente Hintergrundbilder, unmittelbare Vorschau und nachgewiesene interne native Hintergrundabbildung.
- Rein lesender HA-Dashboardimport mit tatsächlicher Administratorprüfung, präziser Unterstützungsprüfung und atomarer Ablehnung statt stillem Teilimport.
- Kaltbackup-Konfiguration, geprüfter SQLite-Restore, Schemaführung und getesteter Migrationsrückweg.
- Neue isolierte Backend-, Wire-/HTTP-, Browser- und Original-Frontendtests; keine produktive HA-Operation.

Image-/privates Ingress-Gate, Veröffentlichung und persönliche Abnahme bleiben getrennte Schritte.
