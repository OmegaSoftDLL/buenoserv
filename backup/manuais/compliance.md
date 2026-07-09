# Manual de Compliance e Validação

## Matriz de Consistência entre Disciplinas

| Disciplina A | Disciplina B | O que verificar |
|--------------|-------------|-----------------|
| Switch (VLANs) | Router (SVIs) | VLANs definidas nos switches têm SVIs correspondentes no roteador |
| Firewall (ACL) | Router (BGP) | Prefixos anunciados não são bloqueados por ACLs de borda |
| Telecom (DWDM) | BOM | Cada transponder, OADM, OLA tem entrada na BOM |
| Telecom (SDH) | DE/PARA | Todo tributário SDH tem DE/PARA mapeado |
| Energia (UPS) | Todas | Soma das cargas ≤ 80% da capacidade da UPS |
| CFTV (câmeras) | Redes (PoE) | Budget PoE do switch ≥ consumo total das câmeras conectadas |
| Cabeamento | Datacenter | Distâncias horizontais ≤ 90m |
| Physical Security | CFTV | Zonas de alarme coincidem com áreas de cobertura de câmeras |

## Tabela de Tolerâncias

| Parâmetro | Aceitável | Crítico |
|-----------|-----------|---------|
| Carga UPS | ≤ 80% | ≥ 90% |
| Distância cabo UTP | ≤ 90m (permanente) | ≤ 100m (canal total) |
| Perda óptica | ≤ budget - 2dB | > budget |
| Temperatura datacenter | 18-27°C | < 15°C ou > 30°C |
| PoE budget switch | ≥ 80% usado | > 100% |
| Aterramento | ≤ 10Ω | > 25Ω |

## Critérios de Aprovação

- **✅ Aprovado:** todos os checks verdes, nenhum vermelho
- **⚠️ Aprovado com Ressalvas:** no máximo 2 amarelos, nenhum vermelho
- **❌ Reprovado:** qualquer vermelho ou 3+ amarelos
