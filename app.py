import streamlit as st
import pandas as pd

# --------- Traduções estáticas ----------
TRANSLATIONS = {
    "Professional Data Insights for Business": {
        "en": "Professional Data Insights for Business",
        "pt": "Inteligência de Dados Profissional para Negócios"
    },
    "Market Opportunities by Sector": {
        "en": "Market Opportunities by Sector",
        "pt": "Oportunidades de Mercado por Setor"
    },
    "ROI Simulator": {
        "en": "ROI Simulator",
        "pt": "Simulador de ROI"
    },
    "Employees": {
        "en": "Employees",
        "pt": "Funcionários"
    },
    "Manual Hours / Week per Employee": {
        "en": "Manual Hours / Week per Employee",
        "pt": "Horas manuais / semana por funcionário"
    },
    "Cost per Hour (BRL)": {
        "en": "Cost per Hour (BRL)",
        "pt": "Custo por hora (BRL)"
    },
    "Initial Investment (BRL)": {
        "en": "Initial Investment (BRL)",
        "pt": "Investimento Inicial (BRL)"
    },
    "Calculate": {
        "en": "Calculate",
        "pt": "Calcular"
    },
    "Annual Saving": {
        "en": "Annual Saving",
        "pt": "Economia Anual"
    },
    "Payback": {
        "en": "Payback",
        "pt": "Payback"
    },
    "years": {
        "en": "years",
        "pt": "anos"
    }
}

def translate(term, lang):
    """Retorna a tradução do termo ou o termo original se não houver tradução."""
    return TRANSLATIONS.get(term, {}).get(lang, term)

# -------- Carregamento dos dados (com tratamento) ----------
csv_path = "static/"
try:
    data = {
        "oportunidades": pd.read_csv(csv_path + "oportunidades_por_setor.csv"),
        "saas": pd.read_csv(csv_path + "mercado_saas_brasil.csv"),
        "meddic": pd.read_csv(csv_path + "funil_vendas_meddic.csv"),
        "roi_auto": pd.read_csv(csv_path + "roi_por_automacao.csv"),
    }
except Exception as e:
    st.error(f"Erro ao carregar arquivos CSV: {e}")
    st.stop()

# -------- Interface Streamlit ---------
st.set_page_config(page_title="DataSolutions Pro")
lang = st.sidebar.radio("Idioma / Language", ("English (UK)", "Português (BR)"))
lang = "pt" if lang == "Português (BR)" else "en"

st.title("DataSolutions Pro")

st.markdown(f"**{translate('Professional Data Insights for Business', lang)}**")

# Tabela
st.header(translate("Market Opportunities by Sector", lang))
st.dataframe(data["oportunidades"], use_container_width=True)

# Simulador de ROI
st.header(translate("ROI Simulator", lang))

with st.form("form_simulador"):
    col1, col2 = st.columns(2)
    emp = col1.number_input(translate("Employees", lang), min_value=1, value=10)
    hour_week = col2.number_input(translate("Manual Hours / Week per Employee", lang), min_value=1.0, value=40.0)
    cost_per_hour = col1.number_input(translate("Cost per Hour (BRL)", lang), min_value=1.0, value=35.0)
    invest = col2.number_input(translate("Initial Investment (BRL)", lang), min_value=1.0, value=150000.0)
    submitted = st.form_submit_button(translate("Calculate", lang))

if submitted:
    annual_saving = emp * hour_week * cost_per_hour * 52 * 0.7
    payback = invest / annual_saving if annual_saving else 0
    roi = ((annual_saving - invest) / invest) * 100 if invest else 0
    st.info(f"{translate('Annual Saving', lang)}: R$ {annual_saving:,.0f}")
    st.info(f"{translate('Payback', lang)}: {payback:.1f} {translate('years', lang)}")
    st.info(f"ROI: {roi:.1f}%")

st.caption("© 2025 DataSolutions Pro")
