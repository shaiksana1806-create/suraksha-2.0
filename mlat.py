from fpdf import FPDF

def generate(case):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 12)

    pdf.cell(200, 10, "MLAT CYBERCRIME REPORT", ln=True)
    pdf.ln(5)

    for k, v in case.items():
        pdf.cell(200, 10, f"{k}: {v}", ln=True)

    filename = f"{case['case_id']}.pdf"
    pdf.output(filename)

    return filename
