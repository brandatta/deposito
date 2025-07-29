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

# Validar columnas
if not {'Sector', 'cantidad', 'codigo'}.issubset(df.columns):
    st.error("La tabla debe tener las columnas: Sector, cantidad, codigo")
    st.stop()

# Filtrar primeros 3 sectores únicos
sectores = df['Sector'].dropna().unique()[:3]
df = df[df['Sector'].isin(sectores)]

# Agrupar por sector y SKU
df_grouped = df.groupby(['Sector', 'codigo'], as_index=False)['cantidad'].sum()

# Colores únicos por SKU
def color_por_codigo(codigo):
    return "#" + hashlib.md5(codigo.encode()).hexdigest()[:6]

# Inicializar estado
if 'sku_seleccionado' not in st.session_state:
    st.session_state['sku_seleccionado'] = None
    st.session_state['sector_seleccionado'] = None

# CSS básico
st.markdown("""
    <style>
    .sector-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        border: 2px solid black;
        border-radius: 8px;
        padding: 10px;
        width: 140px;
        height: 140px;
        margin: 10px;
        background-color: white;
    }
    .sector-title {
        font-weight: bold;
        margin-bottom: 5px;
    }
    .sku-button {
        width: 36px;
        height: 36px;
        border-radius: 4px;
        border: none;
        font-weight: bold;
        font-size: 13px;
        margin: 2px;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Mostrar sectores en una grilla
cols = st.columns(len(sectores))

for idx, sector in enumerate(sectores):
    with cols[idx]:
        st.markdown('<div class="sector-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="sector-title">{sector}</div>', unsafe_allow_html=True)

        grupo = df_grouped[df_grouped['Sector'] == sector]
        # Mostrar botones para cada SKU
        for _, row in grupo.iterrows():
            color = color_por_codigo(row['codigo'])
            cantidad = int(row['cantidad'])
            btn_key = f"{sector}_{row['codigo']}"

            # Usar botones reales de Streamlit
            if st.button(str(cantidad), key=btn_key):
                st.session_state['sku_seleccionado'] = row['codigo']
                st.session_state['sector_seleccionado'] = sector

            # Aplicar color al último botón creado (sí, con CSS scoped)
            st.markdown(f"""
                <style>
                button[data-testid="baseButton-secondary"]#{btn_key} {{
                    background-color: {color} !important;
                    color: white !important;
                }}
                </style>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# Mostrar detalle si hay selección
sku = st.session_state['sku_seleccionado']
sector = st.session_state['sector_seleccionado']

if sku and sector:
    st.markdown(f"### 🔍 Registros para SKU **{sku}** en sector **{sector}**")
    registros = df[(df['Sector'] == sector) & (df['codigo'] == sku)]
    st.dataframe(registros.reset_index(drop=True), use_container_width=True)
