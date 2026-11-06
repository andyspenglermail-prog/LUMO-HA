# LUMO Raumstudio · 0.12.1

**Dein Zuhause denkt mit.** Eine eigenständige Home-Assistant-App für Deine Dashboard-Entwürfe.

Auftrag 01 umfasst ausschließlich Schritt **Dashboard**: Entwürfe erstellen, öffnen, umbenennen, unabhängig duplizieren, einstellen und bestätigt löschen. Hintergrundbilder und Einstellungen werden serverseitig unter Deinem HA-Benutzer gespeichert. Alle sicher begrenzten, verfügbaren HA-JSON-Konfigurationen lassen sich rein lesend als unabhängige Kopie übernehmen: auch Custom Cards, Templates, Styles und Strategies. Unbekannte Daten sind geschützt, nicht abgelehnt. Bericht, gezielte vorhandene Textfeldbearbeitung und verlustfreier JSON-Download bleiben in Schritt 1.

Die vier Schritte bleiben sichtbar. Raum, Design & Display und Dein Raumentwurf sind ehrliche Übergabeseiten, keine bereits implementierten Raumeditoren. Keine Gerätebedienung, KI, Veröffentlichung oder HA-Schreibschnittstelle.

## Einstieg

Die App startet absichtlich ohne Freigabe. Öffne ihre Weboberfläche **über Home Assistant** und folge der Einrichtung in **DOCS.md**. Keine Zugangsdaten im Browser eingeben. Die kanonische Softwareversion steht in `config.json` und wird aus diesem Wert in der Oberfläche angezeigt.

## Prüfungen und Abnahme

Die technische Prüfbasis umfasst SQLite, HTTP, RFC6455, Browserbedienung und den Original-HA-Hintergrundrenderer. Die Prüfmatrix steht unter `docs/raumstudio/VERIFICATION.md`. Containerprüfungen, Repositorybereitstellung, tatsächliche private Installation und Andys persönliche Abnahme sind getrennte Nachweise. Die vorhandenen Apps `lumo_data` und `lumo_preview` werden weder ersetzt noch migriert. 0.12.1 ist ein Update derselben Raumstudio-App unter Slug `lumo_raumstudio` und behält ihr eigenes `/data`. Kein neues Parallelprojekt, keine Installation durch diese Quelländerung.
