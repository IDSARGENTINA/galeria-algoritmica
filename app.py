import streamlit as st
import requests
import time
import json
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import numpy as np

# ============================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Galería Algorítmica | IDSA",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. ESTILOS CSS
# ============================================================
st.markdown("""
    <style>
    .main-header { text-align: center; font-family: 'Georgia', serif; color: #2c3e50; margin-bottom: 0.5rem; }
    .sub-header { text-align: center; color: #7f8c8d; font-style: italic; margin-bottom: 2rem; }
    .tech-box { background-color: #f8f9fa; border-left: 4px solid #667eea; padding: 1rem; border-radius: 8px; margin: 1.5rem 0; }
    .tech-title { color: #2c3e50; font-weight: bold; font-size: 1.1rem; margin-bottom: 0.5rem; }
    .tech-item { color: #34495e; margin: 0.3rem 0; font-size: 0.95rem; }
    .footer { text-align: center; color: #95a5a6; font-size: 0.85rem; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #ecf0f1; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# 3. GESTIÓN DE TOKEN Y NAVEGACIÓN ROBUSTA
# ============================================================
hf_token = st.secrets.get("HF_TOKEN", "")

st.sidebar.title("️ Galería Algorítmica")
st.sidebar.markdown("**Instituto Data Science Argentina**")
st.sidebar.markdown("---")

# Claves lógicas limpias (sin emojis) para evitar bugs de encoding
menu_keys = [
    "Inicio", "Retrato", "Poema", "Memes", "Emociones", "Historias", "DataArt"
]

# Mapeo de claves lógicas a etiquetas visuales
menu_labels = {
    "Inicio": "🏠 Inicio",
    "Retrato": "📸 Opción A: Retrato Algorítmico",
    "Poema": " Opción C: Poema Visual",
    "Memes": "😂 Opción D: Generador de Memes",
    "Emociones": "💝 Opción E: Visualizador de Emociones",
    "Historias": "📖 Opción F: Historias Interactivas",
    "DataArt": "📊 Opción G: Data Art Generator"
}

# format_func es la forma MÁS ESTABLE de manejar emojis en menús de Streamlit
opcion = st.sidebar.radio(
    "Elige una experiencia:",
    menu_keys,
    format_func=lambda x: menu_labels[x]
)

st.sidebar.markdown("---")
if not hf_token:
    with st.sidebar.expander("⚙️ Configurar Token"):
        hf_token = st.text_input("Hugging Face Token", type="password")
        st.info(" Guárdalo en Secrets para producción.")
else:
    st.sidebar.success("✅ Token configurado")

st.sidebar.caption("Arte con IA · 100% Gratuito")

# ============================================================
# 4. FUNCIONES AUXILIARES (BLINDADAS)
# ============================================================
def query_huggingface(api_url, payload, token, retries=3):
    """Consulta la API con reintentos, timeouts y manejo de errores robusto."""
    headers = {"Authorization": f"Bearer {token}"}
    for attempt in range(retries):
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 503:
                wait_time = response.json().get("estimated_time", 20)
                st.warning(f"⏳ Modelo cargando... esperando {wait_time:.0f}s (Intento {attempt+1}/{retries})")
                time.sleep(wait_time)
            elif response.status_code == 200:
                return response.content
            else:
                st.error(f"❌ Error API {response.status_code}: {response.text[:100]}")
                return None
        except requests.exceptions.RequestException as e:
            st.warning(f" Error de red: {str(e)[:50]}. Reintentando...")
            time.sleep(5)
    return None

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def draw_meme_text(img, top_text, bottom_text):
    """Dibuja texto en la imagen con fallback de fuente seguro."""
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except OSError:
        font = ImageFont.load_default()
    
    w, h = img.size
    if top_text:
        draw.text((w/2, 30), top_text, fill="white", font=font, anchor="mm", stroke_width=2, stroke_fill="black")
    if bottom_text:
        draw.text((w/2, h - 30), bottom_text, fill="white", font=font, anchor="mm", stroke_width=2, stroke_fill="black")
    return img

# ============================================================
# 5. RUTAS DE LA APLICACIÓN
# ============================================================

# --- INICIO ---
if opcion == "Inicio":
    st.markdown("<h1 class='main-header'>🎨 Galería Algorítmica</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Donde el arte se encuentra con los datos</p>", unsafe_allow_html=True)
    st.info("Selecciona una experiencia en el menú lateral para comenzar.")

# --- OPCIÓN A: RETRATO ---
elif opcion == "Retrato":
    st.markdown("<h1 class='main-header'>📸 Retrato Algorítmico</h1>", unsafe_allow_html=True)
    st.markdown("<div class='tech-box'><div class='tech-title'>📚 Tecnologías:</div><div class='tech-item'>🤖 InstructPix2Pix (Image-to-Image) | 🧠 Computer Vision, Transfer Learning</div></div>", unsafe_allow_html=True)
    
    uploaded = st.file_uploader("Sube tu imagen", type=["jpg", "png"])
    prompt = st.text_area("Instrucción", placeholder="Ej: 'Conviértelo en pintura al óleo'")
    
    if st.button("Generar", type="primary", use_container_width=True):
        if not hf_token or not uploaded or not prompt:
            st.warning("Completa todos los campos.")
        else:
            with st.spinner("Procesando..."):
                img = Image.open(uploaded).convert("RGB").resize((512, 512))
                res = query_huggingface(
                    "https://api-inference.huggingface.co/models/timbrooks/instruct-pix2pix",
                    {"inputs": prompt, "parameters": {"image": image_to_base64(img), "num_inference_steps": 25}},
                    hf_token
                )
                if res:
                    st.success("¡Listo!")
                    st.image(Image.open(BytesIO(res)), caption="Resultado", use_container_width=True)

# --- OPCIÓN C: POEMA ---
elif opcion == "Poema":
    st.markdown("<h1 class='main-header'> Poema Visual</h1>", unsafe_allow_html=True)
    st.markdown("<div class='tech-box'><div class='tech-title'>📚 Tecnologías:</div><div class='tech-item'>🤖 Stable Diffusion v1.5 (Text-to-Image) | 🧠 Diffusion Models, Prompt Engineering</div></div>", unsafe_allow_html=True)
    
    texto = st.text_input("Palabra o frase", placeholder="Ej: 'Melancolía digital'")
    
    if st.button("Generar", type="primary", use_container_width=True):
        if not hf_token or not texto:
            st.warning("Completa los campos.")
        else:
            with st.spinner("Creando..."):
                res = query_huggingface(
                    "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
                    {"inputs": f"abstract art, {texto}, vibrant, masterpiece", "parameters": {"negative_prompt": "text, ugly"}},
                    hf_token
                )
                if res:
                    st.success("¡Listo!")
                    st.image(Image.open(BytesIO(res)), use_container_width=True)

# --- OPCIÓN D: MEMES ---
elif opcion == "Memes":
    st.markdown("<h1 class='main-header'> Generador de Memes</h1>", unsafe_allow_html=True)
    st.markdown("<div class='tech-box'><div class='tech-title'>📚 Tecnologías:</div><div class='tech-item'> Stable Diffusion + PIL ImageDraw |  Image Composition, Text Rendering</div></div>", unsafe_allow_html=True)
    
    desc = st.text_area("Situación", placeholder="Ej: 'Cuando el código compila a la primera'")
    t1 = st.text_input("Texto superior")
    t2 = st.text_input("Texto inferior")
    
    if st.button("Generar Meme", type="primary", use_container_width=True):
        if not hf_token or not desc:
            st.warning("Completa los campos.")
        else:
            with st.spinner("Creando meme..."):
                res = query_huggingface(
                    "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
                    {"inputs": f"meme style, {desc}, funny", "parameters": {"negative_prompt": "text, watermark"}},
                    hf_token
                )
                if res:
                    img = Image.open(BytesIO(res))
                    if t1 or t2: img = draw_meme_text(img, t1, t2)
                    st.success("¡Meme creado!")
                    st.image(img, use_container_width=True)

# --- OPCIÓN E: EMOCIONES ---
elif opcion == "Emociones":
    st.markdown("<h1 class='main-header'>💝 Visualizador de Emociones</h1>", unsafe_allow_html=True)
    st.markdown("<div class='tech-box'><div class='tech-title'> Tecnologías:</div><div class='tech-item'>🤖 NLP + Stable Diffusion | 🧠 Sentiment Analysis, Keyword Matching, Color Theory</div></div>", unsafe_allow_html=True)
    
    texto = st.text_area("Escribe un texto", height=100)
    
    if st.button("Visualizar", type="primary", use_container_width=True):
        if not hf_token or not texto:
            st.warning("Escribe un texto.")
        else:
            with st.spinner("Analizando..."):
                # NLP básico
                emots = {"alegria": ["feliz", "genial"], "tristeza": ["triste", "llorar"], "ira": ["odio", "furioso"]}
                detected = {k: sum(1 for w in v if w in texto.lower()) for k, v in emots.items()}
                dom = max(detected, key=detected.get) if any(detected.values()) else "neutral"
                
                styles = {"alegria": "bright yellow, sunny", "tristeza": "blue, rainy", "ira": "red, fiery", "neutral": "calm, balanced"}
                
                res = query_huggingface(
                    "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
                    {"inputs": f"abstract art, {styles[dom]}, emotion", "parameters": {"negative_prompt": "text"}},
                    hf_token
                )
                if res:
                    st.markdown(f"**Emoción detectada:** {dom.capitalize()}")
                    st.image(Image.open(BytesIO(res)), use_container_width=True)

# --- OPCIÓN F: HISTORIAS (Lógica de estado corregida) ---
elif opcion == "Historias":
    st.markdown("<h1 class='main-header'>📖 Historias Interactivas</h1>", unsafe_allow_html=True)
    st.markdown("<div class='tech-box'><div class='tech-title'>📚 Tecnologías:</div><div class='tech-item'>🤖 GPT-2 (Transformer) | 🧠 NLP, Text Generation, Autoregressive Models, Session State</div></div>", unsafe_allow_html=True)
    
    if "story" not in st.session_state:
        st.session_state.story = ""
    
    genero = st.selectbox("Género", ["Ciencia Ficcion", "Fantasia", "Terror"])
    
    if st.button("Iniciar Historia", type="primary", use_container_width=True):
        if hf_token:
            with st.spinner("Escribiendo..."):
                res = query_huggingface(
                    "https://api-inference.huggingface.co/models/gpt2",
                    {"inputs": f"En un mundo de {genero}, ", "parameters": {"max_new_tokens": 150, "temperature": 0.8}},
                    hf_token
                )
                if res:
                    try:
                        st.session_state.story = json.loads(res)[0]["generated_text"]
                    except: st.error("Error al generar.")
    
    if st.session_state.story:
        st.markdown("###  Tu historia:")
        st.write(st.session_state.story)
        
        decision = st.text_input("¿Qué hace el protagonista?")
        if st.button("Continuar"):
            if decision and hf_token:
                with st.spinner("Continuando..."):
                    res = query_huggingface(
                        "https://api-inference.huggingface.co/models/gpt2",
                        {"inputs": st.session_state.story + f" Entonces, {decision}", "parameters": {"max_new_tokens": 100}},
                        hf_token
                    )
                    if res:
                        try:
                            st.session_state.story = json.loads(res)[0]["generated_text"]
                            st.rerun()
                        except: st.error("Error al continuar.")

# --- OPCIÓN G: DATA ART ---
elif opcion == "DataArt":
    st.markdown("<h1 class='main-header'>📊 Data Art Generator</h1>", unsafe_allow_html=True)
    st.markdown("<div class='tech-box'><div class='tech-title'> Tecnologías:</div><div class='tech-item'>🤖 Stable Diffusion + Pandas/NumPy | 🧠 EDA, Statistical Analysis, Data Visualization</div></div>", unsafe_allow_html=True)
    
    csv = st.file_uploader("Sube un CSV", type=["csv"])
    if csv:
        df = pd.read_csv(csv)
        st.write(df.head())
        
        if st.button("Generar Arte con Datos", type="primary", use_container_width=True):
            if hf_token:
                with st.spinner("Analizando datos..."):
                    stats = df.describe().to_string()[:100] # Resumen simple
                    res = query_huggingface(
                        "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
                        {"inputs": f"abstract data art, geometric, {stats}", "parameters": {"negative_prompt": "text"}},
                        hf_token
                    )
                    if res:
                        st.image(Image.open(BytesIO(res)), use_container_width=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown("<div class='footer'>Galería Algorítmica · Instituto Data Science Argentina · 2026</div>", unsafe_allow_html=True)
