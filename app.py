# app.py
import streamlit as st
import os
from calculos import calcular_tudo
from utils import gerar_graficos, salvar_excel, gerar_pdf

# Configuração
st.set_page_config(page_title="Orçamento de Piscina", layout="wide")
st.title("📊 Calculadora de Orçamento de Piscina")
st.markdown("Desenvolvido para profissionais da construção civil")

# Dados de custo (ajustáveis)
CUSTO_UNITARIO = {
    "Blocos": 1.5,
    "Tela para Quina Vivas (caixas)": 50,
    "Impermeabilizante1 (caixas 20kg)": 100,
    "Impermeabilizante2 (caixas 20kg)": 150,
    "Cimento (sacos)": 25,
    "Areia (m³)": 150,
    "Ligmassa (litros)": 10,
    "Revestimento (m²)": 60,
    "Argamassa ACIII (kg)": 20,
    "Rejunte Acrílico (sacos)": 40,
    "Espaçadores (unidades)": 0.1
}
EXTRAS = {"custo_hidromassagem_kit": 5000}

# Formulário
st.header("📝 Dados do Projeto")
nome = st.text_input("Nome do cliente ou projeto")
num_pessoas = st.number_input("Número de pessoas na família", min_value=1, value=4)
largura = st.number_input("Largura da piscina (m)", min_value=1.0, value=4.0, step=0.5)
comprimento = st.number_input("Comprimento da piscina (m)", min_value=1.0, value=8.0, step=0.5)

fundo_declive = st.checkbox("Piscina com fundo em declive?")
if fundo_declive:
    prof_min = st.number_input("Profundidade mínima (m)", min_value=0.8, value=1.2, step=0.1)
    prof_max = st.number_input("Profundidade máxima (m)", min_value=1.2, value=1.8, step=0.1)
else:
    prof_min = prof_max = st.number_input("Profundidade (m)", min_value=1.0, value=1.5, step=0.1)

revestimento = st.checkbox("Usar revestimento (azulejo, pastilha etc.)?")
hidromassagem = st.checkbox("Incluir hidromassagem?")

if st.button("🧮 Calcular Orçamento"):
    with st.spinner("Calculando materiais e custos..."):
        materiais, custos, custos_fase, area = calcular_tudo(
            largura, comprimento, prof_min, prof_max,
            usar_revestimento=revestimento,
            hidromassagem=hidromassagem,
            custo_unitario=CUSTO_UNITARIO,
            extras=EXTRAS
        )

        # Salvar dados do projeto
        dados_projeto = {
            "Nome_projeto": nome,
            "Num_pessoas_familia": num_pessoas,
            "Largura": largura,
            "Comprimento": comprimento,
            "Profundidade_min": prof_min,
            "Profundidade_max": prof_max,
            "Revestimento": "Sim" if revestimento else "Não",
            "Hidromassagem": "Sim" if hidromassagem else "Não",
            "Área (m²)": round(area, 2)
        }

        # Gerar gráficos
        gerar_graficos(materiais, custos, custos_fase, area)

        # Mostrar resumo
        st.subheader("💰 Custo Total Estimado")
        custo_total = sum(custos.values())
        st.metric("Valor total", f"R$ {custo_total:,.2f}")

        # Tabelas
        st.subheader("📋 Custos por Fase")
        st.dataframe(pd.DataFrame(list(custos_fase.items()), columns=["Fase", "Custo (R$)"]))

        st.subheader("📦 Materiais Necessários")
        st.dataframe(pd.DataFrame(list(materiais.items()), columns=["Material", "Quantidade"]))

        # Botões de download
        excel_path = salvar_excel(dados_projeto, materiais, custos, custos_fase)
        pdf_path = gerar_pdf(dados_projeto, materiais, custos, custos_fase)

        with open(excel_path, "rb") as f:
            st.download_button("📥 Baixar Excel", f, file_name="relatorio_piscina.xlsx")

        with open(pdf_path, "rb") as f:
            st.download_button("📄 Baixar PDF", f, file_name="orcamento_piscina.pdf")

        # Gráficos embutidos
        st.subheader("📈 Visualizações")
        cols = st.columns(3)
        with cols[0]:
            st.image("graficos/quantidade_por_m2.png", use_container_width=True)
        with cols[1]:
            st.image("graficos/custo_por_fase.png", use_container_width=True)
        with cols[2]:

            st.image("graficos/custo_por_material.png", use_container_width=True)
            import math
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from typing import Dict, Tuple


