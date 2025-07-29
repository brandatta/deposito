import streamlit as st
import pandas as pd
import mysql.connector
import hashlib

# Configuración general
st.set_page_config(page_title="Mapa del Depósito Visual", layout="wide")
st.title("📦 Plano del Depósito con SKUs y cantidades")

# Conexión MySQL
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["app_marco_new"]["host"],
        user=st.secrets["app_marco_new"]["user"],
        password=st.secrets["app_marco_new"]["password"],
        database=st.secrets["app_marco_new"]["database"],
        port=3306,
    )

@st.cache_data
def load_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM mapa_deposito", conn)
    conn.close()
    return df

df = load_data()

# Validar columnas
if not {'Sector', 'cantidad', 'codigo'}.issubset(df.columns):
    st.error("La tabla debe tener las columnas: Sector, cantidad, codigo")
    st.stop()

# Estado del modal
if "mostrar_modal" not in st.session_state:
    st.session_state.mostrar_modal = False
    st.session_state.codigo_modal = ""
    st.session_state.sector_modal = ""

# Filtrar primeros sectores
sectores = df['Sector'].dropna().unique()[:3]
df = df[df['Sector'].isin(sectores)]

# Agrupar por sector y código
df_grouped = df.groupby(['Sector', 'codigo'], as_index=False)['cantidad'].sum()

# Función color por SKU
def color_por_codigo(codigo):
    return '#' + hashlib.md5(codigo.encode()).hexdigest()[:6]

# ---------- CSS ----------
st.markdown("""
<style>
.grilla {
    display: grid;
    grid-template-columns: 1fr;
    gap: 15px;
    margin-top: 20px;
    justify-items: center;
}
.sector {
    width: 120px;
    height: 120px;
    border: 2px solid black;
    border-radius: 6px;
    padding: 5px;
    background-color: white;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    position: relative;
}
.sector-label {
    font-weight: bold;
    font-size: 13px;
    margin-bottom: 6px;
}
.sku-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    justify-content: center;
}
button.sku {
    width: 36px;
    height: 36px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 13px;
    color: white;
    border: none;
    cursor: pointer;
}
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(0,0,0,0.7);
    z-index: 9999;
    display: flex;
    justify-content: center;
    align-items: center;
}
.modal-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    width: 80%;
    max-height: 80%;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)

# ---------- GRILLA ----------
st.markdown('<div class="grilla">', unsafe_allow_html=True)

for sector in sectores:
    grupo = df_grouped[df_grouped['Sector'] == sector]
    with st.container():
        st.markdown(f'<div class="sector"><div class="sector-label">{sector}</div><div class="sku-container">', unsafe_allow_html=True)
        for _, row in grupo.iterrows():
            color = color_por_codigo(str(row['codigo']))
            cantidad = int(row['cantidad'])
            key_btn = f"{sector}_{row['codigo']}"
            if st.button(str(cantidad), key=key_btn):
                st.session_state.mostrar_modal = True
                st.session_state.codigo_modal = row['codigo']
                st.session_state.sector_modal = sector
            st.markdown(f'<style>button#{key_btn} {{ background-color: {color}; }}</style>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------- MODAL ----------
if st.session_state.mostrar_modal:
    sku = st.session_state.codigo_modal
    sector = st.session_state.sector_modal
    st.markdown('<div class="modal-overlay">', unsafe_allow_html=True)
    st.markdown('<div class="modal-content">', unsafe_allow_html=True)

    st.markdown(f"### 📦 Registros para SKU **{sku}** en sector **{sector}**")
    st.dataframe(df[(df["Sector"] == sector) & (df["codigo"] == sku)].reset_index(drop=True), use_container_width=True)

    if st.button("❌ Cerrar modal"):
        st.session_state.mostrar_modal = False

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
