import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_document():
    doc = Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Styles & Colors
    PRIMARY = RGBColor(26, 82, 118)     # Navy Blue
    SECONDARY = RGBColor(40, 116, 166) # Lighter Blue
    TEXT_DARK = RGBColor(44, 62, 80)   # Charcoal
    ACCENT = RGBColor(186, 74, 0)      # Orange accent

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("Erzberger POS – Epson TM-m30III USB TSE\n")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = PRIMARY

    run_sub = p_title.add_run("Module Workflow, Configuration & Testing Guide for Odoo 19\nGerman KassenSichV & BSI TR-03153 Compliance")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(13)
    run_sub.font.italic = True
    run_sub.font.color.rgb = SECONDARY

    # Horizontal Rule
    p_hr = doc.add_paragraph()
    p_hr.paragraph_format.space_after = Pt(14)
    run_hr = p_hr.add_run("―" * 55)
    run_hr.font.color.rgb = RGBColor(200, 200, 200)

    # Hardware Info Callout Box
    table_box = doc.add_table(rows=1, cols=1)
    table_box.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_box = table_box.cell(0, 0)
    set_cell_background(cell_box, "EBF5FB")
    set_cell_margins(cell_box, 140, 140, 200, 200)

    p_box = cell_box.paragraphs[0]
    p_box.paragraph_format.space_after = Pt(4)
    r_box_title = p_box.add_run("Hardware Specifications & Identifiers:\n")
    r_box_title.font.bold = True
    r_box_title.font.size = Pt(11)
    r_box_title.font.color.rgb = PRIMARY

    hardware_info = (
        "• Receipt Printer: Epson TM-m30III (Model: M374B, Serial: XBVW035465)\n"
        "• Printer Network Interfaces: Ethernet LAN, Wi-Fi, USB-A Host (for TSE), USB-C\n"
        "• MAC Address: A4D73CAA9352\n"
        "• TSE Unit: Epson USB-TSE Stick (Model: TSE-TR03153 8GB, SKU: 7112348)\n"
        "• TSE CDCID Code: U31630FE89C52BE8E5\n"
        "• BSI Certificate Validity: 5 Years (Valid through 30/06/2031)\n"
        "• Certified Capacity: 20 Million cryptographic signatures"
    )
    r_box_body = p_box.add_run(hardware_info)
    r_box_body.font.size = Pt(10)
    r_box_body.font.color.rgb = TEXT_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # --- SECTION 1 ---
    h1 = doc.add_heading(level=1)
    r1 = h1.add_run("1. System Architecture & Functional Workflow")
    r1.font.color.rgb = PRIMARY

    p_intro = doc.add_paragraph()
    p_intro.paragraph_format.line_spacing = 1.15
    p_intro.add_run(
        "The erzberger_pos_epson_tse module integrates Odoo 19 Point of Sale directly with the Epson TM-m30III "
        "receipt printer and the inserted BSI-certified USB TSE unit. Unlike Odoo's standard cloud-based Fiskaly "
        "integration, this solution provides 100% offline capability and incurs zero recurring monthly subscription fees."
    )

    # How data is stored
    h2_storage = doc.add_heading(level=2)
    h2_storage.add_run("1.1 How Data is Stored on the USB TSE Stick")
    
    p_storage = doc.add_paragraph()
    p_storage.paragraph_format.line_spacing = 1.15
    p_storage.add_run(
        "A critical technical distinction is that the receipt printer does NOT automatically write to the TSE "
        "merely by printing a standard receipt. The TSE unit is an intelligent security appliance consisting of two parts:\n"
    )
    p_storage_pts = doc.add_paragraph()
    p_storage_pts.paragraph_format.line_spacing = 1.15
    p_storage_pts.add_run(
        "1. A Certified Cryptographic Security Chip (SMAERS / CSP): Generates ECDSA digital signatures (ecdsa-plain-SHA256), "
        "tracks an unalterable signature counter, and cryptographically chains every transaction to the preceding one.\n"
        "2. An 8 GB Secure Flash Memory: Stores transaction logs, audit journals, and system protocols in a tamper-proof "
        "TAR archive format mandated by BSI TR-03153 and DSFinV-K for tax audits."
    )

    # Workflow Phases
    h2_phases = doc.add_heading(level=2)
    h2_phases.add_run("1.2 The 6 Workflow Phases")

    phases = [
        ("Phase 1: Cart Creation", "Cashier adds items. Odoo classifies amounts according to German VAT rates (19% standard, 7% reduced, 0% tax-free)."),
        ("Phase 2: Payment Interception", "When the cashier clicks 'Validate', the custom OrderPaymentValidation patch intercepts the process."),
        ("Phase 3: TSE Communication", "Odoo formats the DSFinV-K process payload (e.g. Beleg^0.00_119.00_0.00_0.00_0.00^119.00:Bar) and transmits an ePOS-Device XML finishTransaction command to the TM-m30III over the local network."),
        ("Phase 4: Hardware Signing & Storage", "The TM-m30III relays the command to the USB-A TSE stick. The crypto chip signs the payload, increments the signature counter, and commits the audit record directly to the 8GB flash drive."),
        ("Phase 5: Receipt & QR Code Generation", "The TSE returns the signature value, counter, start/stop times, and serial number. Odoo formats the standardized DSFinV-K string and generates a scannable QR code completely offline."),
        ("Phase 6: Database Persistence", "The order is saved in Odoo with all TSE audit fields permanently attached to the pos.order database record.")
    ]

    for title, desc in phases:
        p_ph = doc.add_paragraph()
        p_ph.paragraph_format.line_spacing = 1.15
        r_ph_title = p_ph.add_run(f"• {title}: ")
        r_ph_title.font.bold = True
        r_ph_title.font.color.rgb = SECONDARY
        p_ph.add_run(desc)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # --- SECTION 2 ---
    h2 = doc.add_heading(level=1)
    r2 = h2.add_run("2. Configuration Guide & Added Fields")
    r2.font.color.rgb = PRIMARY

    p_cfg_desc = doc.add_paragraph()
    p_cfg_desc.paragraph_format.line_spacing = 1.15
    p_cfg_desc.add_run(
        "All configuration settings are located in Odoo under Point of Sale → Configuration → Point of Sale "
        "(open your cash register). A dedicated card titled 'Epson TM-m30III USB TSE (Germany KassenSichV)' has been added."
    )

    # Table of configurations
    headers = ["Field Name in UI", "Technical Field", "Default Value", "Purpose & Recommendation"]
    cfg_data = [
        ("Enable Epson USB TSE", "l10n_de_epson_tse_enabled", "False", "Master switch to turn on German TSE compliance for this register."),
        ("Simulation / Test Mode", "l10n_de_epson_tse_test_mode", "False", "Simulates valid TSE signatures in browser. Ideal for testing without hardware."),
        ("Printer / TSE IP Address", "l10n_de_epson_tse_ip", "192.168.1.100", "Local IP address of the Epson TM-m30III (e.g. 192.168.1.150)."),
        ("Port", "l10n_de_epson_tse_port", "80", "ePOS HTTP port (80 for standard HTTP, 8043 for HTTPS, 8009 for TSE service)."),
        ("Protocol", "l10n_de_epson_tse_protocol", "HTTP", "Use HTTP (default) or HTTPS if an SSL certificate is loaded on the printer."),
        ("Device ID", "l10n_de_epson_tse_devid", "local_printer", "Epson peripheral identifier (standard: local_printer)."),
        ("Client ID (Kassen-ID)", "l10n_de_epson_tse_client_id", "POS-01", "Unique register identification registered on the TSE."),
        ("TSE Serial / CDCID", "l10n_de_epson_tse_serial", "U31630FE89C52BE8E5", "The exact CDCID printed on your stick label (*U31630FE89C52BE8E5*)."),
        ("Test TSE Connection", "action_test_epson_tse_connection", "Action Button", "Sends TCP socket & HTTP HEAD requests to verify printer reachability.")
    ]

    tbl = doc.add_table(rows=len(cfg_data) + 1, cols=4)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Format Header Row
    for col_idx, text in enumerate(headers):
        cell = tbl.cell(0, col_idx)
        set_cell_background(cell, "1A5276")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(9.5)

    # Format Data Rows
    for row_idx, data_row in enumerate(cfg_data, start=1):
        bg = "F2F4F4" if row_idx % 2 == 0 else "FFFFFF"
        for col_idx, text in enumerate(data_row):
            cell = tbl.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 80, 80)
            p = cell.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(9)
            if col_idx == 0:
                r.font.bold = True
                r.font.color.rgb = PRIMARY
            elif col_idx == 1:
                r.font.name = "Courier New"
                r.font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # --- SECTION 3 ---
    h3 = doc.add_heading(level=1)
    r3 = h3.add_run("3. Step-by-Step Testing Guide in Odoo")
    r3.font.color.rgb = PRIMARY

    # Test Scenario A
    h3_a = doc.add_heading(level=2)
    h3_a.add_run("Scenario A: Testing in Simulation Mode (Zero Hardware Required)")

    p_scen_a = doc.add_paragraph()
    p_scen_a.paragraph_format.line_spacing = 1.15
    p_scen_a.add_run(
        "You can test the entire POS cashier workflow immediately without turning on the printer:\n"
        "1. Open Point of Sale → Configuration → Point of Sale and select your cash register.\n"
        "2. Check 'Enable Epson USB TSE' and check 'Simulation / Test Mode'. Save changes.\n"
        "3. Go to Dashboard and click 'New Session'.\n"
        "4. Add products to the order, click 'Payment', select Cash or Bank, and click 'Validate'.\n"
        "5. Observe the receipt: The 'TSE-Signatur (KassenSichV)' block appears with transaction number, "
        "signature counter, timestamps, signature hash, a scannable QR Code, and a 'TEST-BELEG (TSE-SIMULATION)' badge.\n"
        "6. In backend under Orders → Orders, open the order and check the 'Extra' tab to confirm all fields are saved."
    )

    # Test Scenario B
    h3_b = doc.add_heading(level=2)
    h3_b.add_run("Scenario B: Testing with Live Hardware (TM-m30III + USB TSE Stick)")

    p_scen_b = doc.add_paragraph()
    p_scen_b.paragraph_format.line_spacing = 1.15
    p_scen_b.add_run(
        "1. Hardware Setup: Plug the USB TSE Stick into the USB-A port on the Epson TM-m30III. Connect the Ethernet cable to your router and power on the printer.\n"
        "2. Determine IP Address: Hold down the small push button on the printer's rear interface panel for 3 seconds. The printer prints a network sheet containing the assigned IP address (e.g. 192.168.1.150).\n"
        "3. Odoo Configuration: In POS settings, uncheck 'Simulation / Test Mode'. Enter the printer's IP address and click 'Test TSE Connection'. A green confirmation banner will appear.\n"
        "4. Process a Live Sale: Open a POS session, ring up a sale, and validate payment. The TM-m30III communicates with the USB stick, signs the transaction, saves it to the 8GB flash memory, and prints the compliant receipt.\n"
        "5. QR Code Scan: Scan the QR code with any smartphone camera or tax authority app (e.g. 'KassenSichV Scanner'). It decodes into the official DSFinV-K format starting with V0;POS-01;Kassenbeleg-V1;..."
    )

    # --- SECTION 4 ---
    h4 = doc.add_heading(level=1)
    r4 = h4.add_run("4. Emergency & Offline Handling (§ 7 KassenSichV)")
    r4.font.color.rgb = PRIMARY

    p_emg = doc.add_paragraph()
    p_emg.paragraph_format.line_spacing = 1.15
    p_emg.add_run(
        "German law (§ 7 KassenSichV) permits sales to continue if the TSE hardware fails or is disconnected, "
        "provided the failure is documented. If the TM-m30III printer is unreachable during validation, Odoo displays "
        "a dialog with the exact printer IP and error details, allowing the cashier to retry or issue an emergency receipt."
    )

    # Footer note
    doc.add_paragraph().paragraph_format.space_after = Pt(14)
    p_foot = doc.add_paragraph()
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_foot = p_foot.add_run("Document generated for Erzberger POS Integration — Odoo 19 Enterprise")
    r_foot.font.size = Pt(8.5)
    r_foot.font.italic = True
    r_foot.font.color.rgb = RGBColor(128, 128, 128)

    # Save documents
    target_path1 = "/home/kabilan/workspace/enterprise/odoo19/custom/erzberger]/local/erzberger_addons/erzberger_pos_epson_tse/doc/Erzberger_POS_Epson_TSE_Documentation.docx"
    target_path2 = "/home/kabilan/workspace/enterprise/odoo19/custom/erzberger]/local/erzberger_addons/Erzberger_POS_Epson_TSE_Documentation.docx"
    
    os.makedirs(os.path.dirname(target_path1), exist_ok=True)
    doc.save(target_path1)
    doc.save(target_path2)
    print(f"Successfully created: {target_path1}")
    print(f"Successfully created: {target_path2}")

if __name__ == "__main__":
    create_document()
