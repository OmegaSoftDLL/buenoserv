#!/usr/bin/env python3
"""BUENOSERV — Gerador de Apresentação Comercial HTML."""

TEMPLATE = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BUENOSERV — Apresentação Comercial</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#0a1628;overflow:hidden;height:100vh}
.slide-container{width:100vw;height:100vh;position:relative;overflow:hidden}
.slides{display:flex;transition:transform .6s cubic-bezier(.4,0,.2,1);height:100%}
.slide{min-width:100vw;height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;padding:60px 80px;color:#e0e0e0;position:relative}
.slide h1{font-size:3em;color:#d4a843;margin-bottom:16px;text-align:center}
.slide h2{font-size:2em;color:#d4a843;margin-bottom:24px;border-bottom:2px solid #d4a843;padding-bottom:12px}
.slide p{font-size:1.15em;color:#b0c0dd;line-height:1.7;max-width:800px;text-align:center}
.slide ul{list-style:none;max-width:700px;width:100%}
.slide ul li{color:#b0c0dd;font-size:1.1em;padding:10px 0 10px 36px;position:relative;border-bottom:1px solid rgba(212,168,67,.1)}
.slide ul li::before{content:"▸";position:absolute;left:0;color:#d4a843;font-size:1.2em}
.nav{position:fixed;bottom:30px;left:50%;transform:translateX(-50%);display:flex;gap:12px;z-index:100;align-items:center}
.nav button{background:rgba(212,168,67,.15);border:1px solid #d4a843;color:#d4a843;width:44px;height:44px;border-radius:50%;font-size:1.2em;cursor:pointer;transition:.3s}
.nav button:hover{background:#d4a843;color:#0a1628}
.nav .dots{display:flex;gap:8px}
.nav .dot{width:10px;height:10px;border-radius:50%;background:rgba(212,168,67,.3);cursor:pointer;transition:.3s}
.nav .dot.active{background:#d4a843;transform:scale(1.3)}
.slide-number{position:fixed;bottom:30px;right:30px;color:rgba(212,168,67,.4);font-size:.9em;z-index:100}
.cover{background:linear-gradient(135deg,#0a1628 0%,#1a2744 50%,#0a1628 100%)}
.cover h1{font-size:4em;letter-spacing:4px}
.cover p{color:#8899bb;font-size:1.3em}
.contact-grid{display:grid;grid-template-columns:1fr 1fr;gap:30px;max-width:700px;width:100%}
.contact-item{background:rgba(212,168,67,.08);border:1px solid rgba(212,168,67,.15);border-radius:12px;padding:20px;text-align:center}
.contact-item .icon{font-size:2em;margin-bottom:8px}
.contact-item .label{color:#8899bb;font-size:.85em}
.contact-item .value{color:#d4a843;font-size:1.05em;font-weight:600}
.services-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;max-width:800px;width:100%}
.service-item{background:rgba(212,168,67,.06);border:1px solid rgba(212,168,67,.12);border-radius:10px;padding:18px;text-align:center}
.service-item .icon{font-size:1.8em;margin-bottom:4px}
.service-item .name{color:#d4a843;font-size:.95em}
.diffs{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;max-width:900px;width:100%}
.diff-item{background:rgba(212,168,67,.06);border:1px solid rgba(212,168,67,.12);border-radius:12px;padding:24px;text-align:center}
.diff-item .icon{font-size:2.4em;margin-bottom:10px}
.diff-item h3{color:#d4a843;font-size:1.05em;margin-bottom:6px}
.diff-item p{font-size:.9em;color:#9aabca}
.cases{display:grid;grid-template-columns:1fr 1fr;gap:16px;max-width:800px;width:100%}
.case-item{background:rgba(212,168,67,.06);border:1px solid rgba(212,168,67,.12);border-radius:10px;padding:16px;text-align:left}
.case-item .title{color:#d4a843;font-size:.95em;font-weight:600}
.case-item .sub{color:#8899bb;font-size:.82em}
.clients{display:flex;flex-wrap:wrap;gap:16px;justify-content:center;max-width:800px}
.clients span{background:rgba(212,168,67,.08);border:1px solid rgba(212,168,67,.15);border-radius:8px;padding:12px 24px;color:#d4a843;font-size:1em}
@media(max-width:700px){.slide{padding:30px 20px}.slide h1{font-size:2em}.cover h1{font-size:2.4em}.services-grid,.diffs,.cases{grid-template-columns:1fr}.contact-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="slide-container">
<div class="slides" id="slides">

<div class="slide cover">
<h1>BUENOSERV</h1>
<p>Engenharia de Alta Tensão & Telecomunicações</p>
<p style="font-size:1em;color:#6a7b9a;margin-top:30px">Soluções Elétricas e de Telecom para o Setor de Energia</p>
</div>

<div class="slide">
<h2>Quem Somos</h2>
<p style="margin-bottom:30px">Fundada por <strong style="color:#d4a843">Ricardo Bueno</strong>, engenheiro com mais de 20 anos de experiência em comissionamento de subestações, telecomunicações e sistemas de proteção.</p>
<ul>
<li>20+ anos de mercado</li>
<li>100+ projetos realizados</li>
<li>Atuação em concessionárias, indústrias e geradoras</li>
<li>Expertise em normas nacionais e internacionais</li>
<li>Equipe técnica certificada</li>
</ul>
</div>

<div class="slide">
<h2>Serviços Principais</h2>
<div class="services-grid">
<div class="service-item"><div class="icon">⚡</div><div class="name">Comissionamento SE 69kV–500kV</div></div>
<div class="service-item"><div class="icon">📡</div><div class="name">Telecom (SDH/DWDM/MPLS-TP/GPON)</div></div>
<div class="service-item"><div class="icon">🛡️</div><div class="name">Proteção e Controle IEC 61850</div></div>
<div class="service-item"><div class="icon">📊</div><div class="name">SCADA / EMS / RTU</div></div>
<div class="service-item"><div class="icon">🏢</div><div class="name">Data Centers TIA-942</div></div>
<div class="service-item"><div class="icon">🔐</div><div class="name">Cybersecurity IEC 62351</div></div>
<div class="service-item"><div class="icon">🔌</div><div class="name">Fibra Óptica (Projeto/OTDR)</div></div>
</div>
</div>

<div class="slide">
<h2>Diferenciais Competitivos</h2>
<div class="diffs">
<div class="diff-item"><div class="icon">🎯</div><h3>Experiência Real</h3><p>Mais de 20 anos em campo, em subestações de todas as tensões</p></div>
<div class="diff-item"><div class="icon">🌐</div><h3>Visão Sistêmica</h3><p>Integração elétrica + telecom + TI — uma só solução</p></div>
<div class="diff-item"><div class="icon">📋</div><h3>Metodologia</h3><p>Processos formais de qualidade com certificação e rastreabilidade</p></div>
<div class="diff-item"><div class="icon">⚡</div><h3>Agilidade</h3><p>Equipe enxuta e experiente, tomada de decisão rápida</p></div>
<div class="diff-item"><div class="icon">🔒</div><h3>Segurança</h3><p>Cultura de segurança como valor fundamental</p></div>
<div class="diff-item"><div class="icon">🤝</div><h3>Parceria</h3><p>Relacionamento de longo prazo com clientes</p></div>
</div>
</div>

<div class="slide">
<h2>Cases de Sucesso</h2>
<div class="cases">
<div class="case-item"><div class="title">⚡ Comissionamento SE 138kV</div><div class="sub">Concessionária XYZ — Energização antecipada, zero não conformidades</div></div>
<div class="case-item"><div class="title">🌐 Anel DWDM 100G MSP</div><div class="sub">Concessionária ABC — Disponibilidade 99.999%</div></div>
<div class="case-item"><div class="title">📟 Integração SCADA IEC 61850</div><div class="sub">Grupo Energético Sul — 3 subestações integradas</div></div>
<div class="case-item"><div class="title">🏭 Data Center TIER III</div><div class="sub">Indústria Química — Certificação TIA-942</div></div>
</div>
</div>

<div class="slide">
<h2>Clientes e Parcerias</h2>
<p style="margin-bottom:30px;color:#8899bb">Empresas que confiam na BUENOSERV</p>
<div class="clients">
<span>Concessionária XYZ</span>
<span>Concessionária ABC</span>
<span>Grupo Energético Sul</span>
<span>Indústria Química Nacional</span>
<span>Operadora de Telecom</span>
<span>Geradora Hidrelétrica</span>
</div>
</div>

<div class="slide">
<h2>Contato</h2>
<div class="contact-grid">
<div class="contact-item"><div class="icon">📧</div><div class="label">E-mail</div><div class="value">ricardo@buenoserv.com.br</div></div>
<div class="contact-item"><div class="icon">📞</div><div class="label">Telefone</div><div class="value">(11) 9XXXX-XXXX</div></div>
<div class="contact-item"><div class="icon">🌍</div><div class="label">Site</div><div class="value">www.buenoserv.com.br</div></div>
<div class="contact-item"><div class="icon">📍</div><div class="label">Localização</div><div class="value">São Paulo — SP</div></div>
</div>
</div>

</div>
</div>

<div class="nav">
<button onclick="prevSlide()">◀</button>
<div class="dots" id="dots"></div>
<button onclick="nextSlide()">▶</button>
</div>
<div class="slide-number" id="slideNumber">1 / 7</div>

<script>
let current=0;const slides=document.querySelectorAll('.slide'),dotsContainer=document.getElementById('dots');
slides.forEach((_,i)=>{const d=document.createElement('div');d.className='dot';d.onclick=()=>goTo(i);dotsContainer.appendChild(d)});
const dots=document.querySelectorAll('.dot');
function goTo(i){current=i;document.getElementById('slides').style.transform='translateX(-'+(current*100)+'vw)';dots.forEach(d=>d.classList.remove('active'));dots[current].classList.add('active');document.getElementById('slideNumber').textContent=(current+1)+' / '+slides.length}
function nextSlide(){goTo((current+1)%slides.length)}
function prevSlide(){goTo((current-1+slides.length)%slides.length)}
document.addEventListener('keydown',e=>{if(e.key==='ArrowRight')nextSlide();if(e.key==='ArrowLeft')prevSlide()});
goTo(0);
</script>
</body>
</html>'''

def main():
    import os
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'site')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'apresentacao.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(TEMPLATE)
    print(f"Apresentação gerada: {os.path.abspath(out_path)}")

if __name__ == '__main__':
    main()
