import streamlit as st
import requests
import time
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import json
import pandas as pd
import numpy as np

# ============================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Galería Algorítmica | Instituto Data Science Argentina",
    page_icon="",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ============================================================
# ESTILOS CSS PERSONALIZADOS
# ============================================================
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        font-family: 'Georgia', serif;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        font-size: 2.5rem;
    }
    .sub-header {
        text-align: center;
        color: #7f8c8d;
        font-style: italic;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }
    .project-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
    }
    .tech-box {
        background-color: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 8px;
        margin: 1.5rem 0;
    }
    .tech-title {
        color: #2c3e50;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    .tech-item {
        color: #34495e;
        margin: 0.3rem 0;
        font-size: 0.95rem;
    }
    .footer {
        text-align: center;
        color: #95a5a6;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #ecf0f1;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# GESTIÓN CENTRALIZADA DEL TOKEN DE HUGGING FACE
# ============================================================
hf_token = st.secrets.get("HF_TOKEN", "")

# ============================================================
# SIDEBAR: NAVEGACIÓN Y CONFIGURACIÓN
# ============================================================
st.sidebar.title("🖼️ Galería Algorítmica")
st.sidebar.markdown("**Instituto Data Science Argentina**")
st.sidebar.markdown("---")

opcion = st.sidebar.radio(
    "Elige una experiencia:",
    [
        "🏠 Inicio",
        "📸 Opción A: Retrato Algorítmico",
        "🎨 Opción C: Poema Visual",
        "😂 Opción D: Generador de Memes",
        " Opción E: Visualizador de Emociones",
        "📖 Opción F: Historias Interactivas",
        "📊 Opción G: Data Art Generator"
    ]
)

st.sidebar.markdown("---")

if not hf_token:
    with st.sidebar.expander("⚙️ Configurar Token de Hugging Face"):
        hf_token = st.text_input(
            "Hugging Face Token",
            type="password",
            help="Obtén tu token gratuito en huggingface.co/settings/tokens"
        )
        st.info("💡 Para producción, guarda tu token en `.streamlit/secrets.toml`")
else:
    st.sidebar.success("✅ Token de Hugging Face configurado")

st.sidebar.markdown("---")
st.sidebar.caption("Arte generado con IA · 100% Gratuito")

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================
def query_huggingface(api_url, payload, token, retries=3):
    """Función genérica para consultar la API de Hugging Face con reintentos."""
    headers = {"Authorization": f"Bearer {token}"}
    
    for attempt in range(retries):
        try:
            response = requests.post(
                api_url, 
                headers=headers, 
                json=payload,
                timeout=120
            )
            
            if response.status_code == 503:
                try:
                    error_data = response.json()
                    estimated_time = error_data.get("estimated_time", 20)
                except:
                    estimated_time = 20
                
                st.warning(f" El modelo está despertando... esperando {estimated_time:.0f} segundos (Intento {attempt + 1}/{retries})")
                time.sleep(estimated_time)
                continue
                
            elif response.status_code == 401:
                st.error("❌ Token de Hugging Face inválido.")
                return None
                
            elif response.status_code == 200:
                return response.content
                
            else:
                st.error(f"Error en la API: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            st.warning(f"🌐 Error de conexión. Reintentando... (Intento {attempt + 1}/{retries})")
            time.sleep(5)
            continue
            
        except requests.exceptions.Timeout:
            st.warning(f"⏱️ Timeout. Reintentando... (Intento {attempt + 1}/{retries})")
            time.sleep(5)
            continue
            
        except Exception as e:
            st.error(f"Error inesperado: {str(e)}")
            return None
    
    st.error("❌ No se pudo completar la solicitud después de varios intentos.")
    return None

def image_to_base64(image):
    """Convierte una imagen PIL a base64."""
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def create_meme_image(base_image, top_text, bottom_text):
    """Crea un meme con texto superpuesto."""
    img = base_image.copy()
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    width, height = img.size
    
    draw.text((width/2, 20), top_text, fill="white", font=font, anchor="mm", 
              stroke_width=2, stroke_fill="black")
    
    draw.text((width/2, height - 40), bottom_text, fill="white", font=font, anchor="mm",
              stroke_width=2, stroke_fill="black")
    
    return img

# ============================================================
# PÁGINA DE INICIO
# ============================================================
if opcion == "🏠 Inicio":
    st.markdown("<h1 class='main-header'>🎨 Galería Algorítmica</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Donde el arte se encuentra con los datos</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 2rem; border-radius: 12px; margin: 2rem 0;">
        <h3 style="color: #2c3e50; text-align: center;">Bienvenido a la Galería Algorítmica</h3>
        <p style="text-align: center; color: #7f8c8d; font-size: 1.1rem;">
            Explora 6 experiencias interactivas que combinan inteligencia artificial y creatividad.
            <br>Cada proyecto utiliza tecnologías específicas de Data Science.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='footer'>Galería Algorítmica · Instituto Data Science Argentina · 2026</div>", unsafe_allow_html=True)

# ============================================================
# OPCIÓN A: RETRATO ALGORÍTMICO
# ============================================================
elif opcion == "📸 Opción A: Retrato Algorítmico":
    st.markdown("<h1 class='main-header'>📸 Retrato Algorítmico</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Transforma tu rostro en una obra de arte digital</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tech-box">
        <div class="tech-title">📚 Tecnologías y Conceptos:</div>
        <div class="tech-item">🤖 <b>Modelo:</b> InstructPix2Pix (Image-to-Image Translation)</div>
        <div class="tech-item">🎯 <b>Tarea:</b> Edición de imágenes guiada por texto</div>
        <div class="tech-item">🧠 <b>Arquitectura:</b> Stable Diffusion + Instrucciones en lenguaje natural</div>
        <div class="tech-item">📦 <b>Librerías:</b> Pillow (procesamiento de imágenes), Base64 (codificación)</div>
        <div class="tech-item"> <b>Conceptos:</b> Computer Vision, Transfer Learning, Generative AI, Prompt Engineering</div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Elige una imagen", type=["jpg", "jpeg", "png"])
    instruction = st.text_area("Describe tu transformación", 
                               placeholder="Ej: 'Conviértelo en una pintura al óleo'")
    
    if st.button("🎨 Generar Retrato", type="primary", use_container_width=True):
        if not hf_token:
            st.warning("⚠️ Configura tu Hugging Face Token en la barra lateral.")
        elif not uploaded_file:
            st.warning("⚠️ Sube una imagen primero.")
        elif not instruction.strip():
            st.warning("️ Describe la transformación.")
        else:
            with st.spinner("🌌 Trabajando..."):
                input_image = Image.open(uploaded_file).convert("RGB").resize((512, 512))
                api_url = "https://api-inference.huggingface.co/models/timbrooks/instruct-pix2pix"
                
                payload = {
                    "inputs": instruction,
                    "parameters": {
                        "image": image_to_base64(input_image),
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5
                    }
                }
                
                image_bytes = query_huggingface(api_url, payload, hf_token)
                
                if image_bytes:
                    st.success("¡Retrato creado!")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Original**")
                        st.image(input_image, use_container_width=True)
                    with col2:
                        st.markdown("**Resultado**")
                        result_image = Image.open(BytesIO(image_bytes))
                        st.image(result_image, use_container_width=True)
                    
                    buf = BytesIO()
                    result_image.save(buf, format="PNG")
                    st.download_button(" Descargar", data=buf.getvalue(), 
                                      file_name="retrato_algoritmico.png", mime="image/png")

# ============================================================
# OPCIÓN C: POEMA VISUAL
# ============================================================
elif opcion == "🎨 Opción C: Poema Visual":
    st.markdown("<h1 class='main-header'>🎨 Generador de Poemas Visuales</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Escribe una palabra o frase. El algoritmo creará arte abstracto.</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tech-box">
        <div class="tech-title">📚 Tecnologías y Conceptos:</div>
        <div class="tech-item">🤖 <b>Modelo:</b> Stable Diffusion v1.5 (Text-to-Image)</div>
        <div class="tech-item">🎯 <b>Tarea:</b> Generación de imágenes desde texto</div>
        <div class="tech-item"> <b>Arquitectura:</b> Diffusion Models, Latent Space, U-Net</div>
        <div class="tech-item">📦 <b>Librerías:</b> PIL, Requests, JSON</div>
        <div class="tech-item">🎓 <b>Conceptos:</b> NLP (procesamiento de texto), Generative AI, Prompt Engineering, Negative Prompts, Diffusion Process</div>
    </div>
    """, unsafe_allow_html=True)
    
    user_input = st.text_input("✨ Tu poema o palabra clave:", 
                               placeholder="Ej: 'Melancolía digital', 'Café y código'")
    
    if st.button("Generar Poema Visual", type="primary", use_container_width=True):
        if not hf_token:
            st.warning("⚠️ Configura tu Hugging Face Token.")
        elif not user_input.strip():
            st.warning("⚠️ Escribe una palabra o frase.")
        else:
            with st.spinner("🌌 Tejiendo tu poema visual..."):
                enhanced_prompt = f"abstract art, visual poetry, {user_input}, vibrant colors, fluid shapes, digital masterpiece, ethereal"
                negative_prompt = "text, watermark, realistic, ugly, low quality"
                
                api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
                
                payload = {
                    "inputs": enhanced_prompt,
                    "parameters": {
                        "negative_prompt": negative_prompt,
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5
                    }
                }
                
                image_bytes = query_huggingface(api_url, payload, hf_token)
                
                if image_bytes:
                    st.success("¡Poema visual creado!")
                    image = Image.open(BytesIO(image_bytes))
                    st.image(image, caption=f"'{user_input}'", use_container_width=True)
                    
                    buf = BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("📥 Descargar", data=buf.getvalue(),
                                      file_name=f"poema_{user_input[:20]}.png", mime="image/png")

# ============================================================
# OPCIÓN D: GENERADOR DE MEMES
# ============================================================
elif opcion == "😂 Opción D: Generador de Memes":
    st.markdown("<h1 class='main-header'>😂 Generador de Memes con IA</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Describe una situación y la IA creará un meme único</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tech-box">
        <div class="tech-title">📚 Tecnologías y Conceptos:</div>
        <div class="tech-item">🤖 <b>Modelo:</b> Stable Diffusion v1.5 + Image Processing</div>
        <div class="tech-item">🎯 <b>Tarea:</b> Generación de imágenes + superposición de texto</div>
        <div class="tech-item">🧠 <b>Técnicas:</b> Text-to-Image, Image Manipulation, OCR (reconocimiento de texto)</div>
        <div class="tech-item">📦 <b>Librerías:</b> Pillow (ImageDraw, ImageFont), Base64</div>
        <div class="tech-item">🎓 <b>Conceptos:</b> Computer Vision, Text Rendering, Image Composition, Cultural Pattern Recognition, Viral Content Generation</div>
    </div>
    """, unsafe_allow_html=True)
    
    meme_prompt = st.text_area("Describe la situación del meme:",
                               placeholder="Ej: 'Cuando el código funciona a la primera'",
                               height=100)
    
    top_text = st.text_input("Texto superior (opcional):", placeholder="Ej: 'YO:'")
    bottom_text = st.text_input("Texto inferior (opcional):", placeholder="Ej: 'EL CÓDIGO:'")
    
    if st.button("🎨 Generar Meme", type="primary", use_container_width=True):
        if not hf_token:
            st.warning("️ Configura tu Hugging Face Token.")
        elif not meme_prompt.strip():
            st.warning("⚠️ Describe una situación.")
        else:
            with st.spinner("🎨 Creando meme..."):
                enhanced_prompt = f"meme, funny image, {meme_prompt}, humorous, viral, internet culture, simple background"
                negative_prompt = "text, watermark, realistic, ugly, low quality, complex"
                
                api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
                
                payload = {
                    "inputs": enhanced_prompt,
                    "parameters": {
                        "negative_prompt": negative_prompt,
                        "num_inference_steps": 25,
                        "guidance_scale": 7.0
                    }
                }
                
                image_bytes = query_huggingface(api_url, payload, hf_token)
                
                if image_bytes:
                    base_image = Image.open(BytesIO(image_bytes))
                    
                    if top_text or bottom_text:
                        meme_image = create_meme_image(base_image, top_text, bottom_text)
                    else:
                        meme_image = base_image
                    
                    st.success("¡Meme creado!")
                    st.image(meme_image, caption=f"Meme: '{meme_prompt}'", use_container_width=True)
                    
                    buf = BytesIO()
                    meme_image.save(buf, format="PNG")
                    st.download_button("📥 Descargar Meme", data=buf.getvalue(),
                                      file_name="meme_ia.png", mime="image/png")

# ============================================================
# OPCIÓN E: VISUALIZADOR DE EMOCIONES
# ============================================================
elif opcion == "💝 Opción E: Visualizador de Emociones":
    st.markdown("<h1 class='main-header'>💝 Visualizador de Emociones</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Escribe un texto y la IA visualizará las emociones en arte</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tech-box">
        <div class="tech-title">📚 Tecnologías y Conceptos:</div>
        <div class="tech-item"> <b>Modelo:</b> Stable Diffusion + NLP (Análisis de Sentimientos)</div>
        <div class="tech-item">🎯 <b>Tarea:</b> Análisis de texto + generación de arte emocional</div>
        <div class="tech-item">🧠 <b>Técnicas:</b> Keyword Matching, Sentiment Analysis, Emotion Detection</div>
        <div class="tech-item">📦 <b>Librerías:</b> NLP básico (string matching), Stable Diffusion API</div>
        <div class="tech-item">🎓 <b>Conceptos:</b> Natural Language Processing (NLP), Sentiment Analysis, Emotion Classification, Text Mining, Color Theory, Data Visualization</div>
        <div class="tech-item">💡 <b>Próximo nivel:</b> Modelos como RoBERTa, BERT para análisis más preciso</div>
    </div>
    """, unsafe_allow_html=True)
    
    emotion_text = st.text_area("Escribe un texto (tweet, poema, mensaje):",
                                placeholder="Ej: 'Estoy muy feliz hoy, el sol brilla y todo es maravilloso'",
                                height=100)
    
    if st.button("💝 Visualizar Emociones", type="primary", use_container_width=True):
        if not hf_token:
            st.warning("⚠️ Configura tu Hugging Face Token.")
        elif not emotion_text.strip():
            st.warning("⚠️ Escribe un texto.")
        else:
            with st.spinner("🎨 Analizando emociones..."):
                emotion_keywords = {
                    "alegría": ["feliz", "alegre", "contento", "maravilloso", "excelente", "genial"],
                    "tristeza": ["triste", "melancólico", "deprimido", "llorar", "dolor"],
                    "ira": ["enojado", "furioso", "molesto", "irritado", "odio"],
                    "miedo": ["miedo", "terror", "asustado", "pánico", "ansiedad"],
                    "sorpresa": ["sorprendido", "asombrado", "increíble", "wow", "impresionado"]
                }
                
                text_lower = emotion_text.lower()
                emotions_detected = {}
                
                for emotion, keywords in emotion_keywords.items():
                    count = sum(1 for word in keywords if word in text_lower)
                    if count > 0:
                        emotions_detected[emotion] = count
                
                if not emotions_detected:
                    emotions_detected["neutral"] = 1
                
                emotion_art_map = {
                    "alegría": "bright yellow and orange colors, sunny, cheerful, warm",
                    "tristeza": "blue and gray colors, melancholic, rainy, somber",
                    "ira": "red and black colors, fiery, intense, dramatic",
                    "miedo": "dark purple and black, mysterious, shadowy, eerie",
                    "sorpresa": "vibrant multicolor, explosive, dynamic, energetic",
                    "neutral": "balanced colors, calm, peaceful, serene"
                }
                
                dominant_emotion = max(emotions_detected, key=emotions_detected.get)
                art_style = emotion_art_map[dominant_emotion]
                
                enhanced_prompt = f"abstract art, {art_style}, emotion visualization, {emotion_text[:50]}, expressive, artistic"
                negative_prompt = "text, watermark, realistic, ugly"
                
                api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
                
                payload = {
                    "inputs": enhanced_prompt,
                    "parameters": {
                        "negative_prompt": negative_prompt,
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5
                    }
                }
                
                image_bytes = query_huggingface(api_url, payload, hf_token)
                
                if image_bytes:
                    st.success("¡Emociones visualizadas!")
                    
                    st.markdown("### 📊 Emociones detectadas:")
                    for emotion, intensity in emotions_detected.items():
                        st.write(f"- **{emotion.capitalize()}**: {'❤️' * intensity}")
                    
                    st.markdown(f"**Emoción dominante:** {dominant_emotion.capitalize()}")
                    
                    image = Image.open(BytesIO(image_bytes))
                    st.image(image, caption=f"Visualización de: '{emotion_text[:50]}...'", use_container_width=True)
                    
                    buf = BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("📥 Descargar", data=buf.getvalue(),
                                      file_name=f"emociones_{dominant_emotion}.png", mime="image/png")

# ============================================================
# OPCIÓN F: HISTORIAS INTERACTIVAS
# ============================================================
elif opcion == " Opción F: Historias Interactivas":
    st.markdown("<h1 class='main-header'>📖 Generador de Historias Interactivas</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Elige un género y la IA creará una historia con decisiones</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tech-box">
        <div class="tech-title">📚 Tecnologías y Conceptos:</div>
        <div class="tech-item"> <b>Modelo:</b> GPT-2 (Generative Pre-trained Transformer)</div>
        <div class="tech-item"> <b>Tarea:</b> Generación de texto narrativo interactivo</div>
        <div class="tech-item">🧠 <b>Arquitectura:</b> Transformer, Attention Mechanism, Autoregressive Generation</div>
        <div class="tech-item">📦 <b>Librerías:</b> JSON (parsing de respuestas), Session State (Streamlit)</div>
        <div class="tech-item">🎓 <b>Conceptos:</b> NLP, Language Modeling, Text Generation, Temperature Sampling, Top-p Sampling, Context Windows, Storytelling AI, Interactive Narrative</div>
        <div class="tech-item">💡 <b>Próximo nivel:</b> GPT-3, GPT-Neo, o fine-tuning en datasets de historias</div>
    </div>
    """, unsafe_allow_html=True)
    
    genre = st.selectbox("Elige un género:", 
                         ["Ciencia Ficción", "Fantasía", "Terror", "Romance", "Aventura"])
    
    if "story_history" not in st.session_state:
        st.session_state.story_history = []
        st.session_state.current_story = ""
    
    if st.button("📖 Iniciar Nueva Historia", type="primary", use_container_width=True):
        if not hf_token:
            st.warning("⚠️ Configura tu Hugging Face Token.")
        else:
            with st.spinner(" Generando historia..."):
                prompt = f"Érase una vez en un mundo de {genre.lower()}. "
                
                api_url = "https://api-inference.huggingface.co/models/gpt2"
                
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 200,
                        "temperature": 0.8,
                        "top_p": 0.9
                    }
                }
                
                response_content = query_huggingface(api_url, payload, hf_token)
                
                if response_content:
                    try:
                        story_data = json.loads(response_content)
                        generated_text = story_data[0]["generated_text"]
                        st.session_state.current_story = generated_text
                        st.session_state.story_history = [generated_text]
                    except:
                        st.error("Error al procesar la historia.")
    
    if st.session_state.current_story:
        st.markdown("### 📖 Tu historia:")
        st.write(st.session_state.current_story)
        
        st.markdown("###  ¿Qué happens next?")
        choice1 = st.text_input("Opción 1:", placeholder="Ej: 'Abre la puerta misteriosa'")
        choice2 = st.text_input("Opción 2:", placeholder="Ej: 'Huye del lugar'")
        
        if st.button("🔄 Continuar historia", use_container_width=True):
            if choice1 or choice2:
                with st.spinner("📚 Continuando..."):
                    continuation = f"{st.session_state.current_story} {choice1 or choice2}"
                    
                    api_url = "https://api-inference.huggingface.co/models/gpt2"
                    payload = {
                        "inputs": continuation,
                        "parameters": {
                            "max_new_tokens": 150,
                            "temperature": 0.8
                        }
                    }
                    
                    response_content = query_huggingface(api_url, payload, hf_token)
                    
                    if response_content:
                        try:
                            story_data = json.loads(response_content)
                            new_text = story_data[0]["generated_text"]
                            st.session_state.current_story = new_text
                            st.session_state.story_history.append(new_text)
                            st.rerun()
                        except:
                            st.error("Error al continuar la historia.")

# ============================================================
# OPCIÓN G: DATA ART GENERATOR
# ============================================================
elif opcion == " Opción G: Data Art Generator":
    st.markdown("<h1 class='main-header'> Data Art Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Transforma tus datos en una pieza de arte única</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tech-box">
        <div class="tech-title">📚 Tecnologías y Conceptos:</div>
        <div class="tech-item"> <b>Modelo:</b> Stable Diffusion + Análisis Estadístico</div>
        <div class="tech-item">🎯 <b>Tarea:</b> Análisis de datos + visualización artística</div>
        <div class="tech-item">🧠 <b>Técnicas:</b> Estadística descriptiva, Data Visualization, Feature Extraction</div>
        <div class="tech-item">📦 <b>Librerías:</b> Pandas (DataFrames), NumPy (cálculo numérico), CSV parsing</div>
        <div class="tech-item">🎓 <b>Conceptos:</b> Data Analysis, Statistical Measures (mean, std), Data Preprocessing, Exploratory Data Analysis (EDA), Data-Driven Art, Information Visualization, Pattern Recognition</div>
        <div class="tech-item">💡 <b>Próximo nivel:</b> PCA, t-SNE para reducción dimensional, clustering con K-Means</div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_csv = st.file_uploader("Sube un archivo CSV:", type=["csv"])
    
    if uploaded_csv:
        try:
            df = pd.read_csv(uploaded_csv)
            st.success(f"✅ Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
            
            st.markdown("### 📈 Estadísticas del dataset:")
            st.write(df.describe())
            
            if st.button("🎨 Generar Data Art", type="primary", use_container_width=True):
                if not hf_token:
                    st.warning("⚠️ Configura tu Hugging Face Token.")
                else:
                    with st.spinner("📊 Analizando datos y generando arte..."):
                        num_cols = df.select_dtypes(include=[np.number]).columns
                        stats = []
                        
                        if len(num_cols) > 0:
                            for col in num_cols[:3]:
                                mean_val = df[col].mean()
                                std_val = df[col].std()
                                stats.append(f"{col}: media={mean_val:.2f}, std={std_val:.2f}")
                        
                        data_description = ", ".join(stats) if stats else "datos variados"
                        
                        enhanced_prompt = f"abstract data visualization art, {data_description}, geometric patterns, data-driven art, modern, colorful, digital"
                        negative_prompt = "text, watermark, realistic, ugly, low quality"
                        
                        api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
                        
                        payload = {
                            "inputs": enhanced_prompt,
                            "parameters": {
                                "negative_prompt": negative_prompt,
                                "num_inference_steps": 30,
                                "guidance_scale": 7.5
                            }
                        }
                        
                        image_bytes = query_huggingface(api_url, payload, hf_token)
                        
                        if image_bytes:
                            st.success("¡Data Art creado!")
                            image = Image.open(BytesIO(image_bytes))
                            st.image(image, caption="Arte generado desde tus datos", use_container_width=True)
                            
                            buf = BytesIO()
                            image.save(buf, format="PNG")
                            st.download_button("📥 Descargar Data Art", data=buf.getvalue(),
                                              file_name="data_art.png", mime="image/png")
        except Exception as e:
            st.error(f"Error al procesar el CSV: {str(e)}")
    else:
        st.info("📤 Sube un archivo CSV para comenzar")

# ============================================================
# FOOTER
# ============================================================
st.markdown("<div class='footer'>Galería Algorítmica · Instituto Data Science Argentina · 2026</div>", unsafe_allow_html=True)
