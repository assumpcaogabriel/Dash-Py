import streamlit as st
import pandas as pd
import altair as alt
import datetime
from azure_devops_api import get_teams, get_iterations, filter_iterations_by_date, get_work_items_by_iteration, get_work_items_details, parse_work_items

st.set_page_config(page_title="DevOps Insights (Azure API)", layout="wide")
st.title("📊 Dashboard DevOps - Integração Direta com Azure DevOps API")

st.sidebar.header("🗂️ Configuração")

try:
    teams = get_teams()
    team_names = [t['name'] for t in teams]
    selected_teams = st.sidebar.multiselect("Selecione os Boards", team_names, default=team_names[:1])

    start_date = st.sidebar.date_input("Data de início", datetime.date(2025, 3, 17))
    end_date = st.sidebar.date_input("Data de fim", datetime.date(2025, 3, 28))

    all_iterations = {}
    for team in selected_teams:
        iterations = get_iterations(team)
        filtered = filter_iterations_by_date(iterations, start_date, end_date)
        all_iterations[team] = filtered

    selected_iterations = {}
    for team, iterations in all_iterations.items():
        options = [it["path"] for it in iterations]
        selected = st.sidebar.multiselect(f"Iterations de {team}", options, default=options)
        selected_iterations[team] = selected

    st.sidebar.markdown("---")
    st.sidebar.write("Clique abaixo para carregar os dados.")
    if st.sidebar.button("🔄 Carregar Work Items"):
        all_ids = []
        for team, iterations in selected_iterations.items():
            for iteration_path in iterations:
                ids = get_work_items_by_iteration(team, iteration_path)
                all_ids.extend(ids)

        if not all_ids:
            st.warning("Nenhum item encontrado para os filtros selecionados.")
        else:
            raw_items = get_work_items_details(all_ids)
            df = pd.DataFrame(parse_work_items(raw_items))

            st.success(f"✅ {len(df)} itens carregados.")
            st.dataframe(df)

            # Gráfico
            if "Tamanho" in df.columns and "Estado" in df.columns:
                chart = alt.Chart(df[df["Tamanho"].notna()]).mark_bar().encode(
                    x=alt.X("Tamanho:N", title="T-shirt Size"),
                    y=alt.Y("count():Q", title="Quantidade"),
                    color="Estado:N",
                    column="Estado:N"
                ).properties(width=120)
                st.altair_chart(chart)

except Exception as e:
    st.error(f"Erro ao conectar na API do Azure DevOps: {e}")