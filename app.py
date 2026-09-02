import streamlit as st
import requests
import time
import json
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Galería Algorítmica | IDSA",
    page_icon="🎨",
    layout="wide",  # Cambiado a wide para acomodar mejor los páneles y las pestañas educativas
    initial_sidebar_state="expanded"
)

# Set matplotlib to non-interactive mode
import matplotlib
matplotlib.use('Agg')

# ============================================================
# 2. ESTILOS CSS CON CLIMA ARTÍSTICO Y CORPORATIVO
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Lora:ital@0;1&family=Fira+Code:wght@400;500&display=swap');
    
    .main-header {
        font-family: 'Playfair Display', serif;
        color: #1E3A8A;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.1rem;
    }
    .sub-header {
        font-family: 'Lora', Georgia, serif;
        color: #4B5563;
        font-size: 1.25rem;
        font-style: italic;
        margin-bottom: 2rem;
    }
    .business-card {
        background-color: #F0FDF4;
        border-left: 5px solid #16A34A;
        padding: 1.5rem;
        border-radius: 4px;
        margin-bottom: 1.5rem;
    }
    .theory-card {
        background-color: #EFF6FF;
        border-left: 5px solid #2563EB;
        padding: 1.5rem;
        border-radius: 4px;
        margin-bottom: 1.5rem;
    }
    .code-title {
        font-family: 'Fira Code', monospace;
        font-size: 1.1rem;
        color: #D97706;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. GESTIÓN DE TOKEN Y NAVEGACIÓN ROBUSTA (AMPLIADA)
# ============================================================
hf_token = st.secrets.get("HF_TOKEN", "")

st.sidebar.title("🖼️ Galería Algorítmica v2")
st.sidebar.markdown("**Instituto Data Science Argentina**")
st.sidebar.markdown("*De la Imaginación a la Ingeniería de Negocios*")
st.sidebar.markdown("---")

# Menú extendido con las 4 nuevas propuestas alineadas a negocios
menu_keys = [
    "Inicio", 
    "Retrato", 
    "Poema", 
    "Memes", 
    "Emociones", 
    "Historias", 
    "DataArt",
    "Rockola",    # Nueva: Audio & Speech
    "Curador",    # Nueva: Búsqueda Multimodal
    "Oraculo",    # Nueva: RAG & LLMs
    "Tasador"     # Nueva: ML Predictivo Tabular
]

menu_labels = {
    "Inicio": "🏠 Inicio",
    "Retrato": "📸 Retrato Algorítmico",
    "Poema": "🎨 Poema Visual",
    "Memes": "😂 Generador de Memes",
    "Emociones": "💝 Visualizador de Emociones",
    "Historias": "📖 Historias Interactivas",
    "DataArt": "📊 Data Art Generator",
    "Rockola": "🎙️ La Rockola de la IA",
    "Curador": "🔍 El Curador Inteligente",
    "Oraculo": "📜 El Oráculo de la Historia",
    "Tasador": "🔮 El Tasador Algorítmico"
}

opcion = st.sidebar.radio(
    "Selecciona una experiencia:",
    menu_keys,
    format_func=lambda x: menu_labels[x]
)

st.sidebar.markdown("---")
if not hf_token:
    with st.sidebar.expander("⚙️ Configurar Token"):
        hf_token = st.text_input("Hugging Face Token", type="password")
        st.info("💡 Consejo: Guárdalo en Streamlit Secrets para producción.")
else:
    st.sidebar.success("✅ Token configurado de forma segura")

st.sidebar.caption("IDSA · Laboratorio de Innovación Curricular")

# ============================================================
# 4. FUNCIONES AUXILIARES BLINDADAS Y NUEVAS LÓGICAS
# ============================================================
def query_huggingface(api_url, payload, token, retries=5):
    """Consulta la API de Hugging Face de forma resiliente."""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    for i in range(retries):
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.content
            elif response.status_code == 503:
                # Modelo cargando en HF, esperar y reintentar
                time.sleep(8)
            else:
                st.error(f"Error de API Hugging Face: {response.status_code} - {response.text}")
                break
        except requests.exceptions.RequestException as e:
            time.sleep(2)
    return None

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def draw_meme_text(img, top_text, bottom_text):
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default() # Simplificado para portabilidad extrema en contenedores
    except OSError:
        font = ImageFont.load_default()
    w, h = img.size
    
    # Renderizado básico de texto en imagen
    if top_text:
        draw.text((w/2, 40), top_text.upper(), fill="white", font=font, anchor="mm", stroke_width=2, stroke_fill="black")
    if bottom_text:
        draw.text((w/2, h - 40), bottom_text.upper(), fill="white", font=font, anchor="mm", stroke_width=2, stroke_fill="black")
    return img

# ============================================================
# 5. ESTRUCTURA DE LAS PÁGINAS Y CONTENIDOS COMPLETOS
# ============================================================

# --- INICIO ---
if opcion == "Inicio":
    st.markdown("<h1 class='main-header'>🎨 Galería Algorítmica v2</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Donde el código creativo se convierte en soluciones de negocio</p>", unsafe_allow_html=True)
    
    st.markdown("""
    ### ¡Bienvenido al Laboratorio Curricular del IDSA!
    Esta plataforma interactiva está diseñada para guiarte en una ruta formativa disruptiva. Aquí, cada experiencia 
    comienza como un **juego creativo** (el \"gancho\" para despertar tu curiosidad) y evoluciona hacia una **solución 
    de negocios real**, desglosando los conceptos matemáticos subyacentes y entregándote el código Python exacto.
    
    #### 🚀 Explora las Experiencias en la Barra Lateral:
    1. **Fase Creativa:** Juega, interactúa y genera activos directamente en la app.
    2. **Fase Corporativa:** Entiende cómo las marcas usan esta misma tecnología para facturar millones o automatizar operaciones.
    3. **Fase de Ingeniería:** Domina el código detrás de la magia.
    """)
    
    # Mostrar resumen de las rutas formativas en columnas estéticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📊 **Ruta 1: Visión e Imagen**\n\nAutomatización visual, marketing dinámico y catálogos inteligentes con Stable Diffusion y PIL.")
    with col2:
        st.success("🗣️ **Ruta 2: NLP y Audio**\n\nAsistentes de voz corporativos, análisis afectivo e interfaces RAG conversacionales avanzadas.")
    with col3:
        st.warning("🔮 **Ruta 3: Analítica y Regresión**\n\nData storytelling corporativo, valorización predictiva y modelos tabulares de Machine Learning.")

# --- 1. RETRATO ALGORÍTMICO ---
elif opcion == "Retrato":
    st.markdown("<h1 class='main-header'>📸 Retrato Algorítmico</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Edición de imágenes guiada por instrucciones contextuales</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Experiencia Creativa", "💼 Pivot de Negocios", "🔬 Fundamentos Académicos", "🐍 Código Python"])
    
    with tab1:
        st.subheader("Transformación guiada por texto (InstructPix2Pix)")
        uploaded_file = st.file_uploader("Sube un retrato base:", type=["jpg", "png", "jpeg"])
        instruction = st.text_input("¿Qué cambio quieres aplicar?", placeholder="Haz que parezca un cuadro impresionista de Van Gogh")
        
        if st.button("Aplicar Transformación") and uploaded_file and instruction:
            if not hf_token:
                st.error("Por favor, ingresa tu Hugging Face Token en la barra lateral para procesar.")
            else:
                with st.spinner("Reinterpretando los píxeles del lienzo..."):
                    img = Image.open(uploaded_file)
                    img_b64 = image_to_base64(img)
                    api_url = "https://api-inference.huggingface.co/models/timbrooks/instruct-pix2pix"
                    payload = {"inputs": instruction, "image": img_b64}
                    result = query_huggingface(api_url, payload, hf_token)
                    if result:
                        st.image(Image.open(BytesIO(result)), caption="Resultado Algorítmico", use_column_width=True)
                    else:
                        st.error("No se pudo obtener una respuesta del modelo. Reintenta en unos instantes.")
                        
    with tab2:
        st.markdown("""
        <div class='business-card'>
            <h4>💼 Aplicación Comercial: Localización de Catálogos de E-Commerce</h4>
            <p>En lugar de pagar sesiones fotográficas millonarias para adaptar modelos a diferentes estaciones, geografías o festividades, las grandes empresas de moda y retail usan modelos de <b>Image-to-Image</b> para modificar ropa o fondos dinámicamente según el mercado objetivo.</p>
            <ul>
                <li><b>Valor de negocio:</b> Reducción del 90% en costos de pre-producción de catálogos y personalización visual demográfica en tiempo real.</li>
                <li><b>Ejemplo de uso:</b> Cambiar instantáneamente una chaqueta de verano a invierno sobre el mismo modelo físico.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with tab3:
        st.markdown("""
        <div class='theory-card'>
            <h4>🔬 El Algoritmo Detrás de la Edición</h4>
            <p><b>InstructPix2Pix</b> une dos dominios: la comprensión lingüística profunda y la síntesis espacial de imágenes. Utiliza un codificador de texto <b>CLIP</b> para mapear la directiva ("instruction") y la procesa junto a la representación latente de la imagen original a través de una arquitectura <b>U-Net</b> entrenada para predecir y ajustar los coeficientes de difusión de forma condicionada.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab4:
        st.code("""
import requests
import base64
from io import BytesIO
from PIL import Image

# Función para convertir imagen local a base64
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Configuración de llamada a Hugging Face
API_URL = "https://api-inference.huggingface.co/models/timbrooks/instruct-pix2pix"
headers = {"Authorization": "Bearer TU_HF_TOKEN"}

payload = {
    "inputs": "Convert the background to a sunny beach",
    "image": image_to_base64("retrato_base.jpg")
}

response = requests.post(API_URL, headers=headers, json=payload)
if response.status_code == 200:
    img_resultado = Image.open(BytesIO(response.content))
    img_resultado.save("retrato_negocios.jpg")
        """, language="python")

# --- 2. POEMA VISUAL ---
elif opcion == "Poema":
    st.markdown("<h1 class='main-header'>🎨 Poema Visual</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Generación artística a partir del espacio de latencia</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Experiencia Creativa", "💼 Pivot de Negocios", "🔬 Fundamentos Académicos", "🐍 Código Python"])
    
    with tab1:
        st.subheader("Traducción de Letras en Formas (Stable Diffusion v1.5)")
        poem_prompt = st.text_area("Escribe un micro-poema o prompt abstracto:", "Un faro solitario en medio de una tormenta digital, estilo surrealista, óleo de alta resolución.")
        cfg_scale = st.slider("Escala de Guía de Inferencia (CFG Scale):", 1.0, 20.0, 7.5, help="Controla qué tan fiel es la IA al texto original.")
        
        if st.button("Materializar Poema"):
            if not hf_token:
                st.error("Se requiere configurar el token en la barra lateral.")
            else:
                with st.spinner("Pintando en el lienzo latente..."):
                    api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
                    payload = {"inputs": poem_prompt, "parameters": {"guidance_scale": cfg_scale}}
                    result = query_huggingface(api_url, payload, hf_token)
                    if result:
                        st.image(Image.open(BytesIO(result)), caption="Arte Abstracto Autogenerado")
                    else:
                        st.error("Fallo de inferencia de red. Reintenta.")
                        
    with tab2:
        st.markdown("""
        <div class='business-card'>
            <h4>💼 Aplicación Comercial: Generación Automatizada de Activos de Marketing</h4>
            <p>En agencias de diseño y publicidad, la conceptualización veloz ahorra cientos de horas hombre. El Text-to-Image permite crear layouts publicitarios de prueba o generar variaciones masivas de fondos e isotipos de marca sin requerir bocetados manuales costosos en fases iniciales.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab3:
        st.markdown("""
        <div class='theory-card'>
            <h4>🔬 ¿Cómo sueña Stable Diffusion?</h4>
            <p>Los modelos de difusión inversa parten de una matriz de ruido Gaussiano puro y, de forma iterativa y matemática, remueven el ruido guiados por la codificación semántica del texto a través de un espacio de latencia comprimido por un autocodificador variacional (VAE).</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab4:
        st.code("""
import requests
from io import BytesIO
from PIL import Image

API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
headers = {"Authorization": "Bearer TU_HF_TOKEN"}

payload = {
    "inputs": "Abstract art of a corporate growth chart, digital oil painting",
    "parameters": {"guidance_scale": 8.5}
}

response = requests.post(API_URL, headers=headers, json=payload)
img = Image.open(BytesIO(response.content))
img.save("visual_marketing.png")
        """, language="python")

# --- 3. GENERADOR DE MEMES ---
elif opcion == "Memes":
    st.markdown("<h1 class='main-header'>😂 Generador de Memes</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Manipulación paramétrica y superposición de capas vectoriales</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Experiencia Creativa", "💼 Pivot de Negocios", "🔬 Fundamentos Académicos", "🐍 Código Python"])
    
    with tab1:
        st.subheader("Crea tu meme con IA y Pillow")
        base_prompt = st.text_input("Imagen de fondo para el meme:", "Un programador cansado mirando la pantalla de una computadora portátil")
        top_text = st.text_input("Texto Superior:", "CUANDO EL CÓDIGO COMPILA")
        bottom_text = st.text_input("Texto Inferior:", "A LA PRIMERA")
        
        if st.button("Generar Meme"):
            if not hf_token:
                st.error("Token de Hugging Face requerido en la barra lateral.")
            else:
                with st.spinner("Generando plantilla de meme con IA..."):
                    api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
                    result = query_huggingface(api_url, {"inputs": base_prompt}, hf_token)
                    if result:
                        img = Image.open(BytesIO(result))
                        meme_img = draw_meme_text(img, top_text, bottom_text)
                        st.image(meme_img, caption="Meme Académico IDSA")
                    else:
                        st.error("No se pudo obtener el fondo de forma remota.")
                        
    with tab2:
        st.markdown("""
        <div class='business-card'>
            <h4>💼 Aplicación Comercial: Generadores de Banners Dinámicos</h4>
            <p>Esta lógica de manipulación digital es el núcleo de los motores de anuncios inteligentes de plataformas de E-Commerce (como MercadoLibre o Amazon). Permite tomar una fotografía base producida por IA y superponer datos dinámicos como precios, porcentajes de descuento y nombres de usuario personalizados en tiempo de ejecución.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab3:
        st.markdown("""
        <div class='theory-card'>
            <h4>🔬 Coordenadas Bidimensionales y Superposición</h4>
            <p>Trabajar con capas digitales requiere dominar el espacio cartesiano de pixeles <i>(x, y)</i> donde la esquina superior izquierda representa el origen (0,0). La librería Pillow de Python permite manipular matrices bidimensionales, mapear anclajes y trazar fuentes vectoriales en base a posiciones calculadas de forma dinámica según el ancho y alto del canvas.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab4:
        st.code("""
from PIL import Image, ImageDraw, ImageFont

def render_ad_banner(img_path, discount_text):
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    
    # Dibujar cuadro de descuento de forma determinista
    draw.rectangle([10, 10, 200, 60], fill="red")
    draw.text((20, 20), discount_text, fill="white", font=font)
    img.save("banner_oferta.png")
        """, language="python")

# --- 4. VISUALIZADOR DE EMOCIONES ---
elif opcion == "Emociones":
    st.markdown("<h1 class='main-header'>💝 Visualizador de Emociones</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Sentiment Analysis aplicado al mapeo cromático de arte</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Experiencia Creativa", "💼 Pivot de Negocios", "🔬 Fundamentos Académicos", "🐍 Código Python"])
    
    with tab1:
        st.subheader("Expresa tus sentimientos y mira el color resultante")
        sentiment_input = st.text_area("¿Cómo estuvo tu día? Escríbelo en inglés (para mayor precisión del analizador):", "I had an amazing and incredibly productive day at work today, I feel so happy!")
        
        if st.button("Mapear Estado de Ánimo"):
            if not hf_token:
                st.error("Token de Hugging Face requerido en la barra lateral.")
            else:
                with st.spinner("Analizando semántica emocional..."):
                    # 1. Análisis de Sentimiento con DistilBERT
                    api_sentiment = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"
                    sentiment_res = query_huggingface(api_sentiment, {"inputs": sentiment_input}, hf_token)
                    
                    if sentiment_res:
                        try:
                            # Parsear respuesta JSON
                            res_json = json.loads(sentiment_res.decode("utf-8"))
                            # Obtener el sentimiento predominante
                            scores = res_json[0]
                            pred = max(scores, key=lambda x: x['score'])
                            label = pred['label']
                            conf = pred['score']
                            
                            st.write(f"**Sentimiento Detectado:** {label} ({conf:.2%} de confianza)")
                            
                            # 2. Mapear Emoción a Prompts de color artísticos
                            if label == "POSITIVE":
                                prompt_arte = "Vibrant warm colors, yellow and orange sunset palette, hopeful expressionist painting, joy"
                            else:
                                prompt_arte = "Dark cold colors, deep blue and prussian grey palette, melancholic impressionist painting, solitude"
                                
                            # 3. Generar la obra visual
                            api_diff = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
                            art_res = query_huggingface(api_diff, {"inputs": prompt_arte}, hf_token)
                            if art_res:
                                st.image(Image.open(BytesIO(art_res)), caption="Tu Estado de Ánimo en el Lienzo Algorítmico")
                        except Exception as e:
                            st.error(f"Error al procesar la emoción: {e}")
                            
    with tab2:
        st.markdown("""
        <div class='business-card'>
            <h4>💼 Aplicación Comercial: Auditoría de Experiencia y Salud de Marca</h4>
            <p>La combinación de análisis lingüístico con variables visuales se traduce en el mundo empresarial en <b>Brand Health Monitoring</b>. Las corporaciones procesan miles de comentarios y tweets diarios sobre su marca, los categorizan automáticamente y diseñan tableros ejecutivos codificados por colores para reaccionar a crisis de relaciones públicas en tiempo real.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab3:
        st.markdown("""
        <div class='theory-card'>
            <h4>🔬 Arquitecturas de Transformación Afectiva</h4>
            <p>Los clasificadores de sentimientos modernos (como <b>DistilBERT</b>) procesan los tokens del texto a través de capas de autoatención para capturar las sutilezas gramaticales y contextuales que diferencian un halago de un sarcasmo. La salida de este clasificador es un vector de probabilidad multiclase que permite gatillar flujos condicionales de software de forma automatizada.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab4:
        st.code("""
import requests
import json

# Clasificador de Sentimiento con Hugging Face
API_SENTIMENT = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"
headers = {"Authorization": "Bearer TU_HF_TOKEN"}

texto = "I love this product, it solved all my operational problems!"
res = requests.post(API_SENTIMENT, headers=headers, json={"inputs": texto})
resultado = json.loads(res.content.decode("utf-8"))

# Mapear lógica de respuesta de negocios
sentimiento = max(resultado[0], key=lambda x: x['score'])
if sentiment['label'] == 'POSITIVE':
    print("Acción de negocio: Enviar cupón de fidelización")
else:
    print("Acción de negocio: Alerta para soporte prioritario")
        """, language="python")

# --- 5. HISTORIAS INTERACTIVAS ---
elif opcion == "Historias":
    st.markdown("<h1 class='main-header'>📖 Historias Interactivas</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Modelado de lenguaje secuencial con persistencia de estados</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Experiencia Creativa", "💼 Pivot de Negocios", "🔬 Fundamentos Académicos", "🐍 Código Python"])
    
    # Inicialización de historial en Session State si no existe
    if "story_context" not in st.session_state:
        st.session_state.story_context = "Once upon a time, in a high-tech data lab at IDSA, a young data scientist booted an algorithm."
    
    with tab1:
        st.subheader("Co-creación Narrativa Inteligente (GPT-2 / Text Gen)")
        st.text_area("Contexto Actual de la Historia:", st.session_state.story_context, height=150, disabled=True)
        
        user_input = st.text_input("Ingresa tu aporte o acción al relato:", "Suddenly, the computer screens began to display mysterious red coordinates.")
        
        if st.button("Continuar Relato"):
            if not hf_token:
                st.error("Configura el token en la barra de navegación para usar modelos lingüísticos.")
            else:
                with st.spinner("La IA está escribiendo el siguiente capítulo..."):
                    # Concatenamos la acción del usuario al contexto
                    full_prompt = f"{st.session_state.story_context} {user_input}"
                    api_text = "https://api-inference.huggingface.co/models/gpt2"
                    
                    result = query_huggingface(api_text, {"inputs": full_prompt, "parameters": {"max_new_tokens": 50}}, hf_token)
                    if result:
                        try:
                            res_json = json.loads(result.decode("utf-8"))
                            generated_text = res_json[0]['generated_text']
                            # Actualizar contexto de sesión
                            st.session_state.story_context = generated_text
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error de des-serialización textual: {e}")
                            
        if st.button("Reiniciar Relato"):
            st.session_state.story_context = "Once upon a time, in a high-tech data lab at IDSA, a young data scientist booted an algorithm."
            st.rerun()
            
    with tab2:
        st.markdown("""
        <div class='business-card'>
            <h4>💼 Aplicación Comercial: Asistentes de Venta Consultiva e Interactiva</h4>
            <p>Los modelos secuenciales de texto autogenerativo estructuran las bases de los <b>Asistentes Virtuales Conversacionales</b> que guían a los leads por el embudo de ventas. Al preservar el historial y la memoria de la conversación, el agente puede sugerir el software óptimo basándose en los problemas expresados previamente por el cliente.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab3:
        st.markdown("""
        <div class='theory-card'>
            <h4>🔬 Ventanas de Contexto y Decodificación Probabilística</h4>
            <p>Los modelos autorregresivos predicen secuencialmente el próximo token basándose únicamente en el histórico de tokens previos. La <b>temperatura</b> regula la entropía probabilística de la salida: temperaturas bajas (&lt; 0.5) devuelven respuestas lógicas y deterministas de negocio, mientras que temperaturas altas (&gt; 0.8) induen creatividad e impredecibilidad literaria.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab4:
        st.code("""
import requests
import json

# Generación conversacional estructurada
API_TEXT = "https://api-inference.huggingface.co/models/gpt2"
headers = {"Authorization": "Bearer TU_HF_TOKEN"}

contexto_comercial = "User: How can I double my sales using data? Assistant:"
payload = {
    "inputs": contexto_comercial,
    "parameters": {
        "max_new_tokens": 40,
        "temperature": 0.3  # Baja temperatura para respuestas lógicas de negocios
    }
}

response = requests.post(API_TEXT, headers=headers, json=payload)
print(json.loads(response.content.decode("utf-8"))[0]['generated_text'])
        """, language="python")

# --- 6. DATA ART GENERATOR ---
elif opcion == "DataArt":
    st.markdown("<h1 class='main-header'>📊 Data Art Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Traducción de variables estadísticas a prompts de diseño abstracto</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Experiencia Creativa", "💼 Pivot de Negocios", "🔬 Fundamentos Académicos", "🐍 Código Python"])
    
    with tab1:
        st.subheader("Análisis de datos numéricos y generación de lienzo")
        uploaded_csv = st.file_uploader("Sube un CSV de ejemplo (ej. ventas corporativas):", type=["csv"])
        
        # CSV de ejemplo por defecto para evitar bloqueos
        if not uploaded_csv:
            st.info("💡 Mostrando simulación con datos financieros por defecto (Subí tu propio CSV para interactuar).")
            df = pd.DataFrame({
                'Mes': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
                'Ventas': [15000, 24000, 18000, 31000, 42000, 39000]
            })
        else:
            df = pd.read_csv(uploaded_csv)
            
        st.write("Vista previa de tus datos estructurados:")
        st.dataframe(df.head())
        
        # Selección de columna numérica para el análisis matemático
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            col_target = st.selectbox("Selecciona la columna que define el arte:", numeric_cols)
            
            # Cálculo de variables estadísticas clave
            mean_val = df[col_target].mean()
            std_val = df[col_target].std()
            max_val = df[col_target].max()
            coef_variation = (std_val / mean_val) if mean_val != 0 else 0
            
            st.write(f"📊 **Análisis Estadístico:** Promedio = {mean_val:.2f} | Desviación Estándar = {std_val:.2f} | Coeficiente de Variación = {coef_variation:.2%}")
            
            # Traducción algorítmica a prompt estético
            if coef_variation > 0.3:
                pincelada = "chaotic irregular brushstrokes, sharp high-contrast color palette, high volatility concept"
            else:
                pincelada = "smooth fluid brushstrokes, calm pastel monochromatic palette, stable geometric concept"
                
            data_prompt = f"An abstract generative digital art representing financial metrics, {pincelada}, premium design, oil painting style"
            st.info(f"🔮 **Prompt de Datos Autogenerado:** *'{data_prompt}'*")
            
            if st.button("Generar Data Art"):
                if not hf_token:
                    st.error("Token de Hugging Face requerido en la barra lateral.")
                else:
                    with st.spinner("Transformando estadísticas en vectores estéticos..."):
                        api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
                        result = query_huggingface(api_url, {"inputs": data_prompt}, hf_token)
                        if result:
                            st.image(Image.open(BytesIO(result)), caption="Data Art resultante basado en tu CSV")
                        else:
                            st.error("Fallo de red en inferencia. Reintenta.")
        else:
            st.error("El CSV subido no contiene columnas numéricas válidas para procesar.")
            
    with tab2:
        st.markdown("""
        <div class='business-card'>
            <h4>💼 Aplicación Comercial: Storytelling de Datos de Alto Impacto para Ejecutivos</h4>
            <p>Las directivas empresariales sufren fatiga visual ante reportes estáticos en blanco y negro. El <b>Data-Driven Art</b> y las visualizaciones conceptuales disruptivas se utilizan en reportes de responsabilidad social corporativa (RSC), memorias anuales o portales interactivos de inversionistas para capturar la atención y transmitir de forma emotiva la salud y el dinamismo operativo de la firma.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab3:
        st.markdown(r"""
        <div class='theory-card'>
            <h4>🔬 Mapeo de Métricas de Dispersión</h4>
            <p>El <b>Coeficiente de Variación (CV)</b>, calculado como la relación entre la desviación estándar $\sigma$ y el promedio $\mu$, es una medida de dispersión adimensional perfecta para caracterizar la volatilidad de una serie. En el pipeline de código, mapear CVs elevados a variables textuales caóticas traduce de forma matemáticamente coherente la turbulencia del negocio a la composición visual final.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab4:
        st.code("""
import pandas as pd
import requests

# 1. Cargar y Analizar CSV
df = pd.read_csv("ventas_anuales.csv")
volatilidad = df["Ventas"].std() / df["Ventas"].mean()

# 2. Mapeo Estadístico a Prompt
estilo = "chaotic sharp high-contrast" if volatilidad > 0.25 else "harmonious soft pastel"
prompt = f"Abstract expressionist painting of business success, {estilo} patterns"

# 3. Consumo de API Generativa
API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
headers = {"Authorization": "Bearer TU_HF_TOKEN"}
response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        """, language="python")

# --- 7. LA ROCKOLA DE LA IA (NUEVA) ---
elif opcion == "Rockola":
    st.markdown("<h1 class='main-header'>🎙️ La Rockola de la IA</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Procesamiento de audio digital y síntesis de voz paramétrica</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Experiencia Creativa", "💼 Pivot de Negocios", "🔬 Fundamentos Académicos", "🐍 Código Python"])
    
    with tab1:
        st.subheader("Generación de Audio y Doblaje Autogestionado")
        text_to_speak = st.text_input("Ingresa la frase que quieres sonorizar:", "Bienvenido al Instituto Data Science Argentina. El futuro de los negocios se construye con algoritmos.")
        
        if st.button("Sintetizar Audio"):
            if not hf_token:
                st.error("Token de Hugging Face requerido en la barra de navegación lateral.")
            else:
                with st.spinner("Sintetizando espectrograma y compilando ondas sonoras..."):
                    # Modelo TTS Serverless de Hugging Face de alta fidelidad
                    api_tts = "https://api-inference.huggingface.co/models/facebook/mms-tts-spa"
                    payload = {"inputs": text_to_speak}
                    audio_bytes = query_huggingface(api_tts, payload, hf_token)
                    
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/wav")
                        st.success("🎉 ¡Audio generado exitosamente! Puedes descargarlo o reproducirlo.")
                    else:
                        st.error("El endpoint de TTS está temporalmente inactivo o cargando. Por favor, reintenta en un momento.")
                        
    with tab2:
        st.markdown("""
        <div class='business-card'>
            <h4>💼 Aplicación Comercial: Sistemas IVR y Localización de Contenido</h4>
            <p>La tecnología de <b>Text-to-Speech (TTS)</b> es el pilar de los canales de telefonía inteligente y doblaje automatizado de videos promocionales. Permite a las corporaciones financieras o de retail generar locuciones de facturas y avisos personalizados sobre el saldo de cada cliente de forma instantánea, eliminando la necesidad de locutores humanos para tareas repetitivas.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab3:
        st.markdown("""
        <div class='theory-card'>
            <h4>🔬 De Texto a Señal de Audio: TTS y Vocoders</h4>
            <p>El procesamiento de audio digital se divide en dos fases críticas:
            1. **Conversión de Texto a Espectrograma de Mel:** Una representación visual de frecuencias a lo largo del tiempo.
            2. **Vocoder (ej: HiFi-GAN):** Una red neuronal que traduce ese espectrograma bidimensional a ondas acústicas continuas comprimidas en vectores binarios y empaquetadas en un contenedor <code>WAV</code>.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab4:
        st.code("""
import requests

API_TTS = "https://api-inference.huggingface.co/models/facebook/mms-tts-spa"
headers = {"Authorization": "Bearer TU_HF_TOKEN"}

payload = {
    "inputs": "Hola, estimando cliente. Su saldo pendiente es de cinco mil pesos."
}

response = requests.post(API_TTS, headers=headers, json=payload)
if response.status_code == 200:
    with open("mensaje_cliente.wav", "wb") as f:
        f.write(response.content)
    print("Audio guardado como mensaje_cliente.wav")
        """, language="python")

# --- 8. EL CURADOR INTELIGENTE (NUEVA) ---
elif opcion == "Curador":
    st.markdown("<h1 class='main-header'>🔍 El Curador Inteligente</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Motores de recomendación mediante Embeddings Multimodales (CLIP)</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Experiencia Creativa", "💼 Pivot de Negocios", "🔬 Fundamentos Académicos", "🐍 Código Python"])
    
    # Catálogo MOCK de obras de arte del IDSA con embeddings descriptivos simulados
    catalogo = [
        {"id": 1, "titulo": "Amanecer Abstracto", "estilo": "Minimalista y cálido, tonos naranjas suaves", "embedding": np.array([0.85, 0.10, 0.05])},
        {"id": 2, "titulo": "Metrópolis Digital", "estilo": "Cyberpunk frío, luces de neón azules y violetas", "embedding": np.array([0.05, 0.90, 0.05])},
        {"id": 3, "titulo": "Bosque Rústico", "estilo": "Orgánico y natural, verdes profundos e impresionista", "embedding": np.array([0.10, 0.05, 0.85])}
    ]
    
    with tab1:
        st.subheader("Buscador Semántico para Galería o Retail")
        user_query = st.text_input("Describe el diseño o atmósfera que buscas para tu ambiente:", "Quiero algo frío con colores neón para mi oficina tecnológica")
        
        if st.button("Buscar Recomendaciones"):
            with st.spinner("Procesando consulta en el espacio vectorial común..."):
                # Simulación de extracción de embeddings basada en similitud lingüística simple para asegurar el funcionamiento sin red de CLIP
                # Clasificamos la consulta semánticamente de manera rudimentaria pero explicativa
                query_low = user_query.lower()
                if "naranja" in query_low or "cálido" in query_low or "sol" in query_low or "amanecer" in query_low:
                    vec_query = np.array([0.90, 0.05, 0.05])
                elif "frío" in query_low or "neón" in query_low or "azul" in query_low or "tecnología" in query_low or "cyberpunk" in query_low:
                    vec_query = np.array([0.02, 0.95, 0.03])
                else: # Bosque / Orgánico por defecto
                    vec_query = np.array([0.08, 0.02, 0.90])
                
                # Calcular similitud coseno localmente en base al catálogo
                resultados = []
                for item in catalogo:
                    u = vec_query
                    v = item["embedding"]
                    sim = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
                    resultados.append((item["titulo"], item["estilo"], sim))
                
                # Ordenar por similitud
                resultados = sorted(resultados, key=lambda x: x[2], reverse=True)
                
                st.write("### Obras Sugeridas:")
                for r in resultados:
                    st.write(f"🖼️ **{r[0]}** - *{r[1]}* (Similitud semántica: **{r[2]:.2%}**)")
                    st.progress(float(r[2]))
                    
    with tab2:
        st.markdown("""
        <div class='business-card'>
            <h4>💼 Aplicación Comercial: Motores de Recomendación Multimodal y Visuales</h4>
            <p>Los líderes de E-Commerce (como Pinterest, Zara o Ikea) no buscan productos por texto exacto; asocian imágenes y semántica en espacios compartidos. Un cliente sube una foto de una lámpara y el sistema recomienda alfombras que comparten la misma estética de diseño. Esto es el núcleo del <b>Visual Search Shopping</b>.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab3:
        st.markdown("""
        <div class='theory-card'>
            <h4>🔬 Espacios de Similitud Vectorial y Modelo CLIP</h4>
            <p>Modelos como <b>CLIP</b> (Contrastive Language-Image Pretraining) de OpenAI alinean vectores de imágenes y de texto en una misma matriz métrica de alta dimensión. La <b>Similitud Coseno</b>, definida como la fórmula matemática de normalización del producto punto entre dos vectores, mide el coseno del ángulo formado por las dos variables: un coseno cercano a 1 denota equivalencia semántica total.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab4:
        st.code("""
import numpy as np

# Datos simulados de producto (Vectores de Embedding CLIP de 3 dimensiones)
emb_cliente = np.array([0.02, 0.95, 0.03])  # Buscó algo tecnológico/frío
emb_producto = np.array([0.05, 0.90, 0.05]) # Metrópolis neón

# Cálculo de Similitud Coseno pura en Python
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

score = cosine_similarity(emb_cliente, emb_producto)
print(f"Similitud de Recomendación: {score:.2%}")
        """, language="python")

# --- 9. EL ORÁCULO DE LA HISTORIA (NUEVA) ---
elif opcion == "Oraculo":
    st.markdown("<h1 class='main-header'>📜 El Oráculo de la Historia</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Sistemas de QA corporativos basados en Arquitecturas RAG</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Experiencia Creativa", "💼 Pivot de Negocios", "🔬 Fundamentos Académicos", "🐍 Código Python"])
    
    # Base de datos vectorial corporativa mockeada para auditar respuestas
    corpus_documental = [
        {"tema": "Stable Diffusion", "contenido": "Stable Diffusion v1.5 es un modelo latente de texto a imagen desarrollado por Runway y LMU Münich."},
        {"tema": "Hugging Face", "contenido": "El token de Hugging Face actúa como credencial HTTPS para el acceso a las APIs de inferencia del Hub de modelos."},
        {"tema": "Streamlit", "contenido": "Streamlit permite a los científicos de datos programar backends y frontends fluidos empleando únicamente Python."}
    ]
    
    with tab1:
        st.subheader("Consulta del Oráculo Tecnológico de IDSA")
        st.write("Escribe una pregunta sobre la arquitectura del framework:")
        user_query = st.text_input("Pregunta al oráculo:", "Contame sobre Stable Diffusion")
        
        if st.button("Consultar Base de Conocimiento"):
            with st.spinner("Buscando en la base documental indexada (RAG)..."):
                # Simular recuperación semántica por coincidencia de términos
                query_low = user_query.lower()
                contexto_recuperado = "No se encontraron documentos de soporte exactos."
                for doc in corpus_documental:
                    if doc["tema"].lower() in query_low:
                        contexto_recuperado = doc["contenido"]
                        break
                
                st.write("📑 **Documento de soporte recuperado de la base interna:**")
                st.info(contexto_recuperado)
                
                # LLM para reformulación semántica
                if hf_token:
                    api_llm = "https://api-inference.huggingface.co/models/meta-llama/Llama-3-8b-instruct"
                    prompt_rag = f"Context: {contexto_recuperado}\\nQuestion: {user_query}\\nAnswer in Spanish as an academic expert:"
                    
                    result = query_huggingface(api_llm, {"inputs": prompt_rag, "parameters": {"max_new_tokens": 100}}, hf_token)
                    if result:
                        try:
                            # Parsear respuesta del LLM
                            res_json = json.loads(result.decode("utf-8"))
                            output_text = res_json[0]['generated_text']
                            st.write("📜 **Respuesta formateada por el Oráculo:**")
                            st.write(output_text)
                        except Exception:
                            st.write("📜 **Respuesta de soporte directa:** " + contexto_recuperado)
                else:
                    st.warning("⚠️ Configura el token de Hugging Face en la barra lateral para ver la reformulación con Llama 3.")
                    
    with tab2:
        st.markdown("""
        <div class='business-card'>
            <h4>💼 Aplicación Comercial: Auditoría y Búsqueda de Políticas y Contratos</h4>
            <p>Los modelos de lenguaje comunes tienden a alucinar (inventar datos). En finanzas o leyes, esto es inaceptable. El enfoque de <b>Retrieval-Augmented Generation (RAG)</b> obliga al modelo de IA a responder basándose única y estrictamente en fragmentos reales de contratos o políticas corporativas previamente recuperados, garantizando veracidad técnica absoluta.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab3:
        st.markdown("""
        <div class='theory-card'>
            <h4>🔬 El Pipeline de RAG en Tres Fases</h4>
            <p>1. **Indexación:** División de un corpus documental masivo en trozos pequeños (*chunks*) y conversión de cada trozo en un vector denso.
            2. **Recuperación:** La consulta del usuario se vectoriza y se buscan por cercanía matemática (*K-Nearest Neighbors*) los trozos más similares.
            3. **Generación:** Se inyectan esos trozos como contexto estructurado en el Prompt del LLM, acotando su espectro creativo a los datos provistos.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab4:
        st.code("""
# Flujo simplificado de RAG puro en Python
documentos = [
    "La tasa de interés preferencial corporativa de IDSA es del 12% anual.",
    "Los reclamos de soporte técnico se resuelven en un plazo máximo de 24 horas."
]

pregunta_usuario = "Cual es la tasa de interes corporativa?"

# Simulación de recuperación semántica
contexto = [doc for doc in documentos if "tasa" in doc][0]

# Construcción de Prompt Seguro para el LLM corporativo
prompt_seguro = f\"\"\"
Responde la pregunta basándote estrictamente en el contexto provisto.
Contexto: {contexto}
Pregunta: {pregunta_usuario}
Respuesta:
\"\"\"
        """, language="python")

# --- 10. EL TASADOR ALGORÍTMICO (NUEVA) ---
elif opcion == "Tasador":
    st.markdown("<h1 class='main-header'>🔮 El Tasador Algorítmico</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Regresión y predicción de valores comerciales con algoritmos supervisados</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Experiencia Creativa", "💼 Pivot de Negocios", "🔬 Fundamentos Académicos", "🐍 Código Python"])
    
    with tab1:
        st.subheader("Simulación Interactiva de Modelos Predictivos")
        
        col1, col2 = st.columns(2)
        with col1:
            dim_x = st.slider("Dimensiones de la obra (Ancho en cm):", 10, 200, 80)
            reputacion = st.slider("Reputación del artista en la plataforma (1 a 100):", 1, 100, 50)
            complejidad_prompt = st.slider("Complejidad del Prompt (cantidad de tokens):", 5, 120, 30)
            
        with col2:
            # Fórmula de simulación predictiva (Regresión Lineal emulada matemáticamente con coeficientes entrenados)
            # Base = $150 + Ancho * 1.5 + Reputacion * 12.5 + tokens * 0.8
            precio_estimado = 150 + (dim_x * 1.5) + (reputacion * 12.5) + (complejidad_prompt * 0.8)
            
            st.metric(label="Valor Estimado de Mercado (USD)", value=f"${precio_estimado:,.2f}")
            
            # Graficación interactiva de la curva de valor del artista empleando Matplotlib
            fig, ax = plt.subplots(figsize=(6, 4))
            reps_range = np.linspace(1, 100, 100)
            precios_range = 150 + (dim_x * 1.5) + (reps_range * 12.5) + (complejidad_prompt * 0.8)
            ax.plot(reps_range, precios_range, color="#2563EB", label="Curva de Valoración", linewidth=2)
            ax.scatter([reputacion], [precio_estimado], color="red", s=100, zorder=5, label="Tu Obra Actual")
            ax.set_title("Efecto de la Reputación del Artista en el Precio Final")
            ax.set_xlabel("Reputación del Artista")
            ax.set_ylabel("Valor Estimado (USD)")
            ax.grid(True, linestyle="--", alpha=0.6)
            ax.legend()
            st.pyplot(fig)
            plt.close(fig) # Liberación de memoria headless
            
    with tab2:
        st.markdown("""
        <div class='business-card'>
            <h4>💼 Aplicación Comercial: Scoring Crediticio e Inteligencia de Precios Dinámicos</h4>
            <p>Los bancos, aseguradoras e inmobiliarias no adivinan precios. Recopilan cientos de variables históricas (ingresos, historial de pago, dimensiones de propiedad, año de construcción) y entrenan modelos predictivos de <b>Regresión Lineal o Random Forests</b> para automatizar la fijación de tarifas o autorizar préstamos hipotecarios en milisegundos de forma objetiva y rentable.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab3:
        st.markdown(r"""
        <div class='theory-card'>
            <h4>🔬 Modelado de Regresión Supervisado</h4>
            <p>Un modelo de regresión matemática busca encontrar la función continua:
            $$Y = \beta_0 + \beta_1 X_1 + \beta_2 X_2 + ... + \beta_n X_n + \epsilon$$
            Donde cada coeficiente $\beta_i$ determina el impacto marginal de la variable predictora $X_i$ sobre el objetivo final (precio o tasa). El entrenamiento minimiza la suma de errores cuadráticos para ajustar la recta o superficie hiper-dimensional de la forma más exacta posible a los datos reales.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab4:
        st.code("""
import pandas as pd
from sklearn.linear_model import LinearRegression

# 1. Datos de entrenamiento históricos de ventas de propiedades/arte
datos = pd.DataFrame({
    "ancho": [50, 100, 150, 80],
    "reputacion": [10, 80, 95, 40],
    "precio": [200, 1100, 1600, 600]
})

# 2. Separación de Variables Predictoras e Target
X = datos[["ancho", "reputacion"]]
y = datos["precio"]

# 3. Entrenamiento de Regresión Lineal
modelo = LinearRegression()
modelo.fit(X, y)

# 4. Predicción en Vivo de una Nueva Obra
nueva_obra = [[90, 60]] # Ancho=90, Reputacion=60
precio_predicho = modelo.predict(nueva_obra)
print(f"Precio estimado en producción: ${precio_predicho[0]:.2f}")
        """, language="python")

# ============================================================
# FOOTER ACADÉMICO UNIFICADO
# ============================================================
st.markdown("---")
st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0.9rem;'>Dirección Académica · Instituto Data Science Argentina (IDSA)<br>Entorno de Innovación Abierta y Creatividad Tecnológica con IA · © 2026</p>", unsafe_allow_html=True)