# =======================
# FUNÇÕES DE CÁLCULO DE MATERIAIS
# =======================

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


# =======================
# ENTRADA DE DADOS
# =======================

def coletar_dados_projeto() -> Dict[str, float]:
    print("\n=== PROJETO PARA UMA FAMÍLIA ===")
    dados = {}
    dados["Nome_projeto"] = input("Nome do projeto ou cliente: ").strip()
    dados["Num_pessoas_familia"] = int(input("Quantas pessoas compõem a família? "))
    dados["Vai_hidromassagem"] = input("O projeto inclui hidromassagem? (Sim/Não): ").strip().capitalize()

    tipo = input("Tipo de piscina (Azulejo/Vinilico): ").strip().lower()
    dados["Tipo_piscina"] = "Vinilico" if tipo.startswith("v") else "Azulejo"

    print("\n=== DADOS DA PISCINA ===")
    dados["Largura"] = float(input("Largura da piscina (m): ").replace(',', '.'))
    dados["Comprimento"] = float(input("Comprimento da piscina (m): ").replace(',', '.'))

    fundo_declive = input("Piscina com fundo em declive? (Sim/Não): ").strip().capitalize()
    if fundo_declive == "Sim":
        dados["Profundidade_min"] = float(input("Profundidade mínima (m): ").replace(',', '.'))
        dados["Profundidade_max"] = float(input("Profundidade máxima (m): ").replace(',', '.'))
    else:
        dados["Profundidade_min"] = dados["Profundidade_max"] = float(input("Profundidade (m): ").replace(',', '.'))

    dados["Usar_revestimento"] = input("Tipo de acabamento (Revestimento/Outro): ").strip().capitalize()
    if dados["Usar_revestimento"] == "Revestimento":
        dados["Revestimento_largura_peca"] = float(input("Largura da peça (m): ").replace(',', '.'))
        dados["Revestimento_altura_peca"] = float(input("Altura da peça (m): ").replace(',', '.'))

    return dados


# =======================
# CÁLCULOS PRINCIPAIS
# =======================

def calcular_tudo(
    dados_piscina: Dict[str, float],
    custo_unitario: Dict[str, float],
    extras: Dict[str, float],
    preco_agua_por_litro: float = 0.01,
    caminhos_enchimento: int = 3,
    fluxo_mangueira_lph: float = 1000.0
) -> Tuple[Dict[str, float], Dict[str, float], Dict[str, float], float]:

    largura = dados_piscina["Largura"]
    comprimento = dados_piscina["Comprimento"]
    profundidade = (dados_piscina["Profundidade_min"] + dados_piscina["Profundidade_max"]) / 2

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

    if dados_piscina["Usar_revestimento"] == "Revestimento":
        materiais["Revestimento (m²)"] = calcular_revestimento(area)

    if dados_piscina["Vai_hidromassagem"] == "Sim":
        materiais["Hidromassagem (kit)"] = 1

    if dados_piscina["Tipo_piscina"] == "Vinilico":
        area_manta = (area + perimetro * profundidade) * 1.10
        materiais["Manta Vinilica (m²)"] = round(area_manta, 3)

    # Enchimento da piscina
    volume_m3 = largura * comprimento * profundidade
    litros = volume_m3 * 1000
    materiais["Volume de água (L)"] = round(litros, 2)
    materiais["Caminhões de enchimento (unidades)"] = caminhos_enchimento
    tempo_horas = litros / (caminhos_enchimento * fluxo_mangueira_lph)
    materiais["Tempo estimado enchimento (h)"] = round(tempo_horas, 2)

    custos = {m: materiais[m] * custo_unitario.get(m, 0) for m in materiais}
    custos["Custo de enchimento (R$)"] = round(litros * preco_agua_por_litro, 2)

    if "Hidromassagem (kit)" in materiais:
        custos["Hidromassagem (kit)"] = extras.get("custo_hidromassagem_kit", 0)

    fases = {
        "Alvenaria": ["Blocos", "Cimento (sacos)"],
        "Impermeabilização": ["Impermeabilizante1 (caixas 20kg)", "Impermeabilizante2 (caixas 20kg)"],
        "Chapisco/Reboco": ["Cimento (sacos)", "Areia (m³)", "Argamassa ACIII (kg)"],
        "Revestimento": ["Revestimento (m²)", "Argamassa ACIII (kg)"],
        "Acabamento": ["Rejunte Acrílico (sacos)", "Espaçadores (unidades)"],
        "Enchimento": ["Custo de enchimento (R$)"]
    }
    if "Hidromassagem (kit)" in materiais:
        fases["Extras"] = ["Hidromassagem (kit)"]

    custos_fase = {fase: sum(custos.get(m, 0) for m in mats) for fase, mats in fases.items()}
    return materiais, custos, custos_fase, area


