from fpdf import FPDF
from datetime import datetime

class MeetingPDF(FPDF):
    def header(self):
        # Header di setiap halaman
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, "Laporan Notulensi Meeting Otomatis", border=False, ln=True, align="L")
        self.set_font("helvetica", "I", 8)
        self.cell(0, 5, f"Dibuat pada: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
        self.ln(10)

    def footer(self):
        # Nomor halaman di bawah
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Halaman {self.page_no()}/{{nb}}", align="C")

def save_to_pdf(text_content, filename="Notulensi_Meeting.pdf"):
    pdf = MeetingPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Menggunakan font Helvetica (standar & ringan)
    pdf.set_font("helvetica", size=11)
    
    # Memproses teks agar aman dari karakter aneh (encoding)
    # Gemini sering memberikan Markdown, kita akan membersihkan sedikit
    clean_text = text_content.encode('latin-1', 'replace').decode('latin-1')
    
    # Tulis isi ke PDF
    # multi_cell otomatis membungkus teks ke baris baru jika sudah mentok pinggir
    pdf.multi_cell(0, 7, txt=clean_text)
    
    pdf.output(filename)
    print(f"File PDF berhasil dibuat: {filename}")