# LUMO Data · 0.5.0-data.1

LUMO ist ein Home-Assistant-Dashboard-Designer. Dieser Entwicklungsstand
verbindet den Designer generisch und ausschließlich lesend mit Home Assistant.
Er ist nicht selbst das fertige native HA-Dashboard.

## Im Home-Assistant-App-Store finden

Im bereits eingebundenen LUMO-Repository im Store-Menü **Nach Updates suchen**
ausführen. Anschließend nach **LUMO Data · Entwicklung · Read-only** suchen.
Die App ist ein neuer separater Eintrag, kein Updateknopf der alten Offline-App.
Die bestehende `lumo_preview` wird weder ersetzt noch umkonfiguriert.

Falls das Repository noch fehlt, unter **Einstellungen → Apps → App-Store →
Menü ⋮ → Repositories** `https://github.com/andyspenglermail-prog/LUMO-HA`
hinzufügen. Ältere HA-Oberflächen nennen Apps noch Add-ons.

## Einrichtung

1. Die separate App installieren. Installation und Start sind bewusste eigene
   Schritte; die Veröffentlichung allein startet oder installiert nichts.
2. In ihrer Konfiguration `allowed_user_ids` mit der eigenen HA-Benutzer-ID
   befüllen. Die Benutzer-ID steht in der HA-Benutzerverwaltung bei aktivem
   erweitertem Modus. Gemeint ist die ID, nicht Anzeigename oder Benutzername.
3. `enabled` bewusst auf `true` setzen. Mit `false` bleiben Datenabrufe gesperrt.
4. `allowed_entity_patterns` bei Bedarf eingrenzen, z. B. `sensor.*`.
   Eine leere Erlaubnisliste lässt alle nicht ausgeschlossenen Entitäten zu.
   `denied_entity_patterns` kann zusätzliche Ausschlüsse enthalten.
5. Konfiguration speichern, App starten und **Weboberfläche öffnen** wählen.
6. Im Designer zunächst **Bestand laden**, danach die gewünschten Entitäten
   zuordnen und **Werte aktualisieren** bzw. **Verlauf laden** verwenden.
   Es werden keine Hausdaten mitgeliefert oder automatisch vorbelegt.

Nach einer Optionsänderung die App neu starten: Eine erkannte Änderung sperrt
weitere Datenabrufe bis zum Neustart. Keine HA-Tokens in Browserfelder eintragen.
Die App erhält ihren Zugriff intern über den Supervisor und prüft zusätzlich
Ingress und die freigegebenen Benutzer-IDs. Direkter Portzugriff ist nicht vorgesehen.

## Funktionsumfang und Grenzen

- Neutrales Editor-UI, drei vorhandene Ausgabestile, veränderbare Kachelmaße,
  Mehrfachbindungen und die vorhandenen Designer-/Analysekacheln.
- Bereiche, Geräte, Entitäten, aktuelle Zustände und begrenzte historische
  Abfragen aus der laufenden HA-Instanz; ausschließlich manuell ausgelöste Lesezugriffe.
- Fehlende oder nicht verfügbare Zustände und leere Historien werden angezeigt;
  vorhandener Recorder-Verlauf wird weder erzeugt noch garantiert.
- Historische Einheiten bleiben an ihren Beobachtungen. Gemischte oder unbekannte
  Einheiten werden nicht still als gemeinsame numerische Reihe ausgegeben.
- Kein Serviceaufruf, keine Gerätesteuerung, kein Speichern in HA und keine KI.
- Noch kein vollständiger nativer Dashboardexport. Berechnete Runtime-Kennzahlen
  sind semantisch noch nicht allgemein freigegeben.
- Kein dauerhaftes Speichern von Entwürfen durch diesen Backendstand zugesagt.
- Native Installation, echter Ingress, Touch- und qualitative Designabnahme
  müssen am eigenen Zielsystem noch geprüft werden.

## Plattform und Prüfung

`amd64` und `aarch64`. Die unveränderten Runtime-Dateien entsprechen dem
korrigierten `0.5.0-data.1`-Kandidaten. 80 gezielte Regressionstests bestanden;
das gezielte unabhängige Nachreview der fünf Korrekturen war ohne Findings.
Images wurden für beide Architekturen gebaut. Start, Gesundheitsroute,
Ablehnung direkter Datenabfragen und Privilegienabgabe wurden in isolierten
Containern geprüft; der ARM64-Lauf war emuliert, nicht auf echtem ARM-Gerät.
Zur Store-Veröffentlichung wurde ausschließlich die Architekturdeklaration um
`aarch64` erweitert; Runtime-Code, Rechte und Opt-in-Vorgaben bleiben unverändert.
