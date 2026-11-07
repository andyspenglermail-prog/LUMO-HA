# LUMO Raumstudio · 0.14.1

**Dein Zuhause denkt mit.** Update derselben Home-Assistant-App `lumo_raumstudio`, kein neuer Slug.

Schritt **Dashboard** behält die serverseitige, benutzergetrennte Verwaltung, Bilder und verlustfreien HA-Import/JSON-Export. Unbekannte Karten, Templates, Styles, große Zahlen und native Reihenfolgen bleiben geschützt. Importierte Ressourcen werden nicht ausgeführt.

Schritt **Raum** liest Bereiche, Etagen, Geräte, das vollständige Entitätsregister und tatsächliche Zustände aus Home Assistant zur Laufzeit. Keine Beispieldaten oder privaten Snapshots im Produkt. Eigene Raumansichten lassen sich erstellen, benennen, mit Icon versehen, ausblenden, sortieren, duplizieren und bestätigt entfernen. Geräte und einzelne stabile Entitätsreferenzen können in mehreren Ansichten vorkommen, ohne ihre HA-Zuordnung zu verändern. Suche, Domainfilter, Auswahl passender Treffer, Rückgängig, ungespeicherte Eingaben und Konflikte sind integriert.

Die rechte Eigenschaftenspalte trennt HA-Struktur von lokaler Anzeige. Nur die gesonderte **HA-Bereichskorrektur** schreibt nach serverseitiger Prüfung der Rechte des anfragenden Administrators, konkreter Vorschau, ausdrücklicher Bestätigung und frischem Vergleich. Es gibt keine Geräteaktionen, Services, HA-Dashboard-Publikation, Bereichserstellung/-löschung oder beliebigen API-Proxy. Unklares Ergebnis wird nie automatisch wiederholt. Echte Schreibabnahme bleibt ohne freigegebenes Testobjekt offen.

**Design & Display** bietet drei tatsächlich unterschiedliche Profile, individuelle Stiloverrides, sechs Zielgeräteklassen und eine read-only Funktionsvorschau aus denselben gespeicherten Raumreferenzen. Der Editor bleibt neutral. Eigene Viewports führen zu echtem Reflow; Fitzoom und 1:1-Prüfung bleiben getrennt. Ein revisionsgebundenes Native-Theme-Sidecar bildet nachgewiesene Karten-/Header-Stile ab, ohne `compile_native` oder importierte Exporte umzuschreiben. Navigation, Inhaltsdichte und Zielraster sind ausdrücklich nur LUMO-Vorschau. **Dein Raumentwurf** bleibt die bisherige Übergabeseite; kein Schritt4-Authoring. Technischer Vertrag: `docs/raumstudio/STEP3.md`.

Optional eigene **Raumfotos** in Schritt 3: sichere vorhandene Bildbibliothek, Upload/Auswahl/Entfernen und stabile, separat gespeicherte Ansichtsbindung. Keine Änderung am globalen Hintergrund aus Schritt 1. Bei nur einer sichtbaren Ansicht bleibt die Überschrift ohne redundante Navigation; ausgeblendete gespeicherte Ansichten werden verständlich erklärt. Fotos sind LUMO-Vorschaugestaltung, nicht bereits native HA-Fotokarten.

## Einstieg

Über HA-Ingress öffnen. Standardmäßig ist Zugriff deaktiviert; Freigabe über `enabled` und `allowed_user_ids`. Keine Credentials oder Upstream-Adressen im Browser eingeben. Anleitung, Rechte, Bedienung und Sicherung in **DOCS.md**. Die kanonische Version in `config.json` wird im Header angezeigt.

## Prüfungen und Abnahme

`docs/raumstudio/STEP2.md` dokumentiert API, Modell, Quellen und R01–R25. `docs/raumstudio/VERIFICATION.md` beschreibt die bestehende und ergänzte Suite. Tests laufen mit realem Browser, tatsächlichem Backend/SQLite/CoreClient und isolierter synthetischer RFC6455-Gegenstelle. Parent-Livechecks, amd64/aarch64-Images, Veröffentlichung, tatsächliche Storeanzeige, Installation, physische Endgeräte und persönliche Abnahme sind getrennte Nachweise; Quelländerung ist keine Installation. `lumo_data` und `lumo_preview` bleiben unverändert.
