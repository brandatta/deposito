import streamlit as st
import pandas as pd
import mysql.connector

# Configuración general
st.set_page_config(page_title="Mapa del Depósito", layout="wide")
st.title("📦 Plano del Depósito - 1 Fila x 3 Columnas")

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

# Agrupar y preparar resumen por sector
df_summary = df.groupby('Sector').agg({
    'cantidad': 'sum',
    'codigo': lambda x: ', '.join(sorted(set(map(str, x))))
}).reset_index()

# Definir los sectores para la grilla (orden fijo)
sectores_en_grilla = ["ZONA 1", "ZONA 2", "FALLADO MUNRO"]
df_grilla = df_summary[df_summary['Sector'].isin(sectores_en_grilla)]
df_grilla = df_grilla.set_index('Sector').reindex(sectores_en_grilla).reset_index()

# Mostrar como tabla estilizada (sin colores de fondo llamativos)
st.markdown("""
<style>
    .grilla {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0;
        border: 2px solid black;
        margin-top: 20px;
    }
    .celda {
        border: 1px solid black;
        padding: 15px;
        text-align: center;
        font-family: sans-serif;
    }
    .titulo {
        font-weight: bold;
        font-size: 16px;
    }
    .cantidad {
        margin-top: 5px;
        font-size: 14px;
    }
    .codigo {
        margin-top: 5px;
        font-size: 12px;
    }
</style>
<div class="grilla">
""", unsafe_allow_html=True)

# Renderizar cada celda
for _, row in df_grilla.iterrows():
    st.markdown(f"""
    <div class="celda">
        <div class="titulo">{row['Sector']}</div>
        <div class="cantidad">Cantidad: {int(row['cantidad'])}</div>
        <div class="codigo">Códigos:<br>{row['codigo']}</div>
    </div>
    """, unsafe_allow_html=True)

# Cerrar contenedor
st.markdown("</div>", unsafe_allow_html=True)
