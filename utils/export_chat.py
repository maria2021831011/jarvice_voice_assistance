from fpdf import FPDF

def export_txt(history):
    with open("chat.txt", "w") as f:
        for msg in history:
            f.write(f"{msg['role']}: {msg['message']}\n")

def export_pdf(history):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for msg in history:
        pdf.multi_cell(0, 8, f"{msg['role']}: {msg['message']}")
    pdf.output("chat.pdf")