# =======================
# GRÁFICOS
# =======================

def gerar_graficos(materiais, custos, custos_fase, area):
    import seaborn as sns
    import numpy as np
    os.makedirs("graficos", exist_ok=True)

    # Paleta pastel suave
    cores = sns.color_palette("pastel")

    if area == 0:
        quant_por_m2 = {m: 0 for m in materiais}
    else:
        quant_por_m2 = {m: q / area for m, q in materiais.items()}

    # === NOVO: Gráfico em LINHAS com escala logarítmica ===
    plt.figure(figsize=(10, 6))
    x = np.arange(len(quant_por_m2))
    y = list(quant_por_m2.values())
    labels = list(quant_por_m2.keys())

    plt.plot(x, y, color="#9BBFE0", linewidth=2.5, marker="o", markersize=6,
             markerfacecolor="#F6BD60", alpha=0.8)

    plt.yscale("log")  # Escala logarítmica pra mostrar todos os valores
    plt.xticks(x, labels, rotation=80, ha="right")
    plt.grid(True, which="both", linestyle="--", alpha=0.4)
    plt.title("Quantidade de Materiais por m²", fontsize=13, fontweight="bold")
    plt.ylabel("Quantidade (escala logarítmica)")
    plt.tight_layout()
    plt.savefig("graficos/quantidade_por_m2.png", dpi=200)
    plt.close()

    # === Custos por fase ===
    plt.figure(figsize=(10,6))
    plt.barh(list(custos_fase.keys()), list(custos_fase.values()), color=cores[1])
    plt.xlabel("Custo (R$)")
    plt.title("Distribuição de custos por fase", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig("graficos/custos_por_fase.png", dpi=200)
    plt.close()

    # === Custos por material ===
    plt.figure(figsize=(12,6))
    sorted_custos = dict(sorted(custos.items(), key=lambda x: x[1], reverse=True))
    plt.barh(list(sorted_custos.keys()), list(sorted_custos.values()), color=cores[2])
    plt.xlabel("Custo (R$)")
    plt.title("Custos por material (inclui enchimento da piscina)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig("graficos/custos_por_material.png", dpi=200)
    plt.close()

    # === Enchimento da Piscina (mantém o que já estava lindo) ===
    if "Custo de enchimento (R$)" in custos:
        fig, ax = plt.subplots(figsize=(9, 5))
        parametros = ["Volume (L)", "Caminhões", "Tempo (h)", "Custo (R$)"]
        valores = [
            materiais.get("Volume de água (L)", 0),
            materiais.get("Caminhos de enchimento (unidades)", 0),
            materiais.get("Tempo estimado enchimento (h)", 0),
            custos.get("Custo de enchimento (R$)", 0)
        ]
        bar_colors = ["#A8DADC", "#F6BD60", "#BDB2FF", "#FFADAD"]
        barras = ax.bar(parametros, valores, color=bar_colors, alpha=0.8, edgecolor="gray")
        ax.set_title("Enchimento da Piscina - Volume, Caminhões, Tempo e Custo", fontsize=14, fontweight="bold")
        ax.set_ylabel("Valores de enchimento", fontsize=11)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        for i, b in enumerate(barras):
            altura = b.get_height()
            ax.text(b.get_x() + b.get_width()/2, altura + (altura*0.02 if altura>0 else 0.1),
                    f"{valores[i]:,.2f}", ha="center", va="bottom", fontsize=10, color="#333")
        plt.tight_layout()
        plt.savefig("graficos/custo_enchimento.png", dpi=200)
        plt.close(fig)


# =======================
# RELATÓRIOS
# =======================

def salvar_excel(dados_piscina, materiais, custos, custos_fase):
    with pd.ExcelWriter("relatorio_piscina.xlsx") as writer:
        pd.DataFrame([dados_piscina]).to_excel(writer, sheet_name="Dados_Projeto", index=False)
        pd.DataFrame(list(materiais.items()), columns=["Material", "Quantidade"]).to_excel(writer, sheet_name="Materiais", index=False)
        pd.DataFrame(list(custos.items()), columns=["Material", "Custo (R$)"]).to_excel(writer, sheet_name="Custos", index=False)
        pd.DataFrame(list(custos_fase.items()), columns=["Fase", "Custo (R$)"]).to_excel(writer, sheet_name="Custos_Fase", index=False)
    print("✅ Planilha Excel gerada: relatorio_piscina.xlsx")


def gerar_pdf(dados_piscina, materiais, custos, custos_fase):
    doc = SimpleDocTemplate("orcamento_piscina.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    styles.add(ParagraphStyle(name='TitleStyle', fontSize=16, alignment=1, spaceAfter=12))
    story.append(Paragraph(f"Orçamento de Piscina - {dados_piscina['Nome_projeto']}", styles['TitleStyle']))

    def add_section(title: str, data: Dict[str, float]):
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"<b>{title}</b>", styles['Heading3']))
        for k, v in data.items():
            story.append(Paragraph(f"{k}: {v}", styles['Normal']))

    add_section("Dados do Projeto", dados_piscina)
    add_section("Materiais", materiais)
    add_section("Custos por Material (R$)", {k: f"{v:.2f}" for k, v in custos.items()})
    add_section("Custos por Fase (R$)", {k: f"{v:.2f}" for k, v in custos_fase.items()})

    if "Volume de água (L)" in materiais:
        enchimento_data = {
            "Volume de água (L)": materiais.get("Volume de água (L)", 0),
            "Caminhos de enchimento (unidades)": materiais.get("Caminhos de enchimento (unidades)", 0),
            "Tempo estimado enchimento (h)": materiais.get("Tempo estimado enchimento (h)", 0),
            "Custo de enchimento (R$)": custos.get("Custo de enchimento (R$)", 0)
        }
        add_section("Informações de Enchimento", enchimento_data)


    # Adiciona gráficos
    for img_name in sorted(os.listdir("graficos")):
        img_path = os.path.join("graficos", img_name)
        if os.path.exists(img_path):
            story.append(Spacer(1, 12))
            story.append(Image(img_path, width=6*inch, height=4*inch))

    story.append(Spacer(1, 12))
    story.append(Paragraph("✅ Relatório gerado automaticamente com gráficos em tons pastéis para melhor visualização.", styles['Normal']))

    doc.build(story)
    print("✅ PDF gerado: orcamento_piscina.pdf")


# =======================
# EXECUÇÃO PRINCIPAL
# =======================

def main():
    custo_unitario = {
        "Blocos": 1.5,
        "Tela para Quina Vivas (caixas)": 50,
        "Impermeabilizante1 (caixas 20kg)": 100,
        "Impermeabilizante2 (caixas 20kg)": 150,
        "Cimento (sacos)": 25,
        "Areia (m³)": 150,
        "Ligmassa (litros)": 10,
        "Revestimento (m²)": 60,
        "Argamassa ACIII (kg)": 20,
        "Rejunte Acrílico (sacos)": 40,
        "Espaçadores (unidades)": 0.1
    }
    extras = {"custo_hidromassagem_kit": 5000}

    preco_agua_por_litro = 0.01
    caminhos_enchimento = 3
    fluxo_mangueira_lph = 1000.0

    dados_piscina = coletar_dados_projeto()
    materiais, custos, custos_fase, area = calcular_tudo(
        dados_piscina, custo_unitario, extras,
        preco_agua_por_litro, caminhos_enchimento, fluxo_mangueira_lph
    )

    gerar_graficos(materiais, custos, custos_fase, area)
    salvar_excel(dados_piscina, materiais, custos, custos_fase)
    gerar_pdf(dados_piscina, materiais, custos, custos_fase)


if __name__ == "__main__":
    main()
