#!/usr/bin/env python3
"""Gera catálogo de serviços BUENOSERV em PDF"""
from fpdf import FPDF
from datetime import datetime

class PortfolioPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, 'BUENOSERV SERVIÇOS DE ENGENHARIA LTDA', 0, 0, 'L')
        self.cell(0, 6, 'www.buenoservengenharia.com.br', 0, 1, 'R')
        self.line(10, 14, 200, 14)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Pagina {self.page_no()}/{{nb}}', 0, 0, 'C')

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(26, 35, 126)
        self.cell(0, 12, title, 0, 1, 'L')
        self.set_draw_color(201, 168, 76)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(6)

    def service_block(self, icon, title, items):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(26, 35, 126)
        self.cell(0, 7, f'> {title}', 0, 1)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(80, 80, 80)
        for item in items:
            self.cell(0, 5.5, f'  - {item}', 0, 1)
        self.ln(3)


def gerar():
    pdf = PortfolioPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # Capa
    pdf.ln(50)
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(26, 35, 126)
    pdf.cell(0, 14, 'BUENOSERV', 0, 1, 'C')
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, 'Engenharia & Telecomunicacoes', 0, 1, 'C')
    pdf.ln(6)
    pdf.set_draw_color(201, 168, 76)
    pdf.set_line_width(1)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(6)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, 'Catalogo de Servicos', 0, 1, 'C')
    pdf.cell(0, 6, f'{datetime.now().strftime("%B/%Y")}', 0, 1, 'C')
    pdf.ln(40)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, 'BUENOSERV SERVICOS DE ENGENHARIA LTDA | CNPJ: 60.490.193/0001-38', 0, 1, 'C')
    pdf.cell(0, 5, 'Rua Giacomo Fior, 427 - Leme - SP', 0, 1, 'C')
    pdf.cell(0, 5, 'Diretor Tecnico: Ricardo Bueno', 0, 1, 'C')

    # Pagina 2 - Quem somos
    pdf.add_page()
    pdf.section_title('Quem Somos')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 5.5,
        'A BUENOSERV e uma empresa de engenharia especializada em telecomunicacoes, '
        'automacao de subestacoes, energia e seguranca para concessionarias, industrias '
        'e integradoras do setor eletrico.'
    )
    pdf.ln(3)
    pdf.multi_cell(0, 5.5,
        'Com mais de 20 anos de experiencia em comissionamento de subestacoes de ate 500 kV, '
        'sistemas de protecao e redes de telecomunicacoes criticas, entregamos solucoes com '
        'excelencia, seguranca e pontualidade.'
    )
    pdf.ln(3)
    pdf.multi_cell(0, 5.5,
        'Nosso diretor tecnico, Ricardo Bueno, possui vasta experiencia em empresas de '
        'referencia como Zopone, Brasnorte, Lumitrans, ALSTOM Grid, Padtec e EBTE, '
        'com atuacao em projetos de porte nacional e internacional.'
    )

    # Pagina 3 - Servicos
    pdf.add_page()
    pdf.section_title('Servicos')
    pdf.set_text_color(60, 60, 60)
    pdf.service_block('📡', 'Telecomunicacoes', [
        'Redes DWDM, MPLS-TP, SDH ePDH',
        'Radio digital micro-ondas (MW)',
        'Fibra otica OPGW, ADSS, lancto e emenda',
        'Sistemas de comunicacao critica e VoIP',
        'Projetos de redes OTN e Ethernet industrial'
    ])
    pdf.service_block('⚡', 'Automacao de Subestacoes', [
        'Sistemas de Protecao, Controle e Supervisao (SPCS) IEC 61850',
        'Teleprotecao, RTU, IEDs, PMU',
        'Integracao SCADA e sistemas legados',
        'Configuracao de reles de protecao (SEL, GE, ABB, Siemens)',
        'Testes de logicas de automacao e intertravamento'
    ])
    pdf.service_block('🔧', 'Comissionamento', [
        'Testes FAT (Factory Acceptance) e SAT (Site Acceptance)',
        'Start-up e integracao de sistemas de telecom e automacao',
        'Elaboracao de laudos tecnicos e relatorios',
        'Treinamento operacional e transferencia tecnologica',
        'Documentacao as-built'
    ])
    pdf.service_block('🏗️', 'Infraestrutura', [
        'Projetos turn-key de engenharia civil e eletrica para telecom',
        'SPDA (Sistemas de Protecao contra Descargas Atmosfericas)',
        'CFTV, controle de acesso, alarme de intrusao',
        'Data centers, salas tecnicas, DGO',
        'Sistemas de energia DC/AC, nobreaks, bancos de baterias'
    ])
    pdf.service_block('📋', 'Consultoria', [
        'Engenharia do proprietario e fiscalizacao de obras',
        'Elaboracao de especificacoes tecnicas e editais',
        'Due diligence de sistemas de telecom e automacao',
        'Auditoria tecnica e conformidade normativa (ONS, IEC, ABNT)',
        'Planejamento estrategico de expansao de redes'
    ])

    # Pagina 4 - Cases
    pdf.add_page()
    pdf.section_title('Cases')
    cases = [
        ('ZOPONE / ENERSUL', 'Comissionamento SE 230 kV',
         'Comissionamento completo de sistemas de protecao, SCADA, '
         'telecom (SDH/DWDM) e teleprotecao em subestacao 230 kV.'),
        ('BRASNORTE ENERGIA', 'Telecom para Parques Eolicos',
         'Rede de fibra otica OPGW, radio MW e SDH/DWDM para '
         'integracao de parques eolicos ao Sistema Interligado Nacional.'),
        ('PADTEC / LUMITRANS', 'Rede DWDM para Transmissao',
         'Projeto e comissionamento de sistema DWDM backbone para '
         'rede de telecom entre subestacoes de transmissao.'),
        ('ALSTOM GRID', 'Automacao de SE - Sistema de Protecao',
         'Engenharia de automacao, configuracao de IEDs e testes de '
         'sistemas de protecao para subestacoes de ate 500 kV.'),
    ]
    for cliente, projeto, desc in cases:
        pdf.set_fill_color(26, 35, 126)
        pdf.set_text_color(201, 168, 76)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(0, 5, f'{cliente}', 0, 1)
        pdf.set_text_color(26, 35, 126)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 6, projeto, 0, 1)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(0, 5, desc)
        pdf.ln(4)

    # Pagina 5 - Diferenciais e Contato
    pdf.add_page()
    pdf.section_title('Diferenciais')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(60, 60, 60)
    diffs = [
        ('20+ anos de experiencia', 'em comissionamento de SE, protecao, SCADA e telecom'),
        ('Atuacao nacional', 'em concessionarias, industrias e integradoras'),
        ('Equipe multidisciplinar', 'engenheiros eletricistas, de telecom e automacao'),
        ('Metodologia propria', 'processos padronizados para garantia de qualidade'),
        ('Foco em resultados', 'compromisso com prazos, custos e satisfacao do cliente'),
    ]
    for title, desc in diffs:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(26, 35, 126)
        pdf.cell(0, 6, f'  {title}', 0, 1)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 5, f'     {desc}', 0, 1)
        pdf.ln(2)

    pdf.ln(8)
    pdf.section_title('Contato')
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(60, 60, 60)
    info = [
        'Diretor Tecnico: Ricardo Bueno',
        'E-mail: ricardo.bueno@buenoservengenharia.com',
        'Endereco: Rua Giacomo Fior, 427 - Leme - SP',
        'CNPJ: 60.490.193/0001-38',
        'Regime: Simples Nacional',
    ]
    for line in info:
        pdf.cell(0, 5.5, line, 0, 1)

    out = '/tmp/opencode/catalogo-buenoserv.pdf'
    pdf.output(out)
    print(f'OK: {out}')

if __name__ == '__main__':
    gerar()
