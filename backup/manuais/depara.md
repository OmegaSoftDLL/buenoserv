# Manual DE/PARA de Interligação Telecom

## Glossário de Conexões

| Termo | Definição |
|-------|-----------|
| DE/PARA | Mapeamento da origem (DE) para o destino (PARA) de cada conexão |
| Jumper | Cabo curto para interconexão entre equipamentos ou painéis |
| Pig tail | Cabo com conector em uma ponta e fusão na outra (ODF) |
| Patch cord | Cabo com conectores em ambas as pontas |
| Circuito | Conexão lógica fim-a-fim entre dois pontos |
| Lambda (λ) | Comprimento de onda óptico (ITU-T grid) |
| OCH | Optical Channel — circuito óptico no DWDM |
| ODU | Optical Data Unit (OTN) |
| VCAT | Virtual Concatenation (SDH) |
| LCAS | Link Capacity Adjustment Scheme |

## Convenções de Grid ITU-T

### DWDM — 100GHz Grid (C-Band)
| Canal | Frequência (THz) | λ (nm) |
|-------|------------------|--------|
| C01 | 196.10 | 1528.77 |
| C02 | 196.05 | 1529.55 |
| ... | ... | ... |
| C80 | 192.10 | 1560.61 |

### DWDM — 50GHz Grid (C-Band)
| Canal | Frequência (THz) | λ (nm) |
|-------|------------------|--------|
| C01 | 196.125 | 1528.38 |
| C02 | 196.075 | 1529.16 |
| ... | ... | ... |
| C96 | 191.325 | 1566.31 |

## Budget Óptico

### Parâmetros Típicos para Cálculo

| Componente | Perda Típica (dB) |
|------------|-------------------|
| Fibra G.652 (por km) | 0.20 - 0.25 |
| Fibra G.652 (por km, 1625nm) | 0.25 - 0.30 |
| Conector SC/APC | 0.15 - 0.30 |
| Conector LC/APC | 0.15 - 0.30 |
| Fusão (splice) | 0.02 - 0.10 |
| OADM drop (add) | 1.5 - 2.5 |
| OLA (EDFA) | Ganho: 15-22 dB |
| Splitter óptico 1:2 | 3.5 |
| Splitter óptico 1:4 | 7.0 |
| Splitter óptico 1:8 | 10.5 |

### Equação de Budget
```
Budget = Ptx - Prx - Somatório(Perdas) - Margem
```
Onde:
- Ptx: potência de lançamento do transponder (dBm)
- Prx: sensibilidade do receptor (dBm)
- Margem: 2–3 dB de segurança

## Etiquetagem

### Padrão de Rótulo para Jumpers / Patch Cords
```
┌─────────────────────────────┐
│ A: SJC01-ODF01-P01         │
│ λ: C21 (1550.12nm)         │
│ ─────────────────────────── │
│ B: SJC01-OTM01-LC1-RX      │
│ PERDA: 0.45dB              │
└─────────────────────────────┘
```

### Cores de Conectores (Padrão TIA-568 / IEC)
| Cor | Tipo |
|-----|------|
| Azul | PC / UPC (multimodo) |
| Verde | APC (monomodo, angulado) |
| Bege | PC (monomodo) |
| Aqua | OM3/OM4 (laser-optimized) |
| Violeta | OM5 (wideband) |
| Amarelo | SM (monomodo, PC) |

## Validação Automática

Ao gerar um DE/PARA, verificar automaticamente:
1. **Lambdas duplicados** na mesma fibra
2. **Portas duplicadas** (mesma porta usada em 2 circuitos)
3. **Perda excessiva** (budget excedido)
4. **Circuitos sem rota diversa** (quando proteção requerida)
5. **Conectores incompatíveis** (APC vs UPC no mesmo segmento)
6. **Tipos de fibra inconsistentes** (G.652 vs G.655 no mesmo link)
