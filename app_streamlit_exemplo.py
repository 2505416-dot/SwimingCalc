"""
EXEMPLO DE CÓDIGO STREAMLIT CORRIGIDO
Este arquivo mostra como adaptar o código para funcionar no Streamlit Cloud
e resolver o erro NameError na linha 78.
"""

import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple

# =======================
# CONFIGURAÇÃO DA PÁGINA
# =======================

st.set_page_config(
    page_title="Calculadora de Piscinas",
    page_icon="🏊",
    layout="wide"
)

st.title("🏊 Calculadora de Orçamento para Piscinas")
st.markdown("---")


# =======================
# FUNÇÕES DE CÁLCULO (importadas do código original)
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


def calcular_tudo(
    dados_piscina: Dict[str, float],
    custo_unitario: Dict[str, float],
    extras: Dict[str, float],
    preco_agua_por_litro: float = 0.01,
    caminhoes_enchimento: int = 3,
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

    if dados_piscina.get("Usar_revestimento") == "Revestimento":
        materiais["Revestimento (m²)"] = calcular_revestimento(area)

    if dados_piscina.get("Vai_hidromassagem") == "Sim":
        materiais["Hidromassagem (kit)"] = 1

    if dados_piscina.get("Tipo_piscina") == "Vinilico":
        area_manta = (area + perimetro * profundidade) * 1.10
        materiais["Manta Vinilica (m²)"] = round(area_manta, 3)

    # Enchimento da piscina
    volume_m3 = largura * comprimento * profundidade
    litros = volume_m3 * 1000
    materiais["Volume de água (L)"] = round(litros, 2)
    materiais["Caminhões de enchimento (unidades)"] = caminhoes_enchimento
    tempo_horas = litros / (caminhoes_enchimento * fluxo_mangueira_lph)
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
# INTERFACE STREAMLIT
# =======================

# Sidebar para entrada de dados
st.sidebar.header("📋 Dados do Projeto")

nome_projeto = st.sidebar.text_input("Nome do projeto ou cliente", value="Projeto 1")
num_pessoas = st.sidebar.number_input("Quantas pessoas compõem a família?", min_value=1, value=4)
vai_hidromassagem = st.sidebar.selectbox("O projeto inclui hidromassagem?", ["Não", "Sim"])
tipo_piscina = st.sidebar.selectbox("Tipo de piscina", ["Azulejo", "Vinilico"])

st.sidebar.header("📏 Dimensões da Piscina")
largura = st.sidebar.number_input("Largura da piscina (m)", min_value=0.1, value=5.0, step=0.1)
comprimento = st.sidebar.number_input("Comprimento da piscina (m)", min_value=0.1, value=10.0, step=0.1)

fundo_declive = st.sidebar.selectbox("Piscina com fundo em declive?", ["Não", "Sim"])
if fundo_declive == "Sim":
    profundidade_min = st.sidebar.number_input("Profundidade mínima (m)", min_value=0.1, value=1.0, step=0.1)
    profundidade_max = st.sidebar.number_input("Profundidade máxima (m)", min_value=0.1, value=2.0, step=0.1)
else:
    profundidade_min = profundidade_max = st.sidebar.number_input("Profundidade (m)", min_value=0.1, value=1.5, step=0.1)

usar_revestimento = st.sidebar.selectbox("Tipo de acabamento", ["Revestimento", "Outro"])

# Botão para calcular
calcular_btn = st.sidebar.button("🧮 Calcular Orçamento", type="primary")

# =======================
# PROCESSAMENTO E EXIBIÇÃO
# =======================

# SOLUÇÃO DO ERRO: Inicializar variáveis ANTES de usar
# Isso evita o NameError quando a página carrega pela primeira vez
if 'materiais' not in st.session_state:
    st.session_state.materiais = {}
if 'custos' not in st.session_state:
    st.session_state.custos = {}
if 'custos_fase' not in st.session_state:
    st.session_state.custos_fase = {}
if 'area' not in st.session_state:
    st.session_state.area = 0

# Quando o botão é clicado, executar os cálculos
if calcular_btn:
    # Preparar dados
    dados_piscina = {
        "Nome_projeto": nome_projeto,
        "Num_pessoas_familia": num_pessoas,
        "Vai_hidromassagem": vai_hidromassagem,
        "Tipo_piscina": tipo_piscina,
        "Largura": largura,
        "Comprimento": comprimento,
        "Profundidade_min": profundidade_min,
        "Profundidade_max": profundidade_max,
        "Usar_revestimento": usar_revestimento
    }
    
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
    
    # EXECUTAR CÁLCULOS E ARMAZENAR NO SESSION_STATE
    materiais, custos, custos_fase, area = calcular_tudo(
        dados_piscina, custo_unitario, extras,
        preco_agua_por_litro=0.01,
        caminhoes_enchimento=3,
        fluxo_mangueira_lph=1000.0
    )
    
    # Salvar no session_state para persistir entre reruns
    st.session_state.materiais = materiais
    st.session_state.custos = custos
    st.session_state.custos_fase = custos_fase
    st.session_state.area = area
    st.session_state.dados_piscina = dados_piscina

# =======================
# EXIBIÇÃO DOS RESULTADOS
# =======================

# SOLUÇÃO: Agora custos_fase SEMPRE existe (inicializado ou calculado)
if st.session_state.custos_fase:
    st.success("✅ Orçamento calculado com sucesso!")
    
    # Exibir resumo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Área da Piscina", f"{st.session_state.area:.2f} m²")
    with col2:
        total_custos = sum(st.session_state.custos.values())
        st.metric("Custo Total", f"R$ {total_custos:,.2f}")
    with col3:
        volume = st.session_state.materiais.get("Volume de água (L)", 0)
        st.metric("Volume de Água", f"{volume:,.0f} L")
    
    st.markdown("---")
    
    # Tabs para organizar informações
    tab1, tab2, tab3 = st.tabs(["📊 Custos por Fase", "🧱 Materiais", "💰 Custos Detalhados"])
    
    with tab1:
        st.subheader("Distribuição de Custos por Fase")
        # LINHA 78 ORIGINAL DO ERRO - AGORA CORRIGIDA
        st.dataframe(
            pd.DataFrame(list(st.session_state.custos_fase.items()), columns=["Fase", "Custo (R$)"]),
            use_container_width=True
        )
        
        # Gráfico de custos por fase
        fig, ax = plt.subplots(figsize=(10, 6))
        cores = sns.color_palette("pastel")
        ax.barh(list(st.session_state.custos_fase.keys()), 
                list(st.session_state.custos_fase.values()), 
                color=cores[1])
        ax.set_xlabel("Custo (R$)")
        ax.set_title("Distribuição de custos por fase")
        st.pyplot(fig)
    
    with tab2:
        st.subheader("Lista de Materiais Necessários")
        st.dataframe(
            pd.DataFrame(list(st.session_state.materiais.items()), columns=["Material", "Quantidade"]),
            use_container_width=True
        )
    
    with tab3:
        st.subheader("Custos Detalhados por Material")
        st.dataframe(
            pd.DataFrame(list(st.session_state.custos.items()), columns=["Material", "Custo (R$)"]),
            use_container_width=True
        )

else:
    st.info("👈 Preencha os dados no painel lateral e clique em 'Calcular Orçamento'")


# =======================
# FOOTER
# =======================
st.markdown("---")
st.markdown("**Desenvolvido com Streamlit** | Calculadora de Orçamento para Piscinas v1.0")
