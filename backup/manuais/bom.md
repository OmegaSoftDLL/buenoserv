# Manual da Lista de Materiais (BOM)

## Estrutura de Codificação

### Formato Geral de TAG
```
[PREFIXO-DISCIPLINA]-[CATEGORIA]-[SEQ]-[LOCAL]
```
Onde:
- **PREFIXO-DISCIPLINA:** SW, RT, FW, SDH, DWDM, MW, ANT, UPS, GEN, CAM, ACS, RCK
- **CATEGORIA:** CORE, DIST, ACC, AGG, OTM, OADM, OLA, ODF, DDF, PNL, MOD, SFP, CBL
- **SEQ:** numérico 3 dígitos (001-999)
- **LOCAL:** sigla do site (SJC, CWB, SPO, RJO, BSB, REC, FOR, MAO)

### Exemplos
- `SW-CORE-001-SJC` — Switch core 001 em São José dos Campos
- `DWDM-OTM-001-SPO` — Terminal DWDM 001 em São Paulo
- `SDH-ADM-001-CWB` — ADM SDH 001 em Curitiba
- `UPS-001-RJO` — Nobreak 001 no Rio de Janeiro
- `CAM-IP-001-SPO` — Câmera IP 001 em São Paulo

## Hierarquia de BOM

```
BOM MESTRE DO PROJETO (BOM-PROJETO-00)
├── BOM-REDE (BOM-PROJETO-REDE-00)
├── BOM-TELECOM (BOM-PROJETO-TELECOM-00)
├── BOM-ENERGIA (BOM-PROJETO-ENERGIA-00)
├── BOM-SEGURANCA (BOM-PROJETO-SEGURANCA-00)
└── BOM-DCL (BOM-PROJETO-DCL-00)
```

## Colunas Detalhadas

| Campo | Descrição | Obrigatório | Formato |
|-------|-----------|-------------|---------|
| ITEM | Número sequencial | Sim | 001, 002... |
| TAG | Código do item | Sim | SW-CORE-001-SJC |
| CÓDIGO | Part number fabricante | Sim | Conforme fabricante |
| DESCRIÇÃO | Nome técnico do item | Sim | Texto |
| FABRICANTE | Nome do fabricante | Sim | Cisco, Huawei, Padtec, etc. |
| MODELO | Modelo exato | Sim | Conforme datasheet |
| QTD | Quantidade | Sim | Número inteiro |
| UNIDADE | Unidade de medida | Sim | un, pc, m, km, par, kit, conjunto |
| OBS | Observações técnicas | Não | Texto livre |
| FORNECEDOR | Empresa fornecedora | Não | Nome + CNPJ |
| LEAD TIME | Prazo de entrega | Não | Dias corridos |
| VALOR UNIT. | Preço unitário estimado | Não | R$ |
| VALOR TOTAL | Preço total estimado | Não | R$ = QTD × VALOR UNIT. |
| GARANTIA | Prazo de garantia | Não | Meses |
| LINK DATASHEET | URL do datasheet | Não | URL |

## Regras de Negócio

1. **Revisão**: BOM deve ser revisada sempre que houver alteração de projeto
2. **Aprovação**: BOM master deve ser aprovada pelo arquiteto de rede (@network-architect) e pelo cliente
3. **Rastreabilidade**: cada TAG na BOM deve ter correspondência no desenho DXF (atributo ou layer)
4. **Consistência**: somatório de BOMs por disciplina deve fechar com o BOM master
5. **Fornecedores alternativos**: quando possível, indicar mínimo 2 fornecedores homologados
6. **Itens críticos**: marcar com flag "CRÍTICO" itens com lead time > 60 dias
7. **Sobressalentes**: incluir 10% de sobressalente para conectores, fusíveis, módulos SFP

## Templates por Disciplina

### BOM de Rede
```
| ITEM | TAG | CÓDIGO | DESCRIÇÃO | FABRICANTE | MODELO | QTD | UNID. |
|---|---|---|---|---|---|---|---|
```

### BOM de Telecom
```
| ITEM | TAG | CÓDIGO | DESCRIÇÃO | FABRICANTE | MODELO | QTD | UNID. |
|---|---|---|---|---|---|---|---|
```

### BOM de Energia
```
| ITEM | TAG | CÓDIGO | DESCRIÇÃO | FABRICANTE | MODELO | QTD | UNID. |
|---|---|---|---|---|---|---|---|
```
