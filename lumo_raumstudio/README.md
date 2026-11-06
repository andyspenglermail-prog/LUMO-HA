# LUMO Raumstudio

**Dein Zuhause denkt mit.** Eine eigenständige Home-Assistant-App für Deine Dashboard-Entwürfe.

Auftrag 01 umfasst ausschließlich Schritt **Dashboard**: Entwürfe erstellen, öffnen, umbenennen, unabhängig duplizieren, einstellen und bestätigt löschen. Hintergrundbilder und Einstellungen werden serverseitig unter Deinem HA-Benutzer gespeichert. Unterstützte vorhandene HA-Dashboards lassen sich rein lesend als unabhängige Kopie übernehmen.

Die vier Schritte bleiben sichtbar. Raum, Design & Display und Dein Raumentwurf sind ehrliche Übergabeseiten, keine bereits implementierten Raumeditoren. Keine Gerätebedienung, KI, Veröffentlichung oder HA-Schreibschnittstelle.

## Einstieg

Die App startet absichtlich ohne Freigabe. Öffne ihre Weboberfläche **über Home Assistant** und folge der Einrichtung in **DOCS.md**. Keine Zugangsdaten im Browser eingeben. Die kanonische Softwareversion steht in `config.json` und wird aus diesem Wert in der Oberfläche angezeigt.

## Prüfungen und Abnahme

Die technische Prüfbasis umfasst SQLite, HTTP, RFC6455, Browserbedienung und den Original-HA-Hintergrundrenderer. Die Prüfmatrix steht unter `docs/raumstudio/VERIFICATION.md`. Containerprüfungen, Repositorybereitstellung, tatsächliche private Installation und Andys persönliche Abnahme sind getrennte Nachweise. Die vorhandenen Apps `lumo_data` und `lumo_preview` werden weder ersetzt noch migriert. Diese neue App wird einmalig separat installiert; spätere Updates verwenden denselben Slug `lumo_raumstudio` und behalten ihr eigenes `/data`.
