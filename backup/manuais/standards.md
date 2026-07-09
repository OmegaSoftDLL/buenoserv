# Catálogo Central de Normas — Projetos de Rede e Telecom

## Normas Brasileiras (ABNT / ANATEL / INMETRO)

| Sigla | Descrição | Aplicação |
|-------|-----------|-----------|
| **NBR 5410** | Instalações elétricas de baixa tensão | Aterramento, alimentação de racks e equipamentos |
| **NBR 5419** | Proteção contra descargas atmosféricas (SPDA) | Aterramento de torres e equipamentos externos |
| **NBR 6492** | Representação de projetos de arquitetura | Layer naming, simbologia |
| **NBR 10068** | Folhas de desenho — leiaute e dimensões | Formatos A0-A4 |
| **NBR 10582** | Carimbo (legenda) para desenhos técnicos | Campos obrigatórios |
| **NBR 14565** | Cabeamento estruturado para edifícios comerciais e data centers | Topologia, distâncias, performance |
| **NBR 16415** | Cabeamento de telecomunicações para residências | SCS residencial |
| **NBR ISO/IEC 27001** | Sistema de gestão de segurança da informação | Segurança da rede |
| **ANATEL Res. 242/2000** | Homologação de equipamentos de telecomunicações | Certificação de equipamentos |
| **ANATEL Res. 477/2007** | Regulamento de uso do espectro radioelétrico | Radiofrequência |
| **ANATEL Res. 680/2017** | Alteração do regulamento de certificação | Homologação |
| **CGI.br Res. 2009/003** | Regras para PTT Metro / IX.br | BGP peering |
| **LGPD (Lei 13.709/2018)** | Proteção de dados pessoais | Logs, acesso, privacidade |
| **Marco Civil (Lei 12.965/2014)** | Direitos e deveres na internet | Guarda de logs, neutralidade |
| **NR 10** | Segurança em eletricidade | Instalação de racks e equipamentos |
| **NR 17** | Ergonomia | Postos de trabalho NOC/SOC |
| **NR 26** | Sinalização de segurança | Identificação de riscos |
| **IN MJSP 46/2022** | Segurança cibernética em órgãos públicos | Firewall, logging, resposta a incidentes |

## Normas Internacionais

### IEEE
| Padrão | Descrição |
|--------|-----------|
| **IEEE 802.1D** | Spanning Tree Protocol |
| **IEEE 802.1Q** | VLAN tagging |
| **IEEE 802.1w** | Rapid STP |
| **IEEE 802.1s** | Multiple STP |
| **IEEE 802.1X** | Port-based Network Access Control |
| **IEEE 802.3** | Ethernet (10M-100G) |
| **IEEE 802.3af/at/bt** | PoE / PoE+ / PoE++ |
| **IEEE 802.1AB** | LLDP |
| **IEEE 802.1ag** | Connectivity Fault Management |

### ITU-T
| Padrão | Descrição |
|--------|-----------|
| **G.652** | Fibra óptica monomodo padrão |
| **G.654** | Fibra óptica para DWDM |
| **G.691** | Sistemas DWDM com amplificadores ópticos |
| **G.692** | DWDM com canais ópticos |
| **G.703** | Interfaces digitais PDH |
| **G.707** | Hierarquia SDH |
| **G.709** | OTN (Optical Transport Network) |
| **G.783** | Equipamentos SDH |
| **G.783** | Características dos equipamentos SDH |
| **G.803** | Arquitetura SDH |
| **G.957** | Interfaces ópticas SDH |
| **G.958** | Sistemas de linha digital SDH |
| **K.27** | Proteção contra sobretensão em telecom |
| **K.56** | Proteção de estações rádio base |

### ISO/IEC
| Padrão | Descrição |
|--------|-----------|
| **ISO/IEC 11801** | Cabeamento genérico para edifícios |
| **ISO/IEC 24702** | Cabeamento industrial |
| **ISO/IEC 27001** | ISMS — Gestão de segurança |
| **ISO/IEC 27002** | Controles de segurança |
| **ISO 14673** | Símbolos para redes |

