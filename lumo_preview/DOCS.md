# LUMO Raumstudio – Offline-Test

## Bedienung

Die App zeigt ausschließlich synthetische Beispielräume und Beispielwerte.
Mit „Beispielauswahl“ lassen sich Karten erzeugen; Informationen können einzeln
abgewählt werden. Ein Raumwechsel setzt die Auswahl zurück.

„Entwurf herunterladen“ speichert einen JSON-Raumentwurf. Dieser ist als reine
Vorschau markiert, keine HA-Dashboardkonfiguration und kein Installationspaket.
Nicht als Lovelace-Dashboard importieren.

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
privaten Benutzerdaten und keine schreibenden Serverfunktionen.

## Prüfung in HA

Nach Installation und Start die Weboberfläche über HA öffnen. Ein App-Status
„gestartet“ allein beweist noch keinen gesunden Container oder funktionierenden
Ingress. Oberfläche, Raumwechsel und tatsächlichen JSON-Download auf dem eigenen
Client prüfen. Das lokale Health-Endpunkt meldet keine Benutzer- oder Hausdaten.

Bei einem Fehler kurze Meldung und App-Version notieren. Keine Zugangsdaten oder
ungekürzten privaten Logs veröffentlichen. Bei unklarem Installationszustand keine
automatischen Wiederholungen und keine pauschalen Löschaktionen durchführen.

## Stoppen und Entfernen

Nur diese App über ihre HA-App-Seite stoppen oder deinstallieren. Das Paket legt
keine HA-Entitäten, Automationen, Dashboards oder Backendschlüssel an. Eventuell
vorhandene andere Testinstanzen und deren Daten nicht ungeprüft entfernen.
