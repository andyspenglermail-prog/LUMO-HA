# Änderungen

## 0.12.0 – Auftrag 01, neuer Raumstudio-Kandidat

- Eigenständige App `lumo_raumstudio`, keine Änderung oder Migration bestehender Apps.
- Deutsche Dashboardverwaltung mit vier Schritten und ehrlichen Übergabeseiten für Schritte 2–4.
- Serverpersistenz, HA-Benutzereigentum, Transaktionen und Revisionskonflikte.
- Eigene persistente Hintergrundbilder, unmittelbare Vorschau und nachgewiesene interne native Hintergrundabbildung.
- Rein lesender HA-Dashboardimport mit tatsächlicher Administratorprüfung, präziser Unterstützungsprüfung und atomarer Ablehnung statt stillem Teilimport.
- Kaltbackup-Konfiguration, geprüfter SQLite-Restore, Schemaführung und getesteter Migrationsrückweg.
- Neue isolierte Backend-, Wire-/HTTP-, Browser- und Original-Frontendtests; keine produktive HA-Operation.

Image-/privates Ingress-Gate, Veröffentlichung und persönliche Abnahme bleiben getrennte Schritte.
