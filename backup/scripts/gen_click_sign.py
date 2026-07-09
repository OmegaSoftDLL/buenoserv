#!/usr/bin/env python3
"""Contrato click-to-sign — gera contrato + link para assinatura digital"""
import os, sys, datetime

def gerar_contrato_html(cliente, valor, objeto, saida=None):
    saida = saida or os.path.expanduser(f"~/Desktop/Contrato_{cliente.replace(' ','_')}_para_assinatura.html")
    hoje = datetime.date.today()
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>Contrato - {cliente}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',Calibri,sans-serif;background:#F0F2F5;padding:40px;color:#333}}
.paper{{max-width:800px;margin:0 auto;background:#fff;padding:40px;box-shadow:0 2px 12px rgba(0,0,0,.1)}}
h1{{color:#1A237E;font-size:1.5rem;border-bottom:2px solid #C9A84C;padding-bottom:10px;margin-bottom:20px}}
.clausula{{margin:15px 0;line-height:1.6}}
.clausula h3{{color:#1A237E;font-size:1rem;margin-bottom:5px}}
.assinaturas{{display:flex;justify-content:space-between;margin-top:40px;gap:40px}}
.assinatura{{flex:1}}
.assinatura .linha{{border-top:1px solid #333;margin-top:60px;padding-top:8px;font-size:.85rem;text-align:center}}
.btn-assinar{{background:#1A237E;color:#fff;border:none;padding:12px 24px;border-radius:6px;font-size:1rem;cursor:pointer;display:block;margin:20px auto 0}}
.btn-assinar:hover{{background:#283593}}
.assinado{{color:#2E7D32;font-weight:700;text-align:center;padding:10px;background:#E8F5E9;border-radius:6px;display:none}}
@media(max-width:600px){{.assinaturas{{flex-direction:column}}}}
</style>
</head>
<body>
<div class="paper">
<h1>CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE ENGENHARIA</h1>
<p style="margin-bottom:20px;color:#888">{hoje:%d/%m/%Y}</p>

<div class="clausula">
<h3>CONTRATANTE</h3>
<p>{cliente}</p>
</div>
<div class="clausula">
<h3>CONTRATADA</h3>
<p>BUENOSERV SERVIÇOS DE ENGENHARIA LTDA - CNPJ: 60.490.193/0001-38</p>
</div>
<div class="clausula">
<h3>OBJETO</h3>
<p>{objeto}</p>
</div>
<div class="clausula">
<h3>VALOR</h3>
<p>R$ {valor:,.2f}</p>
</div>
<div class="clausula">
<h3>CONDIÇÕES GERAIS</h3>
<p>O presente contrato rege-se pelas leis brasileiras. Fica eleito o foro de Leme-SP.</p>
</div>

<div id="statusAssinatura" class="assinado">✅ Documento assinado digitalmente</div>

<div class="assinaturas">
<div class="assinatura">
<p><strong>BUENOSERV ENGENHARIA</strong></p>
<button class="btn-assinar" onclick="assinar('buenoserv')" id="btnBuenoserv">Assinar como BUENOSERV</button>
<div class="linha" id="assinaturaBuenoserv"></div>
</div>
<div class="assinatura">
<p><strong>{cliente}</strong></p>
<button class="btn-assinar" onclick="assinar('cliente')" id="btnCliente">Assinar como {cliente}</button>
<div class="linha" id="assinaturaCliente"></div>
</div>
</div>
</div>
<script>
let assinaturas = {{buenoserv: false, cliente: false}};
function assinar(quem) {{
    assinaturas[quem] = true;
    document.getElementById('btn' + quem.charAt(0).toUpperCase() + quem.slice(1)).disabled = true;
    document.getElementById('btn' + quem.charAt(0).toUpperCase() + quem.slice(1)).textContent = '✓ Assinado';
    document.getElementById('assinatura' + quem.charAt(0).toUpperCase() + quem.slice(1)).innerHTML = 'Assinado digitalmente em ' + new Date().toLocaleString('pt-BR');
    if (assinaturas.buenoserv && assinaturas.cliente) {{
        document.getElementById('statusAssinatura').style.display = 'block';
    }}
}}
</script>
</body>
</html>"""
    with open(saida, 'w') as f:
        f.write(html)
    print(f"✅ Contrato click-to-sign: {saida}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: gen_click_sign.py <cliente> <valor> <objeto>")
        sys.exit(1)
    gerar_contrato_html(sys.argv[1], float(sys.argv[2]), sys.argv[3])
