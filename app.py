import streamlit as st
import os
import time
import glob
from gtts import gTTS
from PIL import Image
import base64

# Configuración de página e interfaz
st.set_page_config(
    page_title="Voz & Relato | TTS Studio",
    page_icon="🎙️",
    layout="wide"
)

# Crear directorio temporal si no existe
os.makedirs("temp", exist_ok=True)

# ----------------- SIDEBAR CREATIVA -----------------
with st.sidebar:
    st.header("🎛️ Panel de Control")
    
    # Imagen / GIF psicodélico en el sidebar
    try:
        image = Image.open('psicodelico.gif')
        st.image(image, caption="Soundwave Visualizer", use_container_width=True)
    except Exception:
        try:
            image = Image.open('gato_raton.png')
            st.image(image, caption="Interfaces Multimodales", use_container_width=True)
        except Exception:
            st.info("Coloca 'psicodelico.gif' en tu repo para ver el visualizador.")

    st.markdown("---")
    st.subheader("🌐 Configuración de Voz")
    
    option_lang = st.selectbox(
        "Selecciona el idioma",
        ("Español", "English")
    )
    lg = 'es' if option_lang == "Español" else 'en'
    
    velocidad = st.toggle("Modo Lectura Lenta", value=False)
    
    st.markdown("---")
    st.caption("🎧 *Transforma cualquier narrativa en una experiencia sonora.*")

# ----------------- CUERPO PRINCIPAL -----------------
st.title("🎙️ Laboratorio de Síntesis Vocal Multimodal")
st.markdown("> *Explora cómo el texto cobra vida a través de la síntesis de voz en tiempo real.*")

# Fábula de Kafka predefinida
fabula_kafka = (
    "¡Ay! -dijo el ratón-. El mundo se hace cada día más pequeño. "
    "Al principio era tan grande que le tenía miedo. Corría y corría y por cierto "
    "que me alegraba ver esos muros, a diestra y siniestra, en la distancia. "
    "Pero esas paredes se estrechan tan rápido que me encuentro en el último cuarto "
    "y ahí en el rincón está la trampa sobre la cual debo pasar. "
    "Todo lo que debes hacer es cambiar de rumbo dijo el gato... y se lo comió.\n\n"
    "— Franz Kafka."
)

# Pestañas para organizar la experiencia
tab_fabula, tab_editor = st.tabs(["📖 Relato: Pequeña Fábula", "✍️ Estudio de Escritura"])

with tab_fabula:
    col_card, col_meta = st.columns([2.5, 1])
    
    with col_card:
        st.info(fabula_kafka, icon="🐭")
    
    with col_meta:
        st.metric(label="Autor", value="Franz Kafka")
        st.metric(label="Palabras", value=len(fabula_kafka.split()))
        cargar_fabula = st.button("📥 Cargar en el sintetizador", use_container_width=True)

with tab_editor:
    st.markdown("##### Escribe o personaliza el texto a narrar:")
    texto_inicial = fabula_kafka if cargar_fabula else ""
    text = st.text_area(
        "Caja de texto",
        value=texto_inicial,
        height=180,
        placeholder="Escribe o pega aquí la historia que deseas convertir a audio..."
    )
    
    # Métricas dinámicas en tiempo real
    c1, c2, c3 = st.columns(3)
    c1.metric("Caracteres", len(text))
    c2.metric("Palabras", len(text.split()))
    c3.metric("Tiempo estimado de lectura", f"{round(len(text.split()) / 2.5)} seg" if text else "0 seg")

# ----------------- FUNCIÓN TTS ORIGINAL -----------------
def text_to_speech(text, tld, lg):
    # Respeta la función base con soporte para velocidad
    tts = gTTS(text, lang=lg, slow=velocidad)
    try:
        # Sanitizar nombre para evitar fallos por caracteres especiales
        safe_name = "".join(c for c in text[0:15] if c.isalnum() or c in (' ', '_')).rstrip()
        my_file_name = safe_name if safe_name else "audio"
    except Exception:
        my_file_name = "audio"
        
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, text

def get_binary_file_downloader_html(bin_file, file_path, file_label='File'):
    with open(file_path, "rb") as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a style="text-decoration:none; padding:10px 20px; background-color:#FF4B4B; color:white; border-radius:8px; font-weight:bold;" href="data:application/octet-stream;base64,{bin_str}" download="{bin_file}">⬇️ Descargar {file_label}</a>'
    return href

st.markdown("---")

# ----------------- GENERACIÓN DE AUDIO -----------------
col_btn, col_space = st.columns([1, 2])
with col_btn:
    convertir = st.button("🔊 Convertir a Audio", use_container_width=True, type="primary")

if convertir:
    if not text.strip():
        st.warning("⚠️ Primero escribe o carga algún texto en la pestaña de edición.")
    else:
        with st.spinner("🎧 Sintetizando voz y modulando frecuencias..."):
            result, output_text = text_to_speech(text, 'com', lg)
            file_path = f"temp/{result}.mp3"
            
            with open(file_path, "rb") as audio_file:
                audio_bytes = audio_file.read()

        st.success("✨ ¡Síntesis completada con éxito!")
        
        # Reproductor y descarga estilizados
        st.subheader("🔊 Resultado Sonoro:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            get_binary_file_downloader_html(f"{result}.mp3", file_path, file_label="Archivo MP3"),
            unsafe_allow_html=True
        )

# ----------------- LIMPIEZA DE TEMPORALES -----------------
def remove_files(n):
    mp3_files = glob.glob("temp/*.mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                try:
                    os.remove(f)
                    print("Deleted ", f)
                except Exception:
                    pass

remove_files(7)
