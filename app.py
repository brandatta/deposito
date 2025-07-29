import streamlit as st
import pandas as pd
import mysql.connector

# Configuración de la app
st.set_page_config(page_title="Mapa del Depósito", layout="wide")
st.title("📦 Mapa del Depósito")

# Conexión a MySQL
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
    query = "SELECT * FROM mapa_deposito"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

df = load_data()

# Verificar columnas necesarias
if not {'Sector', 'cantidad', 'codigo'}.issubset(df.columns):
    st.error("La tabla debe tener las columnas: Sector, cantidad, codigo")
    st.stop()

# Agrupar por sector
df_summary = df.groupby('Sector').agg({
    'cantidad': 'sum',
    'codigo': lambda x: ', '.join(sorted(set(x)))
}).reset_index()

# Mostrar en tarjetas o grilla adaptable
st.subheader("📦 Distribución por sector")

cols = st.columns(3)  # 3 columnas por fila
for idx, row in df_summary.iterrows():
    with cols[idx % 3]:
        st.markdown(f"""
            <div style="border:1px solid #ccc; border-radius:10px; padding:12px; margin-bottom:10px; background-color:#f7f7f7;">
                <h5 style="margin:0 0 5px;">📍 {row['Sector']}</h5>
                <strong>Cantidad total:</strong> {row['cantidad']}<br>
                <strong>Códigos:</strong> {row['codigo']}
            </div>
        """, unsafe_allow_html=True)
