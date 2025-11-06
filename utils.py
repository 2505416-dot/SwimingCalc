# utils.py
import os
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

os.makedirs("graficos", exist_ok=True)
os.makedirs("relatorios", exist_ok=True)

def gerar_graficos(materiais, custos, custos_fase, area):
    # Quantidade por m²
    quant_por_m2 = {m: q / area for m, q in materiais.items()}
    plt.figure(figsize=(10,6))
    plt.bar(quant_por_m2.keys(), quant_por_m2.values(), color='cornflowerblue')
    plt.xticks(rotation=45, ha='right')
    plt.title("Quantidade de materiais por m²")
    plt.tight_layout()
    plt.savefig("graficos/quantidade_por_m2.png")
    plt.close()

    # Custo por fase
    plt.figure(figsize=(8,8))
    plt.pie(custos_fase.values(), labels=custos_fase.keys(), autopct='%1.1f%%', startangle=90)
    plt.title("Distribuição de custos por fase")
    plt.tight_layout()
    plt.savefig("graficos/custo_por_fase.png")
    plt.close()

    # Custo por material
    sorted_custos = dict(sorted(custos.items(), key=lambda x: x[1], reverse=True))
    plt.figure(figsize=(12,6))
    plt.bar(list(sorted_custos.keys())[:10], list(sorted_custos.values())[:10], color='seagreen')
    plt.xticks(rotation=45, ha='right')
    plt.title("Top 10 custos por material")
    plt.tight_layout()
    plt.savefig("graficos/custo_por_material.png")
    plt.close()

def salvar_excel(dados_projeto, materiais, custos, custos_fase, nome_arquivo="relatorio_piscina.xlsx"):
    caminho = os.path.join("relatorios", nome_arquivo)
    with pd.ExcelWriter(caminho) as writer:
        pd.DataFrame([dados_projeto]).to_excel(writer, sheet_name="Projeto", index=False)
        pd.DataFrame(list(materiais.items()), columns=["Material", "Quantidade"]).to_excel(writer, sheet_name="Materiais", index=False)
        pd.DataFrame(list(custos.items()), columns=["Material", "Custo (R$)"]).to_excel(writer, sheet_name="Custos", index=False)
        pd.DataFrame(list(custos_fase.items()), columns=["Fase", "Custo (R$)"]).to_excel(writer, sheet_name="Custos por Fase", index=False)
    return caminho

def gerar_pdf(dados_projeto, materiais, custos, custos_fase, caminho_pdf="orcamento_piscina.pdf"):
    caminho = os.path.join("relatorios", caminho_pdf)
    doc = SimpleDocTemplate(caminho, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    styles.add(ParagraphStyle(name='Title', fontSize=16, spaceAfter=12, alignment=1))
    story.append(Paragraph(f"Orçamento de Piscina – {dados_projeto.get('Nome_projeto', 'Cliente')}", styles['Title']))

    def add_section(titulo, dados):
        story.append(Paragraph(titulo, styles['Heading2']))
        for k, v in dados.items():
            story.append(Paragraph(f"{k}: {v}", styles['BodyText']))
        story.append(Spacer(1, 12))

    add_section("Dados do Projeto", dados_projeto)
    add_section("Materiais", {k: f"{v:.2f}" for k, v in materiais.items()})
    add_section("Custos por Material (R$)", {k: f"R$ {v:.2f}" for k, v in custos.items()})
    add_section("Custos por Fase (R$)", {k: f"R$ {v:.2f}" for k, v in custos_fase.items()})

    # Gráficos
    for img in ["quantidade_por_m2.png", "custo_por_fase.png", "custo_por_material.png"]:
        img_path = os.path.join("graficos", img)
        if os.path.exists(img_path):
            story.append(Spacer(1, 12))
            story.append(Image(img_path, width=6*inch, height=4*inch))

    story.append(Spacer(1, 20))
    story.append(Paragraph("Etapas do Projeto", styles['Heading2']))
    story.append(Paragraph("""
    1. Alvenaria: estrutura com blocos.
    2. Impermeabilização: proteção contra vazamentos.
    3. Chapisco/Reboco: acabamento base.
    4. Revestimento: estética e funcionalidade.
    5. Acabamento: rejunte e acessórios.
    6. Extras: hidromassagem (se aplicável).
    """, styles['BodyText']))

    doc.build(story)
    return caminho