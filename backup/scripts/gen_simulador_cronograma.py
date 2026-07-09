#!/usr/bin/env python3
"""Simulador de cronograma — Monte Carlo PERT/CPM"""
import random, json, sys, datetime
from statistics import mean, stdev

def pert_3ponto(otimista, provavel, pessimista):
    """PERT: duração esperada = (O + 4P + PES) / 6"""
    return (otimista + 4 * provavel + pessimista) / 6

def pert_desvio(pessimista, otimista):
    """Desvio padrão PERT"""
    return (pessimista - otimista) / 6

def simular_monte_carlo(tarefas, n_simulacoes=1000, confianca=0.95):
    """
    tarefas: lista de dicts {"nome": str, "otimista": dias, "provarel": dias, "pessimista": dias}
    """
    resultados = []
    for _ in range(n_simulacoes):
        total = 0
        for t in tarefas:
            # Triangular distribution (mais realista que PERT puro)
            dur = random.triangular(t["otimista"], t["pessimista"], t["provarel"])
            total += dur
        resultados.append(total)
    
    media = mean(resultados)
    desvio = stdev(resultados)
    p50 = sorted(resultados)[int(n_simulacoes * 0.5)]
    p80 = sorted(resultados)[int(n_simulacoes * 0.8)]
    p95 = sorted(resultados)[int(n_simulacoes * 0.95)]
    
    print(f"\n{'='*55}")
    print(f"  SIMULAÇÃO DE CRONOGRAMA — MONTE CARLO")
    print(f"  {n_simulacoes} simulações | {len(tarefas)} tarefas")
    print(f"{'='*55}")
    print(f"  {'Tarefa':<25} {'PESS':>6} {'OTIM':>6} {'PROV':>6} {'PERT':>6}")
    print(f"  {'─'*49}")
    for t in tarefas:
        pert = pert_3ponto(t["otimista"], t["provarel"], t["pessimista"])
        print(f"  {t['nome'][:24]:<24} {t['pessimista']:>6.0f} {t['otimista']:>6.0f} {t['provarel']:>6.0f} {pert:>6.1f}")
    print(f"  {'─'*49}")
    print(f"  Duração esperada (PERT): {sum(pert_3ponto(t['otimista'],t['provarel'],t['pessimista']) for t in tarefas):.1f} dias")
    print(f"  Média Monte Carlo: {media:.1f} dias (σ={desvio:.1f})")
    print(f"  P50 (mediana): {p50:.1f} dias")
    print(f"  P80: {p80:.1f} dias")
    print(f"  P95: {p95:.1f} dias")
    print(f"{'='*55}")

if __name__ == "__main__":
    # Exemplo: comissionamento de SE
    tarefas = [
        {"nome": "Levantamento de campo", "otimista": 3, "provarel": 5, "pessimista": 10},
        {"nome": "Projeto executivo", "otimista": 10, "provarel": 15, "pessimista": 25},
        {"nome": "BOM e suprimentos", "otimista": 5, "provarel": 10, "pessimista": 20},
        {"nome": "Obra civil", "otimista": 15, "provarel": 25, "pessimista": 40},
        {"nome": "Montagem eletromecânica", "otimista": 10, "provarel": 20, "pessimista": 35},
        {"nome": "Cabeamento fibra/cobre", "otimista": 5, "provarel": 10, "pessimista": 15},
        {"nome": "Comissionamento", "otimista": 5, "provarel": 10, "pessimista": 20},
        {"nome": "SAT e handover", "otimista": 2, "provarel": 5, "pessimista": 10},
    ]
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 1000
    simular_monte_carlo(tarefas, n)
