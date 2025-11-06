# calculos.py
import math
from typing import Dict, Tuple

def calcular_area(largura: float, comprimento: float) -> float:
    return largura * comprimento

def calcular_perimetro(largura: float, comprimento: float) -> float:
    return 2 * (largura + comprimento)

def calcular_blocos(area: float) -> float:
    return area * 12.5

def calcular_tela(perimetro: float, profundidade: float) -> float:
    return (perimetro + 4 * profundidade) / 5

def calcular_impermeabilizante1(area: float) -> int:
    return math.ceil(area / 9)

def calcular_impermeabilizante2(area: float) -> int:
    return math.ceil(area / 4)

def calcular_cimento(area: float) -> float:
    return (0.013 + 0.038 + 0.14) * area / 50

def calcular_areia(area: float) -> float:
    return (0.065 + 0.004 + 0.025) * area

def calcular_ligmassa(area: float) -> float:
    return (0.0026 + 0.05) * area

def calcular_revestimento(area: float) -> float:
    return area

def calcular_argamassa(area: float) -> float:
    return 0.45 * area

def calcular_rejunte(area: float) -> float:
    return 0.05 * area / 20

def calcular_espacadores(area: float) -> float:
    return 12 * area

def calcular_tudo(
    largura: float,
    comprimento: float,
    profundidade_min: float,
    profundidade_max: float,
    usar_revestimento: bool,
    hidromassagem: bool,
    custo_unitario: Dict[str, float],
    extras: Dict[str, float]
) -> Tuple[Dict[str, float], Dict[str, float], Dict[str, float], float]:
    
    profundidade = (profundidade_min + profundidade_max) / 2
    area = calcular_area(largura, comprimento)
    perimetro = calcular_perimetro(largura, comprimento)

    materiais = {
        "Blocos": calcular_blocos(area),
        "Tela para Quina Vivas (caixas)": calcular_tela(perimetro, profundidade),
        "Impermeabilizante1 (caixas 20kg)": calcular_impermeabilizante1(area),
        "Impermeabilizante2 (caixas 20kg)": calcular_impermeabilizante2(area),
        "Cimento (sacos)": calcular_cimento(area),
        "Areia (m³)": calcular_areia(area),
        "Ligmassa (litros)": calcular_ligmassa(area),
        "Argamassa ACIII (kg)": calcular_argamassa(area),
        "Rejunte Acrílico (sacos)": calcular_rejunte(area),
        "Espaçadores (unidades)": calcular_espacadores(area)
    }

    if usar_revestimento:
        materiais["Revestimento (m²)"] = calcular_revestimento(area)

    if hidromassagem:
        materiais["Hidromassagem (kit)"] = 1

    # Custos por material
    custos = {}
    for mat, q in materiais.items():
        if mat == "Hidromassagem (kit)":
            custos[mat] = extras.get("custo_hidromassagem_kit", 0)
        else:
            custos[mat] = q * custo_unitario.get(mat, 0)

    # Fases
    fases = {
        "Alvenaria": ["Blocos", "Cimento (sacos)"],
        "Impermeabilização": ["Impermeabilizante1 (caixas 20kg)", "Impermeabilizante2 (caixas 20kg)"],
        "Chapisco/Reboco": ["Cimento (sacos)", "Areia (m³)", "Argamassa ACIII (kg)"],
        "Revestimento": ["Revestimento (m²)", "Argamassa ACIII (kg)"],
        "Acabamento": ["Rejunte Acrílico (sacos)", "Espaçadores (unidades)"]
    }
    if hidromassagem:
        fases["Extras"] = ["Hidromassagem (kit)"]

    custos_fase = {}
    for fase, mats in fases.items():
        custos_fase[fase] = sum(custos.get(m, 0) for m in mats)

    return materiais, custos, custos_fase, area