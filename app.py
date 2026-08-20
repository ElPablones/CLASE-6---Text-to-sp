import streamlit as st
import os
import time
import glob
from gtts import gTTS
from PIL import Image
import base64
from deep_translator import GoogleTranslator

# Configuración de página e interfaz
st.set_page_config(
    page_title="VocalStudio | Traductor & TTS Multimodal",
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
        st.image(image, caption="Visualizador de Frecuencia", use_container_width=True)
    except Exception:
        try:
            image = Image.open('gato_raton.png')
            st.image(image, caption="Visualizador", use_container_width=True)
        except Exception:
            st.info("Coloca 'psicodelico.gif' en tu repo para ver el visualizador.")

    st.markdown("---")
    st.subheader("🌐 Configuración de Voz")
    
    option_lang = st.selectbox(
        "Idioma para la síntesis de voz",
        ("Español", "English")
    )
    lg = 'es' if option_lang == "Español" else 'en'
    
    velocidad = st.toggle("Modo Lectura Lenta", value=False)
    
    st.markdown("---")
    st.caption("🎧 *Laboratorio multimodal de traducción y síntesis sonora.*")

# ----------------- CUERPO PRINCIPAL -----------------
st.title("🌐 Estudio de Traducción y Síntesis Vocal")
st.markdown("> *Escribe tu texto, tradúcelo en tiempo real si lo deseas y genera la locución al instante.*")

# Inicializar variables de estado para el traductor
if "texto_origen" not in st.session_state:
    st.session_state["texto_origen"] = ""
if "texto_traducido" not in st.session_state:
    st.session_state["texto_traducido"] = ""

# ----------------- SECCIÓN DE TRADUCCIÓN -----------------
col_in, col_mid, col_out = st.columns([1.2, 0.4, 1.2])

with col_in:
    st.subheader("📝 Texto de Entrada")
    texto_input = st.text_area(
        "Ingresa el mensaje original:",
        value=st.session_state["texto_origen"],
        height=180,
        placeholder="Escribe lo que quieras traducir o narrar..."
    )
    # Actualizar estado
    st.session_state["texto_origen"] = texto_input

with col_mid:
    st.markdown("<br><br>", unsafe_allow_html=True)
    dir_traduccion = st.radio(
        "Dirección:",
        ("ES ➔ EN", "EN ➔ ES"),
        label_visibility="collapsed"
    )
    
    if st.button("🔄 Traducir", use_container_width=True, type="secondary"):
        if texto_input.strip():
            src_lang = 'es' if dir_traduccion == "ES ➔ EN" else 'en'
            target_lang = 'en' if dir_traduccion == "ES ➔ EN" else 'es'
            try:
                with st.spinner("Traduciendo..."):
                    traduccion = GoogleTranslator(source=src_lang, target=target_lang).translate(texto_input)
                    st.session_state["texto_traducido"] = traduccion
            except Exception as e:
                st.error("No se pudo completar la traducción. Verifica tu conexión.")
        else:
            st.warning("Escribe algo primero.")

with col_out:
    st.subheader("🌍 Texto Traducido")
    st.text_area(
        "Resultado de la traducción:",
        value=st.session_state["texto_traducido"],
        height=180,
        disabled=True
    )

# Selector de qué texto usar para sintetizar
st.markdown("---")
st.subheader("🎙️ Síntesis de Voz")

opcion_audio = st.radio(
    "¿Qué texto deseas convertir a voz?",
    ("Texto de Entrada", "Texto Traducido"),
    horizontal=True
)

texto_a_narrar = st.session_state["texto_origen"] if opcion_audio == "Texto de Entrada" else st.session_state["texto_traducido"]

# Métricas rápidas
c1, c2, c3 = st.columns(3)
c1.metric("Caracteres", len(texto_a_narrar))
c2.metric("Palabras", len(texto_a_narrar.split()))
c3.metric("Tiempo estimado", f"{round(len(texto_a_narrar.split()) / 2.5)} seg" if texto_a_narrar else "0 seg")

# ----------------- FUNCIÓN TTS ORIGINAL -----------------
def text_to_speech(text, tld, lg):
    tts = gTTS(text, lang=lg, slow=velocidad)
    try:
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

# ----------------- GENERACIÓN DE AUDIO -----------------
if st.button("🔊 Sintetizar Audio", type="primary"):
    if not texto_a_narrar.strip():
        st.warning("⚠️ No hay texto seleccionado para convertir a audio.")
    else:
        with st.spinner("🎧 Sintetizando voz y generando archivo sonoro..."):
            result, output_text = text_to_speech(texto_a_narrar, 'com', lg)
            file_path = f"temp/{result}.mp3"
            
            with open(file_path, "rb") as audio_file:
                audio_bytes = audio_file.read()

        st.success("✨ ¡Síntesis completada con éxito!")
        
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
