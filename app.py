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

# Validación de columnas
if not {'Sector', 'cantidad', 'codigo', 'descripcion'}.issubset(df.columns):
    st.error("La tabla debe tener las columnas: Sector, cantidad, codigo, descripcion")
    st.stop()

# Filtrar primeros 3 sectores únicos
sectores = df['Sector'].dropna().unique()[:3]
df = df[df['Sector'].isin(sectores)]

# Agrupar por sector y sku, sumando cantidades
df_grouped = df.groupby(['Sector', 'codigo'], as_index=False)['cantidad'].sum()

# Función para color único por SKU
def color_por_codigo(codigo):
    return '#' + hashlib.md5(codigo.encode()).hexdigest()[:6]

# Estado para modal
if "show_modal" not in st.session_state:
    st.session_state.show_modal = False
if "selected_sku" not in st.session_state:
    st.session_state.selected_sku = None
if "selected_sector" not in st.session_state:
    st.session_state.selected_sector = None

# Callback al hacer clic
def mostrar_modal(sku, sector):
    st.session_state.selected_sku = sku
    st.session_state.selected_sector = sector
    st.session_state.show_modal = True

# CSS para estilo
st.markdown("""
<style>
.grilla {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-top: 20px;
}
.sector {
    width: 120px;
    height: 120px;
    border: 2px solid black;
    border-radius: 6px;
    background-color: white;
    padding: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
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
.sku-button {
    width: 38px;
    height: 38px;
    border-radius: 4px;
    border: none;
    font-weight: bold;
    font-size: 13px;
    color: white;
    cursor: pointer;
}
.modal-overlay {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background-color: rgba(0, 0, 0, 0.75);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}
.modal {
    background-color: white;
    padding: 20px;
    width: 80%;
    max-height: 80%;
    overflow-y: auto;
    border-radius: 10px;
    position: relative;
}
.close-button {
    position: absolute;
    top: 8px;
    right: 12px;
    font-size: 20px;
    color: black;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# Dibujar grilla
st.markdown('<div class="grilla">', unsafe_allow_html=True)
for sector in sectores:
    grupo = df_grouped[df_grouped['Sector'] == sector]
    with st.container():
        st.markdown(f'<div class="sector"><div class="sector-label">{sector}</div><div class="sku-container">', unsafe_allow_html=True)
        for _, row in grupo.iterrows():
            color = color_por_codigo(str(row['codigo']))
            cantidad = int(row['cantidad'])
            sku_key = f"sku_{sector}_{row['codigo']}"
            if st.button(f"{cantidad}", key=sku_key):
                mostrar_modal(row['codigo'], sector)
            st.markdown(
                f'<style>#{sku_key}{{background-color:{color} !important;}}</style>',
                unsafe_allow_html=True,
            )
        st.markdown('</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Mostrar modal si corresponde
if st.session_state.show_modal:
    sku = st.session_state.selected_sku
    sector = st.session_state.selected_sector
    detalle = df[(df["Sector"] == sector) & (df["codigo"] == sku)]

    # Mostrar modal
    st.markdown("""
    <div class="modal-overlay">
        <div class="modal">
            <div class="close-button" onclick="window.location.href=window.location.href">×</div>
            <h4>📦 Registros para SKU <b>%s</b> en sector <b>%s</b></h4>
    """ % (sku, sector), unsafe_allow_html=True)

    st.dataframe(detalle[['descripcion']].reset_index(drop=True), use_container_width=True)

    st.markdown("</div></div>", unsafe_allow_html=True)
