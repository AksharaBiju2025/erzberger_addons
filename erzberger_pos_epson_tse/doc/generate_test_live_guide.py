import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_guide_document():
    doc = Document()

    # Margins
    for sec in doc.sections:
        sec.top_margin = Inches(0.8)
        sec.bottom_margin = Inches(0.8)
        sec.left_margin = Inches(0.8)
        sec.right_margin = Inches(0.8)

    # Color Palette
    PRIMARY = RGBColor(26, 82, 118)      # Deep Navy Blue
    SECONDARY = RGBColor(40, 116, 166)  # Medium Blue
    SUCCESS = RGBColor(30, 132, 73)     # Forest Green
    WARNING = RGBColor(186, 74, 0)      # Burnt Orange
    TEXT_DARK = RGBColor(44, 62, 80)    # Charcoal Dark

    # Title & Subtitle
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("Odoo 19 POS – Epson TSE Guide\n")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = PRIMARY

    r_sub = p_title.add_run("Step-by-Step Navigation: Test Mode vs. Live Original TSE Data Entry\n")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(13)
    r_sub.font.italic = True
    r_sub.font.color.rgb = SECONDARY

    # Horizontal Divider
    p_hr = doc.add_paragraph()
    p_hr.paragraph_format.space_after = Pt(12)
    r_hr = p_hr.add_run("―" * 55)
    r_hr.font.color.rgb = RGBColor(200, 200, 200)

    # Callout Box: Summary
    tbl_box = doc.add_table(rows=1, cols=1)
    tbl_box.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_box = tbl_box.cell(0, 0)
    set_cell_background(c_box, "EBF5FB")
    set_cell_margins(c_box, 120, 120, 180, 180)
    p_b = c_box.paragraphs[0]
    r_b_t = p_b.add_run("Key Concept to Understand:\n")
    r_b_t.font.bold = True
    r_b_t.font.size = Pt(11)
    r_b_t.font.color.rgb = PRIMARY

    r_b_c = p_b.add_run(
        "• Test Mode (ON): Allows you and your cashiers to practice entering sales. Signatures and QR codes "
        "are simulated in Odoo. ZERO data is written to the physical stick.\n"
        "• Live Mode (OFF): Every validated sale is transmitted over your network to the Epson TM-m30III "
        "and written permanently into the 8 GB flash memory of your original Epson USB-TSE stick (BSI TR-03153)."
    )
    r_b_c.font.size = Pt(10)
    r_b_c.font.color.rgb = TEXT_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # --- SECTION 1 ---
    h1 = doc.add_heading(level=1)
    r1 = h1.add_run("1. Navigation Paths in Odoo 19")
    r1.font.color.rgb = PRIMARY

    p_nav_intro = doc.add_paragraph()
    p_nav_intro.paragraph_format.line_spacing = 1.15
    p_nav_intro.add_run(
        "Below are the primary menu routes in Odoo used to configure and test the Epson TSE module:"
    )

    nav_paths = [
        ("Configuration Menu", "Point of Sale → Configuration → Point of Sale → Select your Register (e.g., 'Shop')", "Where you configure the TSE IP, serial CDCID, and toggle between Test Mode and Live Mode."),
        ("POS Cashier Dashboard", "Point of Sale → Dashboard → Click 'New Session' or 'Continue Selling'", "Where the cashier rings up products, processes customer payments, and validates orders."),
        ("Orders Audit Trail", "Point of Sale → Orders → Orders → Click on any Order → Open 'Extra' Tab", "Where store managers and accountants inspect the permanent TSE signature, counter, and raw QR code data.")
    ]

    for name, route, desc in nav_paths:
        p_n = doc.add_paragraph()
        p_n.paragraph_format.line_spacing = 1.15
        r_n_title = p_n.add_run(f"• {name}:\n   Path: ")
        r_n_title.font.bold = True
        r_n_title.font.color.rgb = PRIMARY
        r_n_route = p_n.add_run(route + "\n   ")
        r_n_route.font.bold = True
        r_n_route.font.color.rgb = SECONDARY
        p_n.add_run(desc)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # --- SECTION 2 ---
    h2 = doc.add_heading(level=1)
    r2 = h2.add_run("2. How to Enter Data in TEST MODE (Simulation)")
    r2.font.color.rgb = PRIMARY

    p_test_desc = doc.add_paragraph()
    p_test_desc.paragraph_format.line_spacing = 1.15
    p_test_desc.add_run(
        "Use Test Mode to train cashiers or verify POS receipt styling without wasting official signatures on your 5-year BSI certificate."
    )

    test_steps = [
        ("Step 1: Navigate to POS Config", "Go to Point of Sale → Configuration → Point of Sale. Click on your register (e.g. 'Shop')."),
        ("Step 2: Enable Test Mode", "Scroll down to the 'Epson TM-m30III USB TSE (Germany KassenSichV)' section. Check ☑ 'Enable Epson USB TSE' and check ☑ 'Simulation / Test Mode'. Click 'Save'."),
        ("Step 3: Open POS Cashier Session", "Go to Point of Sale → Dashboard. Click 'New Session'. The POS screen will load in your browser."),
        ("Step 4: Enter Order Items", "Add any products to the order (e.g. 1x Item with 19% VAT, 1x Item with 7% VAT)."),
        ("Step 5: Process Payment & Validate", "Click the large 'Payment' button. Select a payment method ('Cash' or 'Bank'). Enter the amount paid, then click 'Validate'."),
        ("Step 6: Inspect Receipt Output", "The receipt screen immediately appears. Under the totals, observe the 'TSE-Signatur (KassenSichV)' block with transaction number, signature counter, digital signature hash, offline-generated QR Code, and a red badge stating 'TEST-BELEG (TSE-SIMULATION)'."),
        ("Step 7: Verify Backend Record", "Open Point of Sale → Orders → Orders in another tab. Click on your order, open the 'Extra' tab, and verify that the TSE fields are populated with the test status.")
    ]

    for step_title, step_text in test_steps:
        p_s = doc.add_paragraph()
        p_s.paragraph_format.line_spacing = 1.15
        r_st = p_s.add_run(f"• {step_title}: ")
        r_st.font.bold = True
        r_st.font.color.rgb = SECONDARY
        p_s.add_run(step_text)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # --- SECTION 3 ---
    h3 = doc.add_heading(level=1)
    r3 = h3.add_run("3. How to Enter Data in LIVE MODE (Original Physical TSE)")
    r3.font.color.rgb = PRIMARY

    p_live_desc = doc.add_paragraph()
    p_live_desc.paragraph_format.line_spacing = 1.15
    p_live_desc.add_run(
        "Follow these exact steps when you are ready to record legal sales directly onto your physical Epson USB TSE stick."
    )

    live_steps = [
        ("Step 1: Check Physical Hardware", "Ensure the Epson USB-TSE stick is firmly inserted into the USB-A port on the Epson TM-m30III. Ensure the printer has paper and is connected via Ethernet LAN cable to your router."),
        ("Step 2: Get Printer IP Address", "Turn the printer ON. Hold the small push-button on the rear of the printer for 3 seconds. The printer prints a status sheet showing its IP address (e.g., 192.168.1.150)."),
        ("Step 3: Configure Live Mode in Odoo", "Navigate to Point of Sale → Configuration → Point of Sale. Open your register. In the Epson TSE section:\n"
         "   - Check ☑ 'Enable Epson USB TSE'\n"
         "   - UNCHECK ☐ 'Simulation / Test Mode' (Crucial: Must be unchecked for live writing!)\n"
         "   - Verify 'Printer / TSE IP Address' contains the printer's IP (e.g. 192.168.1.150)\n"
         "   - Verify 'TSE Serial / CDCID' matches your stick label (U31630FE89C52BE8E5)\n"
         "   - Click the 'Test TSE Connection' button. Verify the green success banner appears!"),
        ("Step 4: Launch Live POS Session", "Navigate to Point of Sale → Dashboard → Click 'New Session'."),
        ("Step 5: Enter Customer Sale", "Ring up a real sale with the customer's items."),
        ("Step 6: Validate & Sign", "Click 'Payment', select the payment method (Cash or Card), and click 'Validate'.\n"
         "   - Odoo transmits the fiscal command across your local network to the TM-m30III.\n"
         "   - The stick's BSI crypto-chip calculates the digital signature.\n"
         "   - The full transaction is written into the stick's 8 GB flash memory.\n"
         "   - The printer prints the official customer receipt with the authentic KassenSichV QR-Code.")
    ]

    for step_title, step_text in live_steps:
        p_ls = doc.add_paragraph()
        p_ls.paragraph_format.line_spacing = 1.15
        r_lst = p_ls.add_run(f"• {step_title}: ")
        r_lst.font.bold = True
        r_lst.font.color.rgb = SUCCESS
        p_ls.add_run(step_text)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # --- SECTION 4 ---
    h4 = doc.add_heading(level=1)
    r4 = h4.add_run("4. How to Prove the Data Went to the Original TSE")
    r4.font.color.rgb = PRIMARY

    p_proof_intro = doc.add_paragraph()
    p_proof_intro.paragraph_format.line_spacing = 1.15
    p_proof_intro.add_run(
        "You can easily prove to your client, management, and tax inspectors that transactions are stored on the physical stick using four independent checks:"
    )

    proofs = [
        ("Proof 1: Hardware Signature Counter", "Look at the receipt line 'TSE-Signaturzähler'. On a real TSE stick, this hardware-protected counter increases by +1 on every sale (e.g. 1, 2, 3, 4...). It cannot be reset or decreased."),
        ("Proof 2: CDCID Serial Number", "The receipt and the backend database show the authentic CDCID stamped on your Epson stick: U31630FE89C52BE8E5."),
        ("Proof 3: Smartphone QR-Code Scan", "Open your smartphone camera or any German fiscal inspection app ('KassenSichV Scanner'). Scan the printed QR code on the receipt. It displays the official DSFinV-K string signed by Seiko Epson Corporation."),
        ("Proof 4: Backend Revisionssicherheit", "In Odoo under Orders → Orders → Extra tab, the order is marked 'Signed (Compliant)' with the complete ECDSA Base64 signature hash.")
    ]

    for p_title, p_desc in proofs:
        p_pr = doc.add_paragraph()
        p_pr.paragraph_format.line_spacing = 1.15
        r_pr_t = p_pr.add_run(f"✔ {p_title}: ")
        r_pr_t.font.bold = True
        r_pr_t.font.color.rgb = SUCCESS
        p_pr.add_run(p_desc)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # --- SECTION 5: COMPARISON TABLE ---
    h5 = doc.add_heading(level=1)
    r5 = h5.add_run("5. Side-by-Side Comparison: Test Mode vs. Live Mode")
    r5.font.color.rgb = PRIMARY

    tbl_comp = doc.add_table(rows=6, cols=3)
    tbl_comp.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers_comp = ["Feature / Question", "Test Mode (Simulation)", "Live Mode (Original Physical TSE)"]
    for idx, text in enumerate(headers_comp):
        cell = tbl_comp.cell(0, idx)
        set_cell_background(cell, "1A5276")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(9.5)

    comp_rows = [
        ("Checkbox in Odoo Config", "☑ 'Simulation / Test Mode' checked", "☐ 'Simulation / Test Mode' UNCHECKED"),
        ("Written to 8GB TSE Stick?", "NO (Kept in browser memory)", "YES (Committed to 8GB Flash Memory)"),
        ("Consumes Signature Capacity?", "NO (Zero wear on BSI certificate)", "YES (Counts toward 20M signature limit)"),
        ("Receipt Appearance", "Includes red 'TEST-BELEG' banner", "Clean legal receipt with official QR code"),
        ("Audit / Legal Validity", "For training & development only", "100% Tax-compliant (§ 146a AO / KassenSichV)")
    ]

    for row_idx, (feat, test_val, live_val) in enumerate(comp_rows, start=1):
        bg = "F2F4F4" if row_idx % 2 == 0 else "FFFFFF"
        for col_idx, val in enumerate([feat, test_val, live_val]):
            cell = tbl_comp.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 80, 80)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(9)
            if col_idx == 0:
                r.font.bold = True
                r.font.color.rgb = PRIMARY
            elif col_idx == 2:
                r.font.bold = True
                r.font.color.rgb = SUCCESS

    # Footer
    doc.add_paragraph().paragraph_format.space_after = Pt(14)
    p_foot = doc.add_paragraph()
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_foot = p_foot.add_run("Erzberger POS Integration – Epson TM-m30III TSE – Odoo 19")
    r_foot.font.size = Pt(8.5)
    r_foot.font.italic = True
    r_foot.font.color.rgb = RGBColor(128, 128, 128)

    # Output paths
    p1 = "/home/kabilan/workspace/enterprise/odoo19/custom/erzberger]/local/erzberger_addons/erzberger_pos_epson_tse/doc/Erzberger_POS_TSE_Test_and_Live_Navigation_Guide.docx"
    p2 = "/home/kabilan/workspace/enterprise/odoo19/custom/erzberger]/local/erzberger_addons/Erzberger_POS_TSE_Test_and_Live_Navigation_Guide.docx"

    os.makedirs(os.path.dirname(p1), exist_ok=True)
    doc.save(p1)
    doc.save(p2)
    print("Saved:", p1)
    print("Saved:", p2)

if __name__ == "__main__":
    create_guide_document()
