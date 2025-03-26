import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard DevOps", layout="wide")

st.title("📊 Dashboard Ágil - DevOps Insights")

# Upload das planilhas
st.sidebar.header("📁 Enviar Planilhas")
planning_file = st.sidebar.file_uploader("Upload da Planning (.xlsx)", type=["xlsx"])
devops_file = st.sidebar.file_uploader("Upload da Planilha do DevOps (.xlsx)", type=["xlsx"])

if planning_file and devops_file:
    # Leitura das planilhas
    planning_df = pd.read_excel(planning_file)
    devops_df = pd.read_excel(devops_file)

    st.success("✅ Arquivos carregados com sucesso!")

    # Filtros básicos
    boards = devops_df["Board"].dropna().unique().tolist() if "Board" in devops_df.columns else []
    sprints = devops_df["Sprint"].dropna().unique().tolist() if "Sprint" in devops_df.columns else []

    board_sel = st.sidebar.selectbox("🔎 Selecionar Board", boards) if boards else None
    sprint_sel = st.sidebar.selectbox("📆 Selecionar Sprint", sprints) if sprints else None

    # Aplicar filtros
    filtered_df = devops_df.copy()
    if board_sel:
        filtered_df = filtered_df[filtered_df["Board"] == board_sel]
    if sprint_sel:
        filtered_df = filtered_df[filtered_df["Sprint"] == sprint_sel]

    st.subheader("📋 Itens Filtrados")
    st.dataframe(filtered_df)

    st.markdown("---")
    st.subheader("📌 Itens da Planning")
    st.dataframe(planning_df)

    st.markdown("🔧 Regras de negócio e análises avançadas serão aplicadas aqui...")

else:
    st.info("Envie os dois arquivos para iniciar a análise.")