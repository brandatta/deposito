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

# Cargar datos
@st.cache_data
def load_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM mapa_deposito", conn)
    conn.close()
    return df

df = load_data()

# Validación
if not {'Sector', 'cantidad', 'codigo', 'descripcion'}.issubset(df.columns):
    st.error("La tabla debe tener las columnas: Sector, cantidad, codigo, descripcion")
    st.stop()

# Estado del modal
if "modal_sku" not in st.session_state:
    st.session_state.modal_sku = None
    st.session_state.modal_sector = None
    st.session_state.modal_open = False

# Filtrar primeros 3 sectores únicos
sectores = df['Sector'].dropna().unique()[:3]
df = df[df['Sector'].isin(sectores)]

# Agrupar por sector y sku
df_grouped = df.groupby(['Sector', 'codigo'], as_index=False)['cantidad'].sum()

# Función de color por código
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
    padding: 8px 5px 5px 5px;
    background-color: white;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
}
.sector-label {
    font-weight: bold;
    font-size: 13px;
    margin-bottom: 6px;
    text-align: center;
    width: 100%;
}
.sku-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    overflow-y: auto;
    justify-content: center;
}
button.sku {
    width: 40px;
    height: 40px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 13px;
    color: white;
    border: none;
    cursor: pointer;
}
.modal-overlay {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background-color: rgba(0, 0, 0, 0.7);
    z-index: 1000;
    display: flex;
    justify-content: center;
    align-items: center;
}
.modal-content {
    background-color: white;
    padding: 25px;
    border-radius: 8px;
    max-width: 600px;
    max-height: 80vh;
    overflow-y: auto;
    text-align: left;
}
</style>
<div class="grilla">
""", unsafe_allow_html=True)

# ---------- Render de la grilla ----------
for sector in sectores:
    grupo = df_grouped[df_grouped['Sector'] == sector]
    st.markdown(f'<div class="sector"><div class="sector-label">{sector}</div><div class="sku-container">', unsafe_allow_html=True)
    for _, row in grupo.iterrows():
        color = color_por_codigo(str(row['codigo']))
        cantidad = int(row['cantidad'])
        key = f"sku_{sector}_{row['codigo']}"
        if st.button(str(cantidad), key=key):
            st.session_state.modal_sector = sector
            st.session_state.modal_sku = row['codigo']
            st.session_state.modal_open = True
        # Aplicar color dinámico al botón
        st.markdown(f"<style>button#{key}{{background-color: {color};}}</style>", unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------- Modal si está activo ----------
if st.session_state.modal_open:
    sku = st.session_state.modal_sku
    sector = st.session_state.modal_sector
    registros = df[(df['Sector'] == sector) & (df['codigo'] == sku)]

    st.markdown('<div class="modal-overlay">', unsafe_allow_html=True)
    st.markdown('<div class="modal-content">', unsafe_allow_html=True)
    st.markdown(f"### 📦 Registros de SKU **{sku}** en sector **{sector}**")

    for i, row in registros.iterrows():
        st.markdown(f"- {row['descripcion']}")

    if st.button("❌ Cerrar"):
        st.session_state.modal_open = False

    st.markdown('</div></div>', unsafe_allow_html=True)
