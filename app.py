import time
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="Simulador de Tiro Parabólico", layout="centered"
)
st.title("Simulador de Tiro Parabólico con Cañón")
st.write(
    "Ajusta los parámetros con los controles de la izquierda y haz clic en"
    " **Disparar**."
)

st.sidebar.header("Parámetros del Cañón")
v_0 = st.sidebar.slider("Velocidad (m/s)", 10, 60, 60, 1)
theta = st.sidebar.slider("Ángulo (°)", -90, 90, 45, 1)
x_0 = st.sidebar.slider("Posición X", 14, 50, 50, 1)
y_0 = st.sidebar.slider("Altura Y", 14, 80, 80, 1)
g = 9.8


@st.cache_data
def cargar_imagenes():
    try:
        canon = Image.open("cañon.png")
        fondo = Image.open("fondo.jpg")
        bola = Image.open("bola.png")
        soporte = Image.open("soporte.png")
        return canon, fondo, bola, soporte
    except FileNotFoundError as e:
        return None, None, None, None

canon, fondo, bola, soporte = cargar_imagenes()
if canon is None:
    st.error("Falta una imagen en la carpeta (cañon.png, fondo.jpg, bola.png o soporte.png).")
    st.stop()

col1, col2 = st.sidebar.columns(2)
disparar = col1.button("Disparar")
reiniciar = col2.button("Reiniciar")

if "animando" not in st.session_state:
    st.session_state.animando = False

if reiniciar:
    st.session_state.animando = False
    st.rerun()

if disparar:
    st.session_state.animando = True

contenedor_grafico = st.empty()

@st.cache_resource
def crear_figura_base(x_0, y_0, theta):
    fig, axis = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_facecolor("#1e1e1e")
    axis.set_facecolor("#1e1e1e")
    axis.tick_params(colors="white", which="both")
    for spine in axis.spines.values():
        spine.set_edgecolor("white")
    
    axis.set_xlim([0, 500])
    axis.set_ylim([0, 280])
    

    axis.imshow(fondo, extent=[0, 500, 0, 280], zorder=0)
    

    x_suelo = np.linspace(0, 500, 500)
    canon_size = 500 * 0.08
    altura_colina = y_0 - canon_size / 3
    ancho_meseta = 500 * 0.08
    suavidad = 500 * 0.015
    y_suelo = (altura_colina / 2) * (
        np.tanh((x_suelo - (x_0 - ancho_meseta / 2)) / suavidad)
        - np.tanh((x_suelo - (x_0 + ancho_meseta / 2)) / suavidad)
    )
    axis.fill_between(x_suelo, 0, y_suelo, zorder=2, color="olivedrab")
    

    canon_rotado = canon.rotate(theta, expand=True)
    canon_largo = 30
    ancho_original, alto_original = canon.size
    escala = ancho_original / canon_largo
    ancho = canon_rotado.size[0] / escala
    alto = canon_rotado.size[1] / escala
    
    axis.imshow(
        canon_rotado,
        extent=[x_0 - ancho / 2, x_0 + ancho / 2, y_0 - alto / 2, y_0 + alto / 2],
        zorder=10,
    )
    axis.imshow(
        soporte, extent=[x_0 - 8, x_0 + 8, y_0 - 22, y_0 + 2], zorder=11
    )
    

    (linea_trayectoria,) = axis.imshow(np.zeros((10, 10, 4)), extent=[0,0,0,0], zorder=4) # placeholder o usar plot
    # Mejor usar plot para la línea y imshow para la bola:
    (linea_traj,) = axis.plot([], [], color="blue", linewidth=3, linestyle="--", zorder=4)

    bola_im = axis.imshow(bola, extent=[-20, -10, -20, -10], zorder=9)
    
    return fig, axis, linea_traj, bola_im


fig, axis, linea_traj, bola_im = crear_figura_base(x_0, y_0, theta)

if st.session_state.animando:
    rad = np.pi / 180 * theta
    v_x = v_0 * np.cos(rad)
    v_y = v_0 * np.sin(rad)
    t_max = (v_y + np.sqrt(v_y ** 2 + 2 * g * y_0)) / g
    t = np.linspace(0, t_max, 35) # Un poco más fluido
    x_trayectoria = x_0 + v_x * t
    y_trayectoria = y_0 + v_y * t - 0.5 * g * t ** 2
    

    contenedor_grafico.pyplot(fig)
    
    for i in range(1, len(x_trayectoria)):
        # Actualizamos únicamente los datos de la línea y la posición de la bola
        linea_traj.set_data(x_trayectoria[:i], y_trayectoria[:i])
        
        bx = x_trayectoria[i]
        by = y_trayectoria[i]
        bola_im.set_extent([bx - 6, bx + 6, by - 6, by + 6])
        
        contenedor_grafico.pyplot(fig)
        time.sleep(0.02)
else:

    linea_traj.set_data([], [])
    bola_im.set_extent([-20, -10, -20, -10])
    contenedor_grafico.pyplot(fig)
