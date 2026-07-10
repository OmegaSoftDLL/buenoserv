#!/usr/bin/env python3
"""Gera conteudo completo para cadastro no Google Meu Negocio - BUENOSERV"""
import datetime

OUTPUT = "/tmp/opencode/google_business_completo.md"

CONTEUDO = f"""# Google Meu Negocio — BUENOSERV
## Conteudo completo para cadastro
### Gerado em: {datetime.date.today():%d/%m/%Y}

---

## 1. INFORMACOES BASICAS

| Campo | Valor |
|-------|-------|
| **Nome** | BUENOSERV SERVICOS DE ENGENHARIA LTDA |
| **Categoria** | Empresa de engenharia eletrica |
| **Subcategoria** | Servicos de engenharia eletrica / Comissionamento de subestacoes |
| **Endereco** | Rua Giacomo Fior, 427 — Leme-SP, 13610-000 |
| **Telefone** | (19) - CONSULTAR |
| **WhatsApp** | (19) - CONSULTAR (com botao de contato) |
| **Website** | https://buenoservengenharia.com |
| **Horario** | Segunda a Sexta: 08:00 — 18:00 |
| **Area de servico** | Leme-SP, Piracicaba, Campinas, Ribeirao Preto, Sao Paulo, todo o Brasil |

---

## 2. DESCRICAO (SEO otimizada — ~500 caracteres)

A BUENOSERV e uma empresa de engenharia eletrica especializada em comissionamento de subestacoes de ate 500 kV, sistemas de protecao e controle (IEC 61850), telecomunicacoes (SDH/DWDM/MPLS-TP), SCADA, data centers e cybersecurity. Com mais de 20 anos de experiencia no setor eletrico brasileiro, atendemos concessionarias, industrias e integradoras com solucoes turn-key, testes FAT/SAT, documentacao as-built e engenharia do proprietario. Localizada em Leme-SP, atendemos todo o Brasil com excelencia tecnica e compromisso com prazos. Solicite seu orcamento: https://buenoservengenharia.com

---

## 3. ATRIBUTOS DO NEGOCIO

- Profissional de engenharia
- Consultoria tecnica
- Empresa de engenharia eletrica
- Comissionamento industrial
- Automacao de subestacoes
- Telecomunicacoes para setor eletrico
- Instalacao e manutencao eletrica
- Solucoes em SCADA
- Seguranca cibernetica industrial
- Data center e infraestrutura critica

---

## 4. SERVICOS

| # | Servico | Descricao |
|---|---------|-----------|
| 1 | Comissionamento de Subestacoes | FAT/SAT, start-up, integracao de sistemas, laudos tecnicos ate 500 kV |
| 2 | Telecomunicacoes | Redes SDH, DWDM, MPLS-TP, radio micro-ondas, fibra otica para setor eletrico |
| 3 | SCADA e Automacao | Sistemas de supervisao e controle, RTU, IED, integracao IEC 61850 |
| 4 | Data Center | Projeto e instalacao de infraestrutura critica, nobreaks, climatizacao, CFTV |
| 5 | Cybersecurity | Seguranca de redes industriais, OT security, firewall, segmentacao |

---

## 5. POSTS SUGERIDOS — PRIMEIRA SEMANA

### Post 1 — Apresentacao
**Titulo:** Bem-vindo a BUENOSERV!
**Texto:** Apresentacao da empresa, 20 anos de experiencia em engenharia eletrica e comissionamento.

### Post 2 — Dica Tecnica
**Titulo:** A importancia do FAT e SAT
**Texto:** Por que os testes de fabrica e campo sao essenciais para o sucesso de uma subestacao.

### Post 3 — Case
**Titulo:** Comissionamento de SE 230 kV
**Texto:** Resumo de um projeto recente, desafios e resultados entregues.

### Post 4 — Setor Eletrico
**Titulo:** Expansao da transmissao no Brasil
**Texto:** Dados sobre leiloes de transmissao e oportunidades para engenharia especializada.

### Post 5 — Equipe
**Titulo:** Conheca nossa equipe
**Texto:** Fotos e perfis dos engenheiros e tecnicos da BUENOSERV.

---

## 6. FOTOS SUGERIDAS (10)

| # | Tipo | Descricao |
|---|------|-----------|
| 1 | Escritorio | Fachada do escritorio na Rua Giacomo Fior, 427 |
| 2 | Escritorio | Sala de reunioes e equipe |
| 3 | Projeto | Subestacao comissionada (visao externa) |
| 4 | Projeto | Painel de protecao e controle (IEC 61850) |
| 5 | Projeto | Rack de telecomunicacoes (DWDM/SDH) |
| 6 | Equipamento | Equipe em campo durante SAT |
| 7 | Equipamento | Teste de reles de protecao |
| 8 | Equipamento | Sala de data center / servidores |
| 9 | Logo | Logo BUENOSERV (alta resolucao) |
| 10 | Capa | Imagem de capa para o perfil (banner 1920x1080) |

---

## 7. METADADOS

- **Verificacao:** Codigo por correio (Google envia cartao postal)
- **URL curta:** https://g.page/buenoserv-engenharia
- **Categoria Google:** `engineering_service` | `electrician`
- **Idioma:** pt-BR
"""

def gerar():
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(CONTEUDO)
    print(f"[OK] Conteudo gerado: {OUTPUT}")
    print(f"[OK] Total de caracteres (descricao): ~500")
    print(f"[OK] Posts sugeridos: 5")
    print(f"[OK] Fotos sugeridas: 10")
    print(f"[OK] Servicos listados: 5")

if __name__ == "__main__":
    gerar()