### NIST
| Padrão | Descrição |
|--------|-----------|
| **SP 800-41r1** | Guidelines on Firewalls |
| **SP 800-94** | Guide to IDS/IPS |
| **CSF** | Cybersecurity Framework |

### ANSI/TIA
| Padrão | Descrição |
|--------|-----------|
| **TIA-568** | Cabeamento estruturado |
| **TIA-569** | Pathways and Spaces |
| **TIA-606-B** | Administration |
| **TIA-607** | Grounding and Bonding |
| **TIA-942** | Data Center Infrastructure |
| **TIA-222** | Antenna tower standards |

### Padrões de Mercado
| Fabricante | Plataformas |
|------------|-------------|
| Cisco | IOS, IOS-XE, NX-OS, ASA, FTD |
| Juniper | JunOS |
| Huawei | VRP, CE, NE |
| HPE Aruba | AOS-CX, ProVision |
| Fortinet | FortiOS |
| Palo Alto | PAN-OS |
| MikroTik | RouterOS |
| Nokia/Alcatel | SR OS (TiMOS) |
| Ericsson | RBS, MINI-LINK |
| NEC | MW, SDH, DWDM |
| Padtec | DWDM LightPad |

## Convenções de Layer (NBR 6492 + Personalizado)

### Arquitetura / Civil
| Layer | Cor | Descrição |
|-------|-----|-----------|
| A-WALL | 7 | Paredes |
| A-DOOR | 3 | Portas |
| A-WIND | 4 | Janelas |
| A-STAIR | 6 | Escadas |
| A-ROOF | 5 | Telhados |
| A-DIM | 2 | Cotas |
| A-TEXT | 2 | Textos |

### Rede (Network)
| Layer | Cor | Descrição |
|-------|-----|-----------|
| NET-CORE | 1 | Core/switches/routers |
| NET-ACCESS | 4 | Switches de acesso |
| NET-SERVER | 5 | Servidores |
| NET-WIRELESS | 6 | Wireless/AP |
| NET-PATCH | 4 | Patch panels |
| NET-CABLE | 3 | Cabos UTP |
| NET-FIBER | 6 | Cabos ópticos |
| NET-POWER | 7 | Energia |
| NET-RACK | 7 | Racks |
| NET-TEXT | 2 | Textos |

### Telecom
| Layer | Cor | Descrição |
|-------|-----|-----------|
| TEL-SDH | 5 | Equipamentos SDH |
| TEL-PDH | 6 | Equipamentos PDH |
| TEL-DWDM | 1 | Equipamentos DWDM |
| TEL-OTM | 1 | Optical Terminal Mux |
| TEL-OADM | 4 | Optical ADM |
| TEL-OLA | 6 | Optical Line Amp |
| TEL-FIBER | 6 | Fibras ópticas |
| TEL-RADIO | 1 | Rádio enlaces |
| TEL-MW | 1 | Microwave |
| TEL-MOBILE | 6 | Rede móvel |
| TEL-DAS | 4 | DAS |
| TEL-EXTERNAL | 8 | Planta externa |
| TEL-PROTECTION | 3 | Proteção |

### Segurança
| Layer | Cor | Descrição |
|-------|-----|-----------|
| SEC-CORE | 1 | Core de segurança |
| SEC-FIREWALL | 1 | Firewalls |
| SEC-CAMERA | 3 | Câmeras |
| SEC-ACCESS | 3 | Controle de acesso |
| SEC-SENSOR | 2 | Sensores |
| SEC-ZONE | 2 | Zonas de segurança |
| SEC-TEXT | 2 | Textos |

