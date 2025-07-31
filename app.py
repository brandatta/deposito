import streamlit as st
import pandas as pd
import mysql.connector
import hashlib

# Configuración general
st.set_page_config(page_title="Mapa del Depósito Visual", layout="wide")
st.title("📦 Plano del Depósito (por SKU)")

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
if not {'Sector', 'cantidad', 'codigo'}.issubset(df.columns):
    st.error("La tabla debe tener las columnas: Sector, cantidad, codigo")
    st.stop()

# Dropdown para seleccionar SKU
codigos_disponibles = df['codigo'].dropna().unique()
codigo_seleccionado = st.selectbox("Seleccioná un código:", codigos_disponibles)

# Agrupar cantidad por sector
df_filtrado = df[df['codigo'] == codigo_seleccionado]
df_sector = df_filtrado.groupby('Sector', as_index=False)['cantidad'].sum()

# Lista de sectores
sectores_grilla = df['Sector'].dropna().unique()[:3]
cantidades_por_sector = {row['Sector']: int(row['cantidad']) for _, row in df_sector.iterrows()}

# Color por código
def color_por_codigo(codigo):
    return '#' + hashlib.md5(codigo.encode()).hexdigest()[:6]

# Inicializar estado de sector seleccionado
if "sector_activo" not in st.session_state:
    st.session_state.sector_activo = None

# CSS personalizado
st.markdown(f"""
<style>
.contenedor-flex {{
    display: flex;
    flex-direction: row;
    gap: 15px;
    align-items: flex-start;
    margin-top: 20px;
}}

.columna-vertical {{
    display: flex;
    flex-direction: column;
    gap: 18px;
}}

.sector {{
    width: 120px;
    aspect-ratio: 1 / 1;
    border: 2px solid black;
    border-radius: 8px;
    background-color: #ffffff;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    box-sizing: border-box;
}}

.sector-label {{
    position: absolute;
    top: 6px;
    font-size: 13px;
    font-weight: bold;
    background-color: white;
    padding: 0 4px;
}}

.cantidad-box {{
    width: 40px;
    height: 40px;
    border-radius: 6px;
    background-color: {color_por_codigo(codigo_seleccionado)};
    color: white;
    font-weight: bold;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 12px;
}}
</style>
""", unsafe_allow_html=True)

# Layout visual con flexbox
st.markdown('<div class="contenedor-flex">', unsafe_allow_html=True)

# Grilla vertical con botones
with st.container():
    st.markdown('<div class="columna-vertical">', unsafe_allow_html=True)
    for sector in sectores_grilla:
        cantidad = cantidades_por_sector.get(sector, 0)

        # Mostrar caja de sector
        html = f'<div class="sector"><div class="sector-label">{sector}</div>'
        if cantidad > 0:
            html += f'<div class="cantidad-box">{cantidad}</div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

        # Botón "Ver"
        if st.button(f"Ver {sector}", key=f"btn_{sector}"):
            st.session_state.sector_activo = sector
    st.markdown('</div>', unsafe_allow_html=True)

# Detalle del sector a la derecha
with st.container():
    if st.session_state.sector_activo:
        st.markdown(f"<div style='min-width:300px; max-width: 400px;'><h4>📍 Sector: {st.session_state.sector_activo}</h4>", unsafe_allow_html=True)
        if st.button("❌ Cerrar detalle"):
            st.session_state.sector_activo = None
        else:
            detalle_sector = df[df['Sector'] == st.session_state.sector_activo]
            resumen = detalle_sector.groupby("codigo", as_index=False)["cantidad"].sum()
            st.dataframe(resumen, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
