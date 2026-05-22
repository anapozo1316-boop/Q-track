import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(
    page_title="Q-Track",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}

h1 {
    color: #0b5394;
}

.stButton>button {
    background-color: #0b5394;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

ARCHIVO = "instrumentos.csv"

if not os.path.exists(ARCHIVO):

    columnas = [
        "ID",
        "Fecha",
        "Instrumento",
        "Tiempo de uso",
        "Cantidad de usos",
        "Desgaste",
        "Fallas",
        "Puntaje",
        "Estado"
    ]

    pd.DataFrame(columns=columnas).to_csv(
        ARCHIVO,
        index=False
    )

df = pd.read_csv(ARCHIVO)

st.sidebar.title("🏥 Q-Track")
st.sidebar.info(
    "Sistema inteligente para evaluación de instrumental quirúrgico."
)

st.title("🏥 Q-Track")
st.subheader("Gestión y análisis de instrumentos quirúrgicos")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Instrumentos registrados",
    len(df)
)

col2.metric(
    "Requieren mantenimiento",
    len(df[df["Estado"] == "Requiere mantenimiento"])
)

col3.metric(
    "Retirados",
    len(df[df["Estado"] == "Retirar del servicio"])
)

st.subheader("➕ Registrar instrumento")

with st.form("formulario"):

    nombre = st.text_input(
        "Nombre del instrumento"
    )

    tiempo = st.number_input(
        "Tiempo de uso (años)",
        min_value=0,
        max_value=50
    )

    usos = st.number_input(
        "Cantidad de usos",
        min_value=0,
        max_value=10000
    )

    desgaste = st.selectbox(
        "Nivel de desgaste",
        ["Bajo", "Moderado", "Alto"]
    )

    fallas = st.text_area(
        "Fallas detectadas"
    )

    enviar = st.form_submit_button(
        "Analizar instrumento"
    )

def analizar(tiempo, usos, desgaste, fallas):

    puntaje = 0

    if tiempo >= 5:
        puntaje += 3
    elif tiempo >= 3:
        puntaje += 2

    if usos >= 800:
        puntaje += 3
    elif usos >= 400:
        puntaje += 2

    if desgaste == "Alto":
        puntaje += 3
    elif desgaste == "Moderado":
        puntaje += 2

    texto = fallas.lower()

    fallas_criticas = [
        "fractura",
        "oxidación",
        "deformación",
        "rotura"
    ]

    for falla in fallas_criticas:
        if falla in texto:
            puntaje += 4

    if puntaje >= 10:
        estado = "Retirar del servicio"

    elif puntaje >= 7:
        estado = "Necesita reparación"

    elif puntaje >= 4:
        estado = "Requiere mantenimiento"

    else:
        estado = "Apto para uso"

    return puntaje, estado

if enviar:

    if nombre.strip() == "":
        st.error("Debe ingresar el nombre del instrumento.")

    else:

        puntaje, estado = analizar(
            tiempo,
            usos,
            desgaste,
            fallas
        )

        nuevo = {
            "ID": len(df) + 1,
            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Instrumento": nombre,
            "Tiempo de uso": tiempo,
            "Cantidad de usos": usos,
            "Desgaste": desgaste,
            "Fallas": fallas,
            "Puntaje": puntaje,
            "Estado": estado
        }

        df = pd.concat(
            [df, pd.DataFrame([nuevo])],
            ignore_index=True
        )

        df.to_csv(
            ARCHIVO,
            index=False
        )

        if estado == "Apto para uso":
            st.success("✅ Instrumento apto para uso.")

        elif estado == "Requiere mantenimiento":
            st.warning("⚠️ Requiere mantenimiento.")

        elif estado == "Necesita reparación":
            st.error("🔧 Necesita reparación.")

        elif estado == "Retirar del servicio":
            st.error("🚫 Debe retirarse del servicio.")

st.subheader("📋 Historial")

filtro = st.selectbox(
    "Filtrar por estado",
    [
        "Todos",
        "Apto para uso",
        "Requiere mantenimiento",
        "Necesita reparación",
        "Retirar del servicio"
    ]
)

if filtro != "Todos":
    tabla = df[df["Estado"] == filtro]
else:
    tabla = df

st.dataframe(
    tabla,
    use_container_width=True
)

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Descargar reporte CSV",
    csv,
    "reporte_qtrack.csv",
    "text/csv"
)
