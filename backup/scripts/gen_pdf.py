#!/usr/bin/env python3
"""Gerador de PDF (.pdf) — fpdf2"""
from fpdf import FPDF
import sys, json

class PDFBuenoserv(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(0x1A, 0x23, 0x7E)
        self.cell(0, 8, 'BUENOSERV - SERVICOS DE ENGENHARIA LTDA', align='C')
        self.ln(4)
        self.set_draw_color(0x1A, 0x23, 0x7E)
        self.line(10, 18, 200, 18)
        self.ln(4)
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}/{{nb}}', align='C')
    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(0x1A, 0x23, 0x7E)
        self.cell(0, 8, title, new_x='LMARGIN', new_y='NEXT')
        self.ln(2)
    def chapter_body(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5, text)
        self.ln()
    def add_table(self, cabecalhos, dados):
        self.set_font('Helvetica', 'B', 9)
        self.set_fill_color(0x1A, 0x23, 0x7E)
        self.set_text_color(255, 255, 255)
        col_w = (190 - (len(cabecalhos)-1)) / len(cabecalhos)
        for h in cabecalhos:
            self.cell(col_w, 7, h, border=1, fill=True, align='C')
        self.ln()
        self.set_font('Helvetica', '', 9)
        self.set_text_color(0, 0, 0)
        for row in dados:
            for v in row:
                self.cell(col_w, 6, str(v), border=1, align='C')
            self.ln()

def gerar_pdf(nome, titulo, autor="BUENOSERV ENGENHARIA", secoes=None):
    pdf = PDFBuenoserv()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(0x1A, 0x23, 0x7E)
    pdf.ln(60)
    pdf.cell(0, 15, titulo, align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 10, autor, align='C', new_x='LMARGIN', new_y='NEXT')
    if secoes:
        pdf.add_page()
        for s in secoes:
            pdf.chapter_title(s['titulo'])
            pdf.chapter_body(s['texto'])
    pdf.output(nome)
    print(f"PDF|OK|{nome}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: gen_pdf.py <comando> <args_json>")
        sys.exit(1)
    cmd = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if cmd == "pdf":
        gerar_pdf(args["nome"], args["titulo"], args.get("autor","BUENOSERV"), args.get("secoes"))
    else:
        print(f"Comando desconhecido: {cmd}")
