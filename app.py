# ... tu código Python hasta CSS igual ...

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
.sku {
    width: 40px;
    height: 40px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 13px;
    color: white;
}
</style>
<div class="grilla">
""", unsafe_allow_html=True)

# Renderizado igual, pero sector-label ya se ve bien
for sector in sectores:
    grupo = df_grouped[df_grouped['Sector'] == sector]
    html = f'<div class="sector"><div class="sector-label">{sector}</div><div class="sku-container">'
    for _, row in grupo.iterrows():
        color = color_por_codigo(str(row['codigo']))
        cantidad = int(row['cantidad'])
        html += f'<div class="sku" style="background-color:{color};" title="{row["codigo"]}">{cantidad}</div>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
