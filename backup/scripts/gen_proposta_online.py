#!/usr/bin/env python3
"""Gera link de proposta on-line interativa (HTML)"""
import json, os, sys, datetime

def gerar_proposta_html(cliente, projeto, escopo, valor_mensal, valor_total, prazo, saida=None):
    saida = saida or os.path.expanduser(f"~/Desktop/Proposta_{cliente.replace(' ','_')}.html")
    hoje = datetime.date.today()
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>Proposta - {cliente}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',Calibri,sans-serif;background:#F0F2F5;padding:40px;color:#333}}
.paper{{max-width:800px;margin:0 auto;background:#fff;border-radius:12px;padding:40px;box-shadow:0 2px 12px rgba(0,0,0,.1)}}
.header{{border-bottom:3px solid #1A237E;padding-bottom:20px;margin-bottom:30px}}
.header h1{{color:#1A237E;font-size:1.8rem}}
.header h1 span{{color:#C9A84C}}
.header .data{{color:#888;font-size:.9rem}}
.section{{margin-bottom:25px}}
.section h2{{color:#1A237E;font-size:1.1rem;margin-bottom:10px;border-left:4px solid #C9A84C;padding-left:10px}}
.section p{{line-height:1.6}}
.valor{{font-size:1.5rem;color:#1A237E;font-weight:700}}
.valor span{{font-size:.9rem;color:#888;font-weight:400}}
.cta{{background:#1A237E;color:#fff;border:none;padding:15px 30px;border-radius:8px;font-size:1.1rem;cursor:pointer;margin-top:20px;width:100%}}
.cta:hover{{background:#283593}}
.footer{{border-top:1px solid #ddd;margin-top:30px;padding-top:20px;font-size:.8rem;color:#888;text-align:center}}
@media(max-width:600px){{body{{padding:20px}}.paper{{padding:20px}}}}
</style>
</head>
<body>
<div class="paper">
<div class="header">
<h1>BUENOSERV <span>Proposta</span></h1>
<div class="data">{cliente} — {hoje:%d/%m/%Y}</div>
</div>
<div class="section">
<h2>Projeto</h2>
<p><strong>{projeto}</strong></p>
</div>
<div class="section">
<h2>Escopo</h2>
<p>{escopo}</p>
</div>
<div class="section">
<h2>Investimento</h2>
<p class="valor">R$ {valor_mensal:,.2f}<span>/mês</span></p>
<p>Valor total: <strong>R$ {valor_total:,.2f}</strong></p>
<p>Prazo: {prazo}</p>
<p>Regime: Simples Nacional</p>
</div>
<div class="section">
<h2>Próximos Passos</h2>
<p>Para aceitar esta proposta, responda este e-mail ou clique no botão abaixo.</p>
<button class="cta" onclick="alert('Proposta registrada! Entraremos em contato.')">ACEITAR PROPOSTA</button>
</div>
<div class="footer">
<p>BUENOSERV SERVIÇOS DE ENGENHARIA LTDA — CNPJ: 60.490.193/0001-38</p>
<p>Rua Giacomo Fior, nº 427 - Leme - SP | ricardo.bueno@buenoservengenharia.com</p>
</div>
</div>
</body>
</html>"""
    with open(saida, 'w') as f:
        f.write(html)
    print(f"✅ Proposta on-line: {saida}")
    print(f"   Abra no navegador para visualizar")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Uso: gen_proposta_online.py <cliente> <projeto> <escopo> <valor_mensal> [valor_total] [prazo]")
        sys.exit(1)
    valor_mensal = float(sys.argv[4])
    valor_total = float(sys.argv[5]) if len(sys.argv) > 5 else valor_mensal * 12
    prazo = sys.argv[6] if len(sys.argv) > 6 else "12 meses"
    gerar_proposta_html(sys.argv[1], sys.argv[2], sys.argv[3], valor_mensal, valor_total, prazo)
