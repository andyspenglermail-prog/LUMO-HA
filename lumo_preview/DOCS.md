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

## Begrenzter Textpilot „LUMO fragen“

Im Gerätebuch bleiben Dokumentation und Frage auf derselben Seite. Standardmäßig
ist **kein Gerät** für die KI ausgewählt. „Aktuelles Gerät … mitsenden“ wählt nur
das gerade sichtbare Gerät samt seinen Belegen. Funktionen müssen einzeln gewählt
werden; nur deren Belege kommen hinzu. Der aufklappbare Sendeumfang zeigt den
wirklichen kombinierten Text. Editor-Entwürfe erst bewusst speichern; offene
Formularwerte werden nicht ungefragt übernommen. Ohne Auswahl ist eine Frage
möglich, ausdrücklich ohne Geräte-/Hausdaten. Es gibt keinen Live-Hauszugriff,
keine persönliche Erinnerung, kein aktives Lernen in der App und keine automatische Buchänderung.
Die Datenverarbeitung durch den vom Betreiber gewählten Modellanbieter ist damit
nicht zugesichert; vor Freigabe dessen Datenschutzbedingungen prüfen.

Erst **„Auswahl bewusst an LUMO senden“** sendet. Frage, Datenkennzeichnung und
Metadaten dürfen zusammen maximal 8192 UTF-8-Bytes umfassen; die JSON-Anfrage
maximal 16384 Bytes. Zu große Inhalte werden klar abgewiesen, niemals gekürzt.
Antworten werden ausschließlich als wörtlicher Text dargestellt. Auch
Markdown-/HTML-Inhalt wird nicht ausgeführt. Vorschläge sind keine Freigaben.

Ein Gespräch enthält auch vorher bewusst gesendete Fragen/Antworten. Vor einem
anderen Kontext gegebenenfalls ausdrücklich **„Gespräch löschen“**. Das löscht
den Brückenverlauf, nicht das Gerätebuch. Bei Verbindungsverlust bleibt der
Zustand **unbekannt**. Keine automatische Wiederholung oder neue Anfragekennung.
„Gleiche Anfrage wiederholen“ benutzt exakt den gehaltenen Text und dieselbe
Kennung, selbst wenn das Fragefeld inzwischen bearbeitet wurde. Geht schon die
Gesprächsanlage ohne erhaltene Kennung verloren, wird keine erfundene Kennung
verwendet und keine weitere Anlage automatisch gestartet.

Statusabfragen betreffen nur den eigenen Lauf, laufen mit begrenztem Backoff und
enden bei Seitenwechsel/verborgener Seite. Bei Rückkehr ausdrücklich „Status
prüfen“. Das ist kein Anbieter-Stopp. „Stopp anfragen“ unterdrückt späte Texte,
beweist aber weder Anbieterende noch Kostenstopp. Unklare Zustände nicht durch
Neuladen oder neue Anfragen umgehen; Betreiberklärung kann erforderlich sein.

## Private Brückeneinstellungen und begrenzter Root-Bootstrap

Vorgesehene Supervisor-Optionen: `bridge_url` (fester HTTPS-Ursprung), `bridge_ca`
(öffentliche CA-PEM), `bridge_token` (dediziertes Passwortfeld) und
`allowed_user_ids` (ausdrücklich erlaubte Ingress-Kennungen). Alle Werte sind
standardmäßig leer; alle Modelloperationen sind dann gesperrt. Die eigene Kennung
wird im Panel gezeigt; es gibt weder Freigabe des ersten Benutzers noch pauschale
Freigabe aller Benutzer. Dieselben Kennungen müssen auch am Host erlaubt sein.
Keine Modellschlüssel oder allgemeinen Agenten-API-Token eintragen.

URL, CA und Brückentoken bleiben ausschließlich im Server. Der Browser verwendet
relative eigene Ingress-Anfragen, keine direkte Hostverbindung. Zertifikatskette
und Hostname müssen stimmen; keine Abschaltoption und keine Redirects. Fehler
geben keine privaten Details aus. Nach Optionsänderung werden Modellfreigaben
auch bei Statusabrufen erneut geprüft. Keine HA-/Supervisor-API wird verwendet.

