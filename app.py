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
if not {'Sector', 'cantidad', 'codigo'}.issubset(df.columns):
    st.error("La tabla debe tener las columnas: Sector, cantidad, codigo")
    st.stop()

# Selección de sectores para demo
sectores = df['Sector'].dropna().unique()[:3]
df = df[df['Sector'].isin(sectores)]

# Agrupado
df_grouped = df.groupby(['Sector', 'codigo'], as_index=False)['cantidad'].sum()

# Color por SKU
def color_por_codigo(codigo):
    return "#" + hashlib.md5(codigo.encode()).hexdigest()[:6]

# Mostrar grilla
for sector in sectores:
    st.markdown(f"### Sector: {sector}")
    grupo = df_grouped[df_grouped['Sector'] == sector]
    cols = st.columns(len(grupo))
    for col, (_, row) in zip(cols, grupo.iterrows()):
        color = color_por_codigo(str(row['codigo']))
        cantidad = int(row['cantidad'])
        sku = row['codigo']
        if col.button(f"{cantidad}", key=f"{sector}-{sku}", help=f"{sku}"):
            st.session_state["sku"] = sku
            st.session_state["sector"] = sector

# Modal simple con botón de cierre
if "sku" in st.session_state and "sector" in st.session_state:
    sku_sel = st.session_state["sku"]
    sector_sel = st.session_state["sector"]
    detalle = df[(df["Sector"] == sector_sel) & (df["codigo"] == sku_sel)]
    
    with st.expander(f"📦 Detalle de SKU '{sku_sel}' en sector '{sector_sel}'", expanded=True):
        st.dataframe(detalle.reset_index(drop=True), use_container_width=True)
        if st.button("❌ Cerrar modal"):
            del st.session_state["sku"]
            del st.session_state["sector"]