### Elétrica / Energia
| Layer | Cor | Descrição |
|-------|-----|-----------|
| E-POWER | 7 | Alimentação elétrica |
| E-UPS | 2 | Nobreak/UPS |
| E-GEN | 2 | Gerador |
| E-GROUND | 3 | Aterramento |
| E-TEXT | 2 | Textos |

## Padrão de Folhas A3 — Especificação Técnica

### 1. Regras Gerais

- O formato **A3 (420 × 297 mm)** é **obrigatório** para todos os projetos de rede, telecom, segurança e elétrica.
- Exceções (A2, A1, A0 ou desenhos em escala não usual) somente mediante aprovação da coordenação técnica.
- Todas as pranchas devem ser geradas a partir do template DXF oficial (`scripts/a3_template_gen.py`).
- Unidade padrão: milímetros (INSUNITS = 4).

### 2. Margens — ISO A3

| Margem | Valor | Finalidade |
|--------|-------|------------|
| Esquerda | **25 mm** | Encadernação / arquivamento (filing margin) |
| Direita | **10 mm** | Margem livre |
| Superior | **10 mm** | Margem livre |
| Inferior | **10 mm** | Margem livre |

O retângulo interno (moldura) é desenhado do ponto **(25, 10)** ao ponto **(410, 287)**.

### 3. Layout do Carimbo (Legenda / Título)

Conforme NBR 16752 (antiga NBR 10582) e ISO 7200. Posicionado no **canto inferior direito** da moldura, flush com as linhas inferior e direita.

**Dimensões totais:** 178 mm (largura) × 24 mm (altura).

| Linha | Altura | Descrição |
|-------|--------|-----------|
| Superior | 12 mm | Identificação do projeto |
| Média | 6 mm | Responsáveis / escala / identificação da prancha |
| Inferior | 6 mm | Quadro de revisões |

#### Linha Superior (12 mm)

| Box | Largura | Conteúdo |
|-----|---------|----------|
| 1 | 40 mm | **EMPRESA / LOGO** — retângulo para logotipo (40×12 mm) com guias diagonais |
| 2 | 30 mm | **CONTRATANTE / CLIENTE** |
| 3 | 40 mm | **PROJETO / OBRA** |
| 4 | 68 mm | **CONTEÚDO DA FOLHA / DESCRIÇÃO** |

#### Linha Média (6 mm)

| Box | Largura | Conteúdo |
|-----|---------|----------|
| 5 | 30 mm | **AUTOR / PROJETISTA** (nome, data, assinatura) |
| 6 | 30 mm | **VERIFICADO POR** |
| 7 | 30 mm | **APROVADO POR** |
| 8 | 30 mm | **ESCALA** |
| 9 | 58 mm | **Nº PRANCHA / IDENTIFICAÇÃO** |

#### Linha Inferior — Quadro de Revisões (6 mm)

| Box | Largura | Conteúdo |
|-----|---------|----------|
| Rev. | 10 mm | Número da revisão |
| Descrição / Modificação | 60 mm | Descrição da alteração |
| Data | 20 mm | Data da revisão |
| Aprov. | 20 mm | Aprovador da revisão |
| Nº Folha | 68 mm | Nº da folha (subdividido em "Nº" e "/Total", 34 mm cada) |

### 4. Marcas de Centro

Quatro marcas, uma no ponto médio de cada lado da moldura, estendendo-se **5 mm para fora**:

| Posição | Coordenada | Linha |
|---------|-----------|-------|
| Superior | (217.5, 287) → (217.5, 292) | Vertical |
| Inferior | (217.5, 10) → (217.5, 5) | Vertical |
| Esquerda | (25, 148.5) → (20, 148.5) | Horizontal |
| Direita | (410, 148.5) → (415, 148.5) | Horizontal |

### 5. Marcas de Corte (Trim Marks)

Presentes nos **quatro cantos** da moldura, estendendo-se **10 mm** para fora da moldura em ambas as direções:

