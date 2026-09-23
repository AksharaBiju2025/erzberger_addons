# Erzberger POS - Epson TM-m30III USB TSE Integration (Germany KassenSichV)

Dieses Modul bindet den **Epson TM-m30III Bondrucker (Model: M374B)** zusammen mit dem zertifizierten **Epson USB-TSE-Stick** (`TSE-TR03153 8GB`, SKU `7112348`, CDCID `U31630FE89C52BE8E5`, BSI-Zertifikat gültig bis `30.06.2031`) direkt an **Odoo 19 Point of Sale** an.

> 📖 **Ausführliche Dokumentation zu Workflow, Konfiguration & Tests:**  
> Siehe [doc/WORKFLOW_AND_TESTING.md](doc/WORKFLOW_AND_TESTING.md)

---

## 1. Funktionsweise & Datenspeicherung

### Wie werden die Daten gespeichert?
* Der USB-TSE-Stick enthält einen zertifizierten **Krypto-Sicherheitschip (SMAERS / CSP)** und **8 GB geschützten Flash-Speicher**.
* **Keine automatische Speicherung rein durchs Drucken:** Der Drucker speichert Belege erst dann auf der TSE, wenn die Kasse (Odoo POS) die Transaktion über das TSE-Protokoll signiert.
* **Transaktionsablauf:**
  1. Bei Kassenabschluss bzw. Bezahlung sendet Odoo POS die Belegdaten (Bruttobeträge, Steuersätze 19%/7%/0%, Zahlungsart Bar/Unbar) an den TM-m30III.
  2. Der Krypto-Chip der TSE signiert die Daten (`ecdsa-plain-SHA256`), erhöht den internen Signaturzähler und verkettet die Transaktion manipulationssicher mit dem Hash der vorherigen Transaktion.
  3. Die vollständigen Transaktionsdaten werden manipulationssicher auf dem 8-GB-Flashspeicher des Sticks protokolliert (entsprechend BSI TR-03153 und DSFinV-K).
  4. Die TSE meldet Transaktionsnummer, Start-/Endzeitpunkt, Signaturzähler und den Signaturwert an Odoo POS zurück.
  5. Odoo POS druckt die TSE-Daten und den **gesetzeskonformen KassenSichV-QR-Code** auf den Kundenbeleg.

---

## 2. Hardware-Einrichtung am Epson TM-m30III

1. **TSE-Stick einstecken:**
   * Stecken Sie den Epson USB-TSE-Stick in den USB-A-Anschluss an der Unter-/Rückseite des Epson TM-m30III Druckers.
2. **Netzwerkanbindung:**
   * Verbinden Sie den Drucker per LAN-Netzwerkkabel (Ethernet) mit Ihrem Router / Netzwerk-Switch (empfohlen für maximale Stabilität) oder über WLAN.
3. **IP-Adresse ermitteln:**
   * Schalten Sie den Drucker ein.
   * Halten Sie den kleinen **Status-/Push-Button** an der Rückseite des Druckers für ca. 3 Sekunden gedrückt.
   * Der Drucker druckt ein Statusblatt aus, auf dem die vergebene **IP-Adresse** (z. B. `192.168.1.150`) steht.
   *(Tipp: Vergeben Sie im Router eine feste IP-Adresse / DHCP-Reservation für den Drucker anhand der auf dem Aufkleber sichtbaren MAC-Adresse `A4D73CAA9352`)*.

---

## 3. Konfiguration in Odoo 19

1. Installieren Sie das Modul **`erzberger_pos_epson_tse`** unter *Apps*.
2. Navigieren Sie zu **Kassensystem (Point of Sale) -> Konfiguration -> Einstellungen** oder bearbeiten Sie Ihren Kassenplatz.
3. Scrollen Sie zum Bereich **Epson TM-m30III USB TSE (Germany KassenSichV)**:
   * **Epson USB TSE aktivieren:** Häkchen setzen.
   * **Drucker / TSE IP-Adresse:** Die IP des Druckers eintragen (z. B. `192.168.1.150`).
   * **Port:** `80` (Standard ePOS HTTP) oder `8043` / `8009`.
   * **Device ID:** `local_printer`.
   * **Kassen-ID (Client ID):** z. B. `POS-01`.
   * **TSE CDCID / Seriennummer:** `U31630FE89C52BE8E5` (oder Ihre Seriennummer).
   * **Verbindung testen:** Klicken Sie auf den Button **"Test TSE Connection"**, um die Erreichbarkeit des Druckers sofort zu prüfen.
   * **Simulations- / Test-Modus:** 
     * *Aktiviert:* Simuliert konforme TSE-Signaturen direkt im Browser (ideal für Tests ohne eingeschalteten Drucker).
     * *Deaktiviert:* Reale Signierung über die Hardware-TSE im Drucker (Produktivbetrieb).

---

## 4. Belegprüfung & Nachweis

* Beim Kassieren wird jeder Beleg automatisch signiert.
* Auf dem Kassenbon erscheinen:
  * `TSE-Transaktion: #...`
  * `TSE-Signaturzähler: #...`
  * `TSE-Start & TSE-Stop`
  * `TSE-Seriennummer: U31630FE89C52BE8E5`
  * `TSE-Signatur`
  * **KassenSichV-QR-Code** (kann von Prüfern des Finanzamts direkt gescannt werden).
* Im Odoo Backend unter **Kassensystem -> Bestellungen -> [Bestellung öffnen] -> Zusätzliche Informationen** sind alle TSE-Signaturwerte manipulationssicher hinterlegt.
