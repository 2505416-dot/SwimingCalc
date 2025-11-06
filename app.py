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