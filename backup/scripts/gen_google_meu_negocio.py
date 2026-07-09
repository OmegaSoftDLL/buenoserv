#!/usr/bin/env python3
"""Checklist Google Meu Negócio — configuração de presença local"""
import datetime

CHECKLIST = [
    ("✅", "Criar conta Google Business", "business.google.com - usar ricardo.bueno@buenoservengenharia.com"),
    ("⬜", "Nome da empresa", "BUENOSERV SERVIÇOS DE ENGENHARIA LTDA"),
    ("⬜", "Categoria", "Empresa de engenharia / Serviços de engenharia elétrica"),
    ("⬜", "Endereço", "Rua Giacomo Fior, nº 427 - Leme - SP, 13610-000"),
    ("⬜", "Área de serviço", "Leme-SP, região de Piracicaba, Campinas, Ribeirão Preto, São Paulo, todo o Brasil"),
    ("⬜", "Telefone", "19 - informar número"),
    ("⬜", "WhatsApp", "19 - informar número (configurar botão)"),
    ("⬜", "Horário", "Seg-Sex 08:00-18:00"),
    ("⬜", "Site", "https://buenoservengenharia.com.br"),
    ("⬜", "Fotos", "Logo + 5 fotos (escritório, obras, equipe)"),
    ("⬜", "Postagens", "Publicar 1x/semana (cases, dicas técnicas)"),
    ("⬜", "Verificação", "Código por correio (Google envia cartão)"),
    ("⬜", "Avaliações", "Responder todas em até 24h"),
]

print(f"\n{'='*55}")
print(f"  GOOGLE MEU NEGÓCIO — CHECKLIST")
print(f"  Data: {datetime.date.today():%d/%m/%Y}")
print(f"{'='*55}")
for status, item, detalhe in CHECKLIST:
    print(f"  {status} {item}")
    print(f"     {detalhe}")
print(f"{'='*55}")
print(f"\nAções necessárias:")
print(f"  1. Criar conta em business.google.com")
print(f"  2. Preencher todos os campos acima")
print(f"  3. Solicitar verificação por correio")
print(f"  4. Publicar 1 post/semana")
print(f"  5. Monitorar avaliações")
