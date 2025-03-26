import streamlit as st
import pandas as pd
import altair as alt
import re
from io import BytesIO
from datetime import date

st.set_page_config(page_title="DevOps Dashboard - Upload", layout="wide")
st.title("📊 Dashboard DevOps - Upload de Planning + DevOps (.xlsx)")

st.sidebar.header("📤 Upload dos Arquivos")
planning_file = st.sidebar.file_uploader("📁 Upload da Planning (.xlsx)", type=["xlsx"])
devops_file = st.sidebar.file_uploader("📁 Upload do DevOps (.xlsx)", type=["xlsx"])

# Função para extrair IDs estimados
def extrair_ids_estimada(df):
    if "Card" in df.columns:
        cards = df["Card"].astype(str)
        ids = re.findall(r"(\d+)", " ".join(cards))
        return sorted(set(ids), key=int)
    return []

# Função para classificar status com base no tipo e nos filhos
def classificar_status(row, filhos_map):
    estado = row["Estado"]
    tipo = row["Tipo"]
    if tipo in ["Bug", "Task", "Improvement"]:
        return {
            "New": "Na fila",
            "Active": "Em desenvolvimento",
            "Resolved": "Em testes",
            "Ready": "Em testes",
            "Under Review": "Em testes",
            "On Impediment": "Em impedimento",
            "Closed": "Concluído"
        }.get(estado, "Na fila")
    elif tipo == "User Story":
        filhos_status = filhos_map.get(str(row["ID"]), [])
        if not filhos_status or all(s == "New" for s in filhos_status):
            return "Na fila"
        if any(s == "On Impediment" for s in filhos_status):
            return "Em impedimento"
        if any(s in ["Resolved", "Ready", "Under Review"] for s in filhos_status):
            return "Em testes"
        if any(s == "Active" for s in filhos_status):
            return "Em desenvolvimento"
        if all(s == "Closed" for s in filhos_status):
            return "Concluído"
    return "Na fila"

if planning_file and devops_file:
    st.success("📁 Arquivos carregados com sucesso!")
    planning_df = pd.read_excel(planning_file, header=3)
    devops_df = pd.read_excel(devops_file, sheet_name="Planilha1", header=1)

    ids_estimados = extrair_ids_estimada(planning_df)
    devops_df["ID"] = devops_df["ID"].astype(str)
    devops_df["Parent"] = devops_df["Parent"].astype(str)
    devops_df = devops_df.rename(columns={
        "Work Item Type": "Tipo", "Title": "Titulo",
        "Assigned To": "Responsavel", "State": "Estado",
        "Iteration Path": "IterationPath"
    })

    filhos_map = devops_df.groupby("Parent")["Estado"].apply(list).to_dict()
    devops_df["Status"] = devops_df.apply(lambda row: classificar_status(row, filhos_map), axis=1)
    devops_df["Estimado"] = devops_df["ID"].isin(ids_estimados)
    devops_df["PaiEstimado"] = devops_df["Parent"].isin(ids_estimados)
    bugs_aleatorios_ids = devops_df[devops_df["Titulo"].str.lower().str.contains("bugs aleatórios", na=False)]["ID"].tolist()

    def alem_do_estimado(row):
        if row["Status"] == "Na fila":
            return False
        if row["Estimado"] or row["PaiEstimado"]:
            return False
        if row["Parent"] in bugs_aleatorios_ids:
            return False
        return True

    devops_df["AlemDoEstimado"] = devops_df.apply(alem_do_estimado, axis=1)
    devops_df["Impedimento"] = devops_df["Status"] == "Em impedimento"

    st.markdown("### 🔍 Visão Geral dos Itens")
    st.dataframe(devops_df)

    st.markdown("### 📊 Itens por Status e T-shirt Size")
    if "Tamanho" in devops_df.columns:
        size_chart = alt.Chart(devops_df[devops_df["Tamanho"].notna()]).mark_bar().encode(
            x="Tamanho:N",
            y="count():Q",
            color="Status:N",
            column="Status:N"
        ).properties(width=100)
        st.altair_chart(size_chart)

    st.markdown("### ⛔ Itens em Impedimento")
    st.dataframe(devops_df[devops_df["Impedimento"]])

    st.markdown("### 🚨 Itens Além do Estimado")
    st.dataframe(devops_df[devops_df["AlemDoEstimado"]])

else:
    st.info("Faça o upload dos arquivos para iniciar a análise.")