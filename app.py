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
st.sidebar.header("🎛Parámetros del Cañón")
v_0 = st.sidebar.slider("Velocidad (m/s)", 10, 60, 60, 1)
theta = st.sidebar.slider("Ángulo (°)", -90, 90, 45, 1)
x_0 = st.sidebar.slider("Posición X", 14, 50, 50, 1)
y_0 = st.sidebar.slider("Altura Y", 14, 80, 80, 1)
g = 9.8
try:
  canon = Image.open("cañon.png")
  fondo = Image.open("fondo.jpg")
  bola = Image.open("bola.png")
  soporte = Image.open("soporte.png")
except FileNotFoundError as e:
  st.error(f"Falta una imagen en la carpeta: {e}")
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
def generar_escenario(
    x_anim=None, y_anim=None, mostrar_bola_en_vuelo=False, frame_actual=0
):
  fig, axis = plt.subplots(figsize=(8, 4.5))
  fig.patch.set_facecolor("#1e1e1e")
  axis.set_facecolor("#1e1e1e")
  axis.tick_params(colors="white", which="both")
  for spine in axis.spines.values():
    spine.set_edgecolor("white")
  axis.set_xlim([0, 500])
  axis.set_ylim([0, 280])
  axis.imshow(fondo, extent=[0, 500, 0, 280], zorder=0)
  canon_size = 500 * 0.08
  x_suelo = np.linspace(0, 500, 500)
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
  if mostrar_bola_en_vuelo and x_anim is not None:
    axis.plot(
        x_anim[:frame_actual],
        y_anim[:frame_actual],
        color="blue",
        linewidth=3,
        linestyle="--",
        zorder=4,
    )
    axis.imshow(
        bola,
        extent=[
            x_anim[frame_actual] - 6,
            x_anim[frame_actual] + 6,
            y_anim[frame_actual] - 6,
            y_anim[frame_actual] + 6,
        ],
        zorder=9,
    )
  return fig
if st.session_state.animando:
  rad = np.pi / 180 * theta
  v_x = v_0 * np.cos(rad)
  v_y = v_0 * np.sin(rad)
  t_max = (v_y + np.sqrt(v_y ** 2 + 2 * g * y_0)) / g
  t = np.linspace(0, t_max, 60)
  x_trayectoria = x_0 + v_x * t
  y_trayectoria = y_0 + v_y * t - 0.5 * g * t ** 2
  for i in range(1, len(x_trayectoria)):
    fig = generar_escenario(
        x_trayectoria, y_trayectoria, mostrar_bola_en_vuelo=True, frame_actual=i
    )
    contenedor_grafico.pyplot(fig)
    plt.close(fig)
    time.sleep(0.03)
else:
  fig = generar_escenario()
  contenedor_grafico.pyplot(fig)
  plt.close(fig)
