import streamlit as st
import pandas as pd
import mysql.connector

# Configuración
st.set_page_config(page_title="Mapa del Depósito", layout="wide")
st.title("📦 Mapa visual del Depósito")

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
    'codigo': lambda x: ', '.join(sorted(set(map(str, x))))
}).reset_index()

# Seleccionar los sectores que van en la grilla fija (1 fila x 3 columnas)
# Podés reemplazar estos valores por los nombres reales que quieras mostrar
sectores_en_grilla = ["ZONA 1", "ZONA 2", "FALLADO MUNRO"]

# Filtrar solo esos sectores
df_grilla = df_summary[df_summary['Sector'].isin(sectores_en_grilla)]

# Asegurarse de mantener el orden deseado
df_grilla = df_grilla.set_index('Sector').reindex(sectores_en_grilla).reset_index()

# Crear la grilla de 1 fila y 3 columnas
cols = st.columns(3)

for i, row in enumerate(df_grilla.itertuples()):
    with cols[i]:
        st.markdown(f"""
            <div style="
                border: 2px solid #ccc;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                background-color: #f0f8ff;
                text-align: center;
                min-height: 120px;
            ">
                <h5 style="margin-bottom: 5px;">📍 {row.Sector}</h5>
                <p style="margin: 5px 0;"><strong>Cantidad total:</strong> {row.cantidad}</p>
                <p style="margin: 5px 0; font-size: 12px;"><strong>Productos:</strong><br>{row.codigo}</p>
            </div>
        """, unsafe_allow_html=True)
