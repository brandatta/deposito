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

# Validación de columnas
if not {'Sector', 'cantidad', 'codigo'}.issubset(df.columns):
    st.error("La tabla debe tener las columnas: Sector, cantidad, codigo")
    st.stop()

# Estado del sector seleccionado
if 'sector_seleccionado' not in st.session_state:
    st.session_state['sector_seleccionado'] = None

# Dropdown para seleccionar SKU
codigos_disponibles = df['codigo'].dropna().unique()
codigo_seleccionado = st.selectbox("Seleccioná un código:", codigos_disponibles)

# Agrupar cantidad por sector
df_filtrado = df[df['codigo'] == codigo_seleccionado]
df_sector = df_filtrado.groupby('Sector', as_index=False)['cantidad'].sum()

# Tomar los primeros 3 sectores para la grilla
sectores_grilla = df['Sector'].dropna().unique()[:3]
cantidades_por_sector = {row['Sector']: int(row['cantidad']) for _, row in df_sector.iterrows()}

# Función para color único por código
def color_por_codigo(codigo):
    return '#' + hashlib.md5(codigo.encode()).hexdigest()[:6]

# Grilla con detalle al lado
cols = st.columns([1, 1])  # [Grilla, Detalle]

with cols[0]:  # Grilla a la izquierda
    st.markdown("### 🗂️ Sectores")
    grilla_cols = st.columns(3)
    for i, sector in enumerate(sectores_grilla):
        cantidad = cantidades_por_sector.get(sector, 0)
        with grilla_cols[i]:
            if st.button(f"{sector}\n({cantidad})", key=f"btn_{sector}"):
                st.session_state['sector_seleccionado'] = sector

with cols[1]:  # Detalle a la derecha
    sector = st.session_state['sector_seleccionado']
    if sector:
        st.markdown(f"### 📄 Detalle del sector **{sector}**")
        detalle = df[(df['Sector'] == sector) & (df['codigo'] == codigo_seleccionado)]
        if not detalle.empty:
            st.dataframe(detalle, use_container_width=True)
        else:
            st.info("No hay registros para este código en el sector seleccionado.")

