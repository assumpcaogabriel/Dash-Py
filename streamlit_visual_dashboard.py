import streamlit as st
import pandas as pd
import requests
import altair as alt

st.set_page_config(page_title="Dashboard DevOps - Visual", layout="wide")

st.title("📊 Dashboard DevOps - Análises Visuais")

# 🔍 Parâmetros
st.sidebar.header("📅 Período")
start_date = st.sidebar.date_input("Início")
end_date = st.sidebar.date_input("Fim")

st.sidebar.header("🗂️ Boards")
boards = st.sidebar.text_input("Boards (separados por vírgula)", "App Condor,Max Call")

st.sidebar.header("📌 Planning IDs")
ids_str = st.sidebar.text_area("IDs da Planning (separados por vírgula)", "")

if st.sidebar.button("🔄 Buscar Dados"):
    params = {
        "start": start_date,
        "end": end_date,
        "boards": [b.strip() for b in boards.split(",")],
        "planning_ids": [i.strip() for i in ids_str.split(",") if i.strip()]
    }

    with st.spinner("🔄 Consultando API..."):
        try:
            res = requests.get("http://localhost:8000/api/devops", params=params)
            if res.status_code == 200:
                data = res.json()
                df = pd.DataFrame(data)

                st.success(f"{len(df)} itens carregados da API")
                st.dataframe(df)

                # Gráfico 1: Status por Tamanho
                st.subheader("📈 Quantidade de Itens por Status e T-shirt Size")
                if "status" in df.columns and "tshirt_size" in df.columns:
                    chart1 = alt.Chart(df[df["tshirt_size"].notna()]).mark_bar().encode(
                        x=alt.X("tshirt_size:N", title="Tamanho"),
                        y=alt.Y("count():Q", title="Qtd de Itens"),
                        color="status:N",
                        column="status:N"
                    ).properties(width=120)
                    st.altair_chart(chart1)

                # Gráfico 2: Itens além do estimado
                st.subheader("🚨 Itens Além do Estimado")
                alem_df = df[df["alem_estimado"] == True]
                st.dataframe(alem_df)

                # Gráfico 3: Itens em impedimento
                st.subheader("⛔ Itens em Impedimento")
                imp_df = df[df["impedimento"] == True]
                st.dataframe(imp_df)

            else:
                st.error(f"Erro {res.status_code}: {res.text}")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
else:
    st.info("Preencha os filtros e clique em 'Buscar Dados'")