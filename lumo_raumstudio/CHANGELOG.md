# Änderungen

## 0.14.0 – Auftrag 03: Design & Display

- Drei eigenständige, auf die Vorschau begrenzte Profile: LUMO Noir Luxury, Soft Ivory Premium und Smart Clean. Katalog mit zehn Kategorien und genau 27 ausdrücklich geplanten, gesperrten Profilen.
- Tatsächliche gespeicherte Raumreferenzen mit Runtime-Zuständen, sichtbarer Frische und geschützten nativen Inhalten. Keine Geräteaktionen, Templates oder Custom-Card-Ausführung.
- Individuelle Farben, Kartenmaterial, Rundung, Schatten, Systemtypografie, Dichte, Einzelreset und Kontrastprüfung. Hintergrund bleibt in Schritt 1; eigene native Hintergründe haben Vorrang, externe/komplexe Quellen werden nicht geladen.
- Sechs Mehrfach-Zielklassen, validierte CSS-Viewports, Ausrichtung und getrennte Hardware-/DPR-/Eingabeabsichten. Echter Spalten-Reflow, expliziter Fitzoom und 1:1-Touchprüfung.
- Optionales owner-/CAS-gebundenes Designoverlay, bestätigtes Readback, sichere Dirtyguards, neue Browserprozesse und SQLite-Backup/Restore. Bestehende native Exporte und RoomPlans unverändert.
- Separater Theme-Mappingdownload mit granularer Fähigkeitsmatrix und tatsächlichen berechneten Eigenschaften originaler gepinnter HA-Komponenten. Kein Step4-Dashboardgenerator, keine Installation oder HA-Publikation. Vollständige visuelle HA-Parität wird nicht behauptet.

## 0.13.0 – Auftrag 02: Raum

- Echte Runtime-Registry-/Zustandslesung, effektive Bereiche mit Entity-Vorrang und getrennte Herkunft. Fehlende, deaktivierte, gerätelose und reine Zustandsentitäten bleiben ehrlich sichtbar. Same-user-Leserechte ohne falsches Adminerfordernis; abweichender Supervisor-User ist kein Rechtebeweis.
- Dashboardbezogene persistente Raumansichten: erstellen, Titel/Icon/Sichtbarkeit, Reihenfolge, Duplikat, bestätigtes Entfernen. Geräte und stabile Entityreferenzen getrennt; raumübergreifende Auswahl, Suche/Domainfilter, sichtbare Mehrfachauswahl, Rückgängig und Dirty/CAS-Schutz.
- Drei Desktopspalten und sequenzielle Tablet-/Telefonpanels; tatsächliche Werte werden alle30s/manuell neu gelesen, fehlgeschlagene Abrufe als veraltet markiert. Keine Datenattrappen.
- Eng begrenzte HA-Bereichskorrektur: anfragender Admin, konkrete kurzlebige Vorschau, Bestätigung, frischer Stale-Vergleich, einmaliger Versand, tatsächliches Readback, kein Retry. Keine Geräteaktionen oder beliebiger Proxy. Echte Schreibabnahme ohne Testobjekt bleibt offen.
- Optionale roomPlan-Hülle ohne DB-Umschreiben beim Start. Native Quellen, Step1-Views, Importledger und Bilder bleiben erhalten; Raumplanung schreibt den nativen Export nicht um. Backup-/Upgradeprüfung mit echtem0.12.1-Store.
- Isolierte RED/GREEN- und tatsächliche Browser→Backend→RFC6455-Tests; bestehende65 Methoden bleiben aktiv. Keine Veröffentlichung, Installation, physische Geräte- oder Nutzerabnahme durch diese Quelländerung. Schritte3/4 bleiben außerhalb des Auftrags.

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
