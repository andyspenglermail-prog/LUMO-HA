# LUMO Data · 0.6.0-devices.2

LUMO ist ein Home-Assistant-Dashboard-Designer. Dieser Entwicklungsstand
verbindet den Designer generisch mit Home Assistant. Neben echten Zustandswerten
sind bewusst ausgelöste An/Aus-Aktionen für unterstützte Gerätefunktionen möglich.
Er ist nicht selbst das fertige native HA-Dashboard.

## Bestehende LUMO-Data-App aktualisieren

Im bereits eingebundenen LUMO-Repository im Store-Menü **Nach Updates suchen**
ausführen. Anschließend die bereits installierte **LUMO Data** aktualisieren.
Der Slug bleibt `lumo_data`; der neue Name lautet **LUMO Data · Geräte & Bedienung**.
Keine Deinstallation und keine zweite LUMO-Data-Installation erforderlich.
Die bestehende `lumo_preview` wird weder ersetzt noch umkonfiguriert.

Falls das Repository noch fehlt, unter **Einstellungen → Apps → App-Store →
Menü ⋮ → Repositories** `https://github.com/andyspenglermail-prog/LUMO-HA`
hinzufügen. Ältere HA-Oberflächen nennen Apps noch Add-ons.

## Einrichtung

1. Die bestehende LUMO-Data-App aktualisieren; bei Erstnutzung installieren.
   Die Veröffentlichung allein startet oder installiert nichts. Die bisherigen
   Konfigurationsfelder bleiben erhalten.
2. In ihrer Konfiguration `allowed_user_ids` mit der eigenen HA-Benutzer-ID
   befüllen. Die Benutzer-ID steht in der HA-Benutzerverwaltung bei aktivem
   erweitertem Modus. Gemeint ist die ID, nicht Anzeigename oder Benutzername.
3. `enabled` bewusst auf `true` setzen. Mit `false` bleiben Datenabrufe und
   Schaltaktionen gesperrt. Freigegebene Benutzer können in dieser Version
   unterstützte Funktionen im Bedienmodus ausdrücklich schalten.
4. `allowed_entity_patterns` bei Bedarf eingrenzen, z. B. `sensor.*`.
   Eine leere Erlaubnisliste lässt alle nicht ausgeschlossenen Entitäten zu.
   `denied_entity_patterns` kann zusätzliche Ausschlüsse enthalten.
5. Konfiguration speichern, App starten und **Weboberfläche öffnen** wählen.
6. Im Designer zunächst **Bestand laden**, einen Raum und ein Gerät auswählen.
   Unter **Bearbeiten** die gewünschten Funktionen markieren und direkt
   **Änderungen übernehmen** wählen. Der zusätzliche Knopf **Gewählte Funktionen
   verknüpfen** ist nur nötig, wenn die Unterkacheln schon vor dem Übernehmen
   weiter bearbeitet werden sollen.
   Aktuelle Werte werden für die ausgewählten Funktionen abgerufen; bei Bedarf
   **Werte aktualisieren** bzw. **Verlauf laden** verwenden.
   Es werden keine Hausdaten mitgeliefert oder automatisch vorbelegt.

Nach einer Optionsänderung die App neu starten: Eine erkannte Änderung sperrt
weitere Datenabrufe und Bedienaktionen bis zum Neustart. Keine HA-Tokens in Browserfelder eintragen.
Die App erhält ihren Zugriff intern über den Supervisor und prüft zusätzlich
Ingress und die freigegebenen Benutzer-IDs. Direkter Portzugriff ist nicht vorgesehen.

## Funktionsumfang und Grenzen

- Geräteorientierte Auswahl, horizontale Werkzeugleiste und zusammengehörige
  Unterkacheln. Funktionen ohne Gerätezuordnung bleiben auswählbar.
- Neutrales Editor-UI, drei vorhandene Ausgabestile, veränderbare Kachelmaße,
  Mehrfachbindungen und die vorhandenen Designer-/Analysekacheln.
- Bereiche, Geräte, Entitäten, aktuelle Zustände und begrenzte historische
  Abfragen aus der laufenden HA-Instanz. Werteabrufe folgen der Funktionsauswahl
  oder einer ausdrücklichen Aktualisierung; kein ständiges Hintergrundpolling.
- Fehlende oder nicht verfügbare Zustände und leere Historien werden angezeigt;
  vorhandener Recorder-Verlauf wird weder erzeugt noch garantiert.
- Historische Einheiten bleiben an ihren Beobachtungen. Gemischte oder unbekannte
  Einheiten werden nicht still als gemeinsame numerische Reihe ausgegeben.
- Im Modus **Gestalten** werden keine Gerätebefehle ausgelöst. Im Bedienmodus
  gibt es für unterstützte und verfügbare `light`, `switch` und `input_boolean`
  explizite An/Aus-Aktionen. Tatsächliche HA-Services und der aktuelle Zustand
  bestimmen die Bedienbarkeit. Nicht unterstützte Domänen bleiben Werteanzeige.
- Jede Aktion betrifft genau eine freigegebene Entität. Kein generischer
  Serviceproxy, keine automatische Wiederholung. Ein angenommener Befehl ist
  noch keine bestätigte Zustandsänderung; fehlende Bestätigung bleibt sichtbar.
- Keine Schloss-/Alarm-/Heizungs-/Rollladenaktionen in diesem Schaltumfang.
  Kein Speichern produktiver Dashboards in HA und keine KI.
- Noch kein vollständiger nativer Dashboardexport. Berechnete Runtime-Kennzahlen
  sind semantisch noch nicht allgemein freigegeben.
- Kein dauerhaftes Speichern von Entwürfen durch diesen Backendstand zugesagt.
- Native Installation, echter Ingress, Touch- und qualitative Designabnahme
  müssen am eigenen Zielsystem noch geprüft werden.

## Plattform und Nachweisgrenzen

Zielarchitekturen sind `amd64` und `aarch64`. Lokale Prüfungen verwenden
synthetische HA-Gegenstellen und keine echten Gerätebefehle. Sie ersetzen
keine Bestätigung der physischen Gerätewirkung am eigenen Zielsystem.
Die App bleibt ein Entwicklungsstand; native Ausgabe und physische
Touch-/Designabnahme sind davon getrennt.
