# LUMO Raumstudio – Offline-Test

## Bedienung

Die App zeigt ausschließlich synthetische Beispielräume und Beispielwerte.
Mit „Beispielauswahl“ lassen sich Karten erzeugen; Informationen können einzeln
abgewählt werden. Ein Raumwechsel setzt die Auswahl zurück.

„Entwurf herunterladen“ speichert einen JSON-Raumentwurf. Dieser ist als reine
Vorschau markiert, keine HA-Dashboardkonfiguration und kein Installationspaket.
Nicht als Lovelace-Dashboard importieren.

## Gerätebuch: leer und offline

Die sichtbare Seitennavigation wechselt zwischen **Raumstudio** und **Gerätebuch**.
Beide Seiten bleiben unter dem Ingress-Zugang von Home Assistant. Das Gerätebuch
startet ohne Geräte und ohne Belege; es lädt keine Hausinventur nach.

„Gerät anlegen“ dokumentiert ein physisches Gerät. „Funktion zuordnen“ hält
Funktionsraum, Software-Komponente, HA-Entität und Verdrahtung getrennt fest.
Quellen und Änderungsgründe gehören zur Dokumentation. Bearbeiten, Suchen und
Filtern erfolgen ausschließlich im Browser. Ein Beleg ist keine Authentifizierung,
kein Nachweis einer aktuellen Prüfung und keine Aktionsfreigabe. Hypothesen sind
unbestätigt; Lernen ist nicht aktiv. Es werden keine Dashboards erzeugt.

„JSON exportieren“ lädt validierte Metadaten herunter. **Exporte sind unverschlüsselt**
und können sensible Haus-Metadaten enthalten. Keine Zugangsdaten eintragen und
eigene JSON-Dateien nicht ungeprüft veröffentlichen.

„JSON importieren“ zeigt zuerst eine Vorschau. Erst nach „Vorhandenes Gerätebuch
vollständig ersetzen“ und „Gerätebuch ersetzen“ wird der aktuelle Inhalt ersetzt,
nicht zusammengeführt. Vorher gegebenenfalls exportieren. Abbruch und ungültige
Dateien lassen den aktuellen Inhalt unverändert. Die Dateigrenze beträgt 1 MiB.

„Lokal speichern“ ist **standardmäßig aus**. Ohne Auswahl gehen Änderungen beim
Neuladen, Seitenwechsel oder Schließen verloren; vorher JSON exportieren.
Die optionale Arbeitskopie liegt nur im Browserprofil unter dem jeweiligen
Ingress-Seitenpfad. Eine früher bewusst aktivierte Kopie kann beim Wiederöffnen
statt des leeren Ausgangsbuchs geladen werden. Andere Browser/Benutzer erhalten
sie nicht; ein geänderter Ingress-Pfad kann eine andere lokale Kopie bedeuten.
Ausschalten entfernt nur diese lokale Kopie und lässt die geöffnete Dokumentation
erhalten. Das ist kein gemeinsames Backend, keine verschlüsselte Ablage und keine
verlässliche Sicherung. Der Server speichert keine eingegebenen Metadaten.

## Keine Verbindung zum Haus oder Modell

Diese Version besitzt keinen Livechat, keine Hausdatenanbindung und keine
Geräteaktionen. Sie übernimmt keine persönlichen Erinnerungen oder Gespräche.
Es gibt keine Hintergrundbeobachtung und keine Audiofunktion.

## Berechtigungen

Die App verlangt weder Home-Assistant-/Supervisor-API-Rechte noch Host-Netzwerk,
Host-Ports, Geräte oder Mounts. Startmodus ist `manual`. Die Anwendung läuft als
UID/GID `65532`. Die Plattform kann einen eingeschränkten technischen Token
injizieren; diese Anwendung liest, verwendet oder übermittelt ihn nicht.

Ingress-Anfragen müssen vom vorgesehenen Proxy kommen und eine einzelne gültige
Benutzerkennung tragen. `panel_admin: true` begrenzt die Seitenleistensichtbarkeit,
ist aber keine serverseitige Administratorrollenprüfung. Die App enthält keine
vorinstallierten privaten Benutzerdaten und keine schreibenden Serverfunktionen.
Manuell eingetragene Daten bleiben im Browser beziehungsweise im eigenen Export.

## Prüfung in HA

Nach Installation und Start die Weboberfläche über HA öffnen. Ein App-Status
„gestartet“ allein beweist noch keinen gesunden Container oder funktionierenden
Ingress. Oberfläche, Raumwechsel und tatsächlichen JSON-Download auf dem eigenen
Client prüfen. Das lokale Health-Endpunkt meldet keine Benutzer- oder Hausdaten.
Zusätzlich die Navigation in beide Richtungen, den leeren Gerätebuchstart und
einen eigenen JSON-Export/-Import prüfen. Lokale Fixture-/Chromium-Tests ersetzen
weder einen tatsächlichen Image-Build noch die native HA-/Clientabnahme.

Bei einem Fehler kurze Meldung und App-Version notieren. Keine Zugangsdaten oder
ungekürzten privaten Logs veröffentlichen. Bei unklarem Installationszustand keine
automatischen Wiederholungen und keine pauschalen Löschaktionen durchführen.

## Stoppen und Entfernen

Nur diese App über ihre HA-App-Seite stoppen oder deinstallieren. Das Paket legt
keine HA-Entitäten, Automationen, Dashboards oder Backendschlüssel an. Eventuell
vorhandene andere Testinstanzen und deren Daten nicht ungeprüft entfernen.