**Autorisierte begrenzte Startkorrektur, weiterhin keine native Freigabe:**
Supervisor 2026.10.5 schreibt root-eigene Optionen mit Modus 0600. Der Container
startet deshalb mit einem kurzen Root-Bootstrap: ausschließlich die feste eigene
`/data/options.json` wird begrenzt, ohne Symlinks und als reguläre Datei gelesen
und validiert. Ein Dateiaustausch währenddessen wird erkannt. Danach schließt
der Bootstrap alle Deskriptoren oberhalb der Standard-Ein-/Ausgabe, entfernt
Zusatzgruppen und setzt alle drei UIDs/GIDs irreversibel auf 65532, bevor der
Webserver bindet oder eine Netzwerkverbindung beginnt. Effektive, erlaubte,
vererbbare und ambiente Fähigkeiten müssen null sein; `no_new_privs` ist gesetzt.
Soweit CAP_SETPCAP verfügbar ist, wird auch das Capability-Bounding-Set geleert.
Ohne diese Capability kann das Bounding-Set bestehen bleiben, aber keine
wirksamen/erlaubten Fähigkeiten oder Rechte über exec zurückkehren. Scheitert
die sichere Abgabe, startet kein Server. Keine Root-Web-App oder Root-Helfer.

Die Optionsdatei wird weder geschrieben noch chmod/chown unterzogen. Die private
validierte Momentaufnahme wird unter UID65532 nicht erneut als Secretdatei gelesen.
Vor Zulassung und Ergebnisfreigabe wird ihre aktuelle Dateimetadaten-/Identität
geprüft. Jede beobachtete Änderung, Ersetzung, Löschung oder unprüfbare Quelle
sperrt KI **bis zum App-Neustart**, auch wenn alte Werte wiederhergestellt werden.
Nach jeder Konfigurationsänderung daher bewusst neu starten. Leere/ungültige oder
fehlende Optionen ergeben nach sicherer Rechteabgabe Offline-Betrieb ohne Egress.
Die Host-Allowlist wird zusätzlich unabhängig frisch geprüft.

Es kommen keine API-Rechte, Mounts oder Ersatz-Secretkanäle hinzu. Ein Docker-
Healthcheck würde den Image-USER root erben; er ist deshalb deaktiviert, statt
wiederkehrende privilegierte Prozesse zu starten. Der konstante `/health`-Endpunkt
bleibt im Nicht-Root-Webserver verfügbar. Lokale echte 0600-/UID-/TLS-/Chromium-
Prüfungen und Kopplung an den neuen Host mit echtem SQLite-Journal sind erfolgt;
Image-Build, unabhängiges Review und native HA-/Modellabnahme bleiben getrennte Gates.

Keine Hintergrundbeobachtung, Hausaktionen oder Audiofunktion.

## Berechtigungen

Die App verlangt weder Home-Assistant-/Supervisor-API-Rechte noch Host-Netzwerk,
Host-Ports, Geräte oder Mounts. Startmodus ist `manual`. Nach dem begrenzten
Root-Bootstrap läuft die Anwendung als UID/GID `65532`. Die Plattform kann einen eingeschränkten technischen Token
injizieren; diese Anwendung liest, verwendet oder übermittelt ihn nicht.

Ingress-Anfragen müssen vom vorgesehenen Proxy kommen und eine einzelne gültige
Benutzerkennung tragen. `panel_admin: true` begrenzt die Seitenleistensichtbarkeit,
ist aber keine serverseitige Administratorrollenprüfung. Die App enthält keine
vorinstallierten privaten Benutzerdaten. Lokales Bearbeiten/Import/Export bleiben
im Browser; nur bewusst freigegebene Fragen und Ausschnitte gelangen in das
begrenzte Brückengespräch. Der HA-App-Server speichert keine Gerätebuchdatei.

## Spätere Prüfung in HA – aktuell blockiert

Erst nach unabhängigem Review, Image-/UID-/Capabilityprüfung und separat freigegebener Installation und Start die Weboberfläche über HA öffnen. Ein App-Status
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