- Canto inferior esquerdo: (15, 10) → (25, 10) e (25, 10) → (25, 0)
- Canto inferior direito: (410, 10) → (420, 10) e (410, 10) → (410, 0)
- Canto superior esquerdo: (15, 287) → (25, 287) e (25, 287) → (25, 297)
- Canto superior direito: (410, 287) → (420, 287) e (410, 287) → (410, 297)

### 6. Sistema de Referência em Grade (Opcional)

Marcações leves a cada **50 mm** nas bordas superior e esquerda da moldura, numeradas sequencialmente (1, 2, 3…).

- Borda superior: traços de 3 mm para baixo a partir da linha da moldura.
- Borda esquerda: traços de 3 mm para a direita a partir da linha da moldura.

### 7. Posição do Logotipo

O logotipo da empresa deve ser inserido:

- **Opção A (padrão):** dentro do Box 1 do carimbo (canto superior esquerdo da legenda), substituindo o placeholder.
- **Opção B (alternativa):** canto superior direito da folha, fora da moldura, mantendo 10 mm de margem superior e direita.

### 8. Convenção de Nomenclatura de Arquivos

```
<CLIENTE>-<PROJETO>-<TIPO>-<N PRANCHA>_R<REV>.dwg
```

Exemplo: `EMBRATEL-REDE-METRO-TOPOLOGIA-001_R00.dwg`

| Campo | Descrição |
|-------|-----------|
| CLIENTE | Sigla ou nome abreviado do contratante |
| PROJETO | Código ou nome reduzido do projeto |
| TIPO | Tipo de desenho (PLANTA, TOPOLOGIA, DETALHE, DIAGRAMA) |
| N PRANCHA | Número sequencial com 3 dígitos (001, 002…) |
| REV | Revisão com 2 dígitos (R00, R01…) |

### 9. Dobragem e Arquivamento

- Pranchas A3 devem ser arquivadas **sem dobragem** sempre que possível.
- Quando houver necessidade de encadernação com formato A4, dobrar conforme NBR 10068:
  1. Dobrar ao meio no sentido da largura (210 mm).
  2. Dobrar novamente ao meio (148 mm × 210 mm) com a legenda visível na face externa.
- O carimbo deve permanecer visível após a dobragem (canto inferior direito da folha dobrada).

### 10. Empilhamento de Pranchas / Revisões Parciais

- Revisões parciais: alterar apenas a(s) prancha(s) afetada(s); atualizar o **quadro de revisões** de cada prancha modificada.
- O número da folha ("Nº Folha" / "Total") deve refletir a paginação do conjunto completo.
- Revisões devem seguir sequência alfanumérica: R00 (primeira emissão), R01, R02… R99.
- O campo "REV." da linha inferior do carimbo deve conter a revisão atual da prancha.

### 11. Cores de Plotagem (CTB) para Moldura

| Layer | Cor | Plot Style | Espessura (mm) | Finalidade |
|-------|-----|------------|----------------|------------|
| MARGEM | 7 (branco/preto) | Normal | 0.50 | Moldura externa e margens |
| LEGENDA | 7 (branco/preto) | Normal | 0.35 | Carimbo e divisórias |
| TEXTO | 7 (branco/preto) | Normal | 0.18 | Textos do carimbo |

- Arquivo CTB padrão: `MONO_ESPESSURAS.ctb` (monocromático, variação por espessura).
- Todas as entidades de moldura e legenda devem ser plotadas em **preto (100% K)**.

## Símbolos Padrão (network_symbols.py)
Disponíveis via MCP DXF Server:
- **Rede:** router, switch, firewall, server, wifi_ap, patch_panel, server_rack, ups
- **Telecom:** antenna, fiber_route, fiber_splice, cell_tower, radio_link
- **Segurança:** camera, access_point, sensor, security_zone, nvr
- **Cabos:** cat5e, cat6, cat6a, cat7, cat8, om1, om3, om4, os2
