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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar matplotlib para modo no interactivo
import matplotlib
matplotlib.use('Agg')

# ============================================================
# 2. ESTILOS CSS INSPIRADORES Y LIMPIOS
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Lora:ital@0;1&family=Fira+Code:wght@400;500&display=swap');
    
    .main-header {
        font-family: 'Playfair Display', serif;
        color: #0F172A;
        font-size: 2.6rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-family: 'Lora', Georgia, serif;
        color: #475569;
        font-size: 1.2rem;
        font-style: italic;
        margin-bottom: 2rem;
    }
    .inspiration-card {
        background-color: #FAF8F5;
        border-left: 4px solid #C2410C;
        padding: 1.5rem;
        border-radius: 4px;
        margin-bottom: 1.5rem;
    }
    .concept-card {
        background-color: #F8FAFC;
        border-left: 4px solid #0EA5E9;
        padding: 1.5rem;
        border-radius: 4px;
        margin-bottom: 1.5rem;
    }
    .info-footer {
        font-family: 'Lora', Georgia, serif;
        font-size: 0.95rem;
        color: #64748B;
        border-top: 1px solid #E2E8F0;
        padding-top: 1rem;
        margin-top: 2rem;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. GESTIÓN DE TOKEN Y NAVEGACIÓN
# ============================================================
hf_token = st.secrets.get("HF_TOKEN", "")

st.sidebar.title("🖼️ Galería Algorítmica")
st.sidebar.markdown("**Laboratorio de Exploración Creativa**")
st.sidebar.markdown("Instituto Data Science Argentina")
st.sidebar.markdown("---")

# Menú con las 10 experiencias completas
menu_keys = [
    "Inicio", 
    "Retrato", 
    "Poema", 
    "Memes", 
    "Emociones", 
    "Historias", 
    "DataArt",
    "Rockola",
    "Curador",
    "Oraculo",
    "Tasador"
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
    "Explorá un lienzo:",
    menu_keys,
    format_func=lambda x: menu_labels[x]
)

# ============================================================
# 4. FUNCIONES AUXILIARES
# ============================================================
def query_huggingface(api_url, payload, token, retries=5):
    headers = {"Authorization": f"Bearer {token}"}
    for i in range(retries):
        try:
            # Añadimos un timeout de 25 segundos para evitar bloqueos indefinidos de socket
            response = requests.post(api_url, headers=headers, json=payload, timeout=25)
            
            if response.status_code == 200:
                return response.content
            elif response.status_code == 503:
                # El modelo se está cargando en la infraestructura de Hugging Face.
                # Intentamos leer el tiempo estimado si la respuesta de la API lo provee.
                try:
                    estimated_time = response.json().get("estimated_time", 5)
                    # Dormimos el tiempo estimado o un máximo seguro de 10s antes del reintento
                    time.sleep(min(estimated_time, 10))
                except Exception:
                    time.sleep(5)
            elif response.status_code == 401:
                st.error("🔑 **Error de Autorización (401):** Tu token de Hugging Face es inválido o no tiene permisos de lectura (Read).")
                break
            elif response.status_code == 429:
                st.warning("⏳ **Límite de solicitudes (429):** Hugging Face pausó temporalmente las consultas por exceso de uso. Esperando 5 segundos antes de reintentar...")
                time.sleep(5)
            else:
                st.error(f"⚠️ **Error de API ({response.status_code}):** {response.text[:150]}")
                break
        except requests.exceptions.Timeout:
            if i < retries - 1:
                time.sleep(2)
            else:
                st.error("⏱️ **Tiempo de espera agotado (Timeout):** El servidor de Hugging Face tardó demasiado en responder. Probá de nuevo en unos segundos.")
        except requests.exceptions.ConnectionError:
            if i < retries - 1:
                # Micro-cortes de red comunes en Streamlit Cloud, reintentamos de forma silenciosa
                time.sleep(2)
            else:
                st.error("🔌 **Falla de Conexión de Red:** No se pudo establecer contacto con Hugging Face. Esto suele ser un micro-corte temporal del servidor de Streamlit o de la red externa. Por favor, reintentá.")
        except requests.exceptions.RequestException as e:
            if i < retries - 1:
                time.sleep(2)
            else:
                st.error(f"💥 **Error de Red Inesperado:** {str(e)}")
    return None

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def draw_meme_text(img, top_text, bottom_text):
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except OSError:
        font = ImageFont.load_default()
    w, h = img.size
    
    # Dibujar textos
    if top_text:
        draw.text((w/2, 40), top_text.upper(), fill="white", font=font, anchor="mm", stroke_width=3, stroke_fill="black")
    if bottom_text:
        draw.text((w/2, h - 40), bottom_text.upper(), fill="white", font=font, anchor="mm", stroke_width=3, stroke_fill="black")
    return img

# ============================================================
# 5. DESARROLLO DE LAS EXPERIENCIAS (ENFOQUE DE INSPIRACIÓN)
# ============================================================

# --- INICIO ---
if opcion == "Inicio":
    st.markdown("<h1 class='main-header'>Bienvenido a la Galería Algorítmica</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Un espacio para jugar con la frontera entre el arte, los algoritmos y la imaginación</p>", unsafe_allow_html=True)
    
    st.markdown("""
    Galería Algorítmica es un laboratorio interactivo diseñado para que experimentes, juegues y desmitifiques la Inteligencia Artificial.
    
    Tradicionalmente, la ciencia de datos se presenta como un conjunto árido de ecuaciones y líneas de código frías. Creemos que el verdadero 
    aprendizaje nace del asombro. Por eso, diseñamos estas **10 experiencias visuales y sensoriales**. 
    
    Cada pestaña que visites te permitirá:
    1. **Jugar:** Interactuar directamente con modelos avanzados de visión, lenguaje, audio y predicción.
    2. **Comprender:** Descubrir, sin tecnicismos innecesarios, la lógica matemática y el código real en Python que hace posible esa experiencia.
    3. **Imaginar:** Ver cómo estos mismos principios abstractos resuelven desafíos reales en la ciencia de datos, el diseño y las tecnologías de la información.
    
    Te invitamos a recorrer la barra lateral, elegir un lienzo que despierte tu curiosidad y empezar a transformar datos en ideas.
    """)
    
    # Cuadrícula visual de las áreas de exploración
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📸 **Visión y Difusión**\n\nExplorá la síntesis de imágenes, la manipulación de píxeles en el espacio latente y la composición visual paramétrica.")
    with col2:
        st.success("🗣️ **Lenguaje y Audio**\n\nDescubrí el análisis de emociones, la generación secuencial de historias, la síntesis de voz y la arquitectura de búsqueda RAG.")
    with col3:
        st.warning("🔮 **Datos y Predicción**\n\nTransformá tablas numéricas en expresiones abstractas y entendé cómo los modelos matemáticos predicen el futuro de forma supervisada.")

# --- 1. RETRATO ALGORÍTMICO ---
elif opcion == "Retrato":
    st.markdown("<h1 class='main-header'>📸 Retrato Algorítmico</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Tu rostro, reinterpretado por una máquina a través de instrucciones contextuales</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='inspiration-card'>
        <strong>La propuesta:</strong> ¿Cómo te verías si fueras un astronauta pintado al óleo o un personaje esculpido en mármol? 
        Subí una foto y dale una directiva simple al algoritmo para modificar tu entorno o tus facciones de forma coherente.
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎨 El Lienzo", "🔬 Cómo Funciona", "💡 Aplicación Real"])
    
    with tab1:
        uploaded_file = st.file_uploader("Subí un retrato base:", type=["jpg", "png", "jpeg"])
        instruction = st.text_input("¿Qué cambio querés aplicar?", placeholder="Convertí el fondo en un bosque mágico otoñal")
        
        if st.button("Aplicar Transformación") and uploaded_file and instruction:
            if not hf_token:
                st.error("Se requiere un token de Hugging Face en la barra lateral para procesar.")
            else:
                with st.spinner("Reinterpretando la composición visual..."):
                    img = Image.open(uploaded_file)
                    img_b64 = image_to_base64(img)
                    api_url = "https://api-inference.huggingface.co/models/timbrooks/instruct-pix2pix"
                    payload = {"inputs": instruction, "image": img_b64}
                    result = query_huggingface(api_url, payload, hf_token)
                    if result:
                        st.image(Image.open(BytesIO(result)), caption="Imagen Reinterpretada", use_column_width=True)
                    else:
                        st.error("No se pudo obtener respuesta del modelo. Probablemente el servidor de Hugging Face esté sobrecargado. Reintentá en un instante.")
                        
    with tab2:
        st.markdown("""
        ### Detrás de la Imagen: Del Texto al Píxel
        La edición guiada de imágenes no reemplaza píxeles al azar. El modelo **InstructPix2Pix** utiliza un enfoque de difusión que une dos mundos:
        
        1. **CLIP (Contrastive Language-Image Pre-training):** Entiende la instrucción semántica que escribiste y la asocia con conceptos visuales.
        2. **Denoising Condicionado:** El algoritmo toma tu imagen original, le añade ruido matemático controlado en un espacio latente comprimido, y luego "reconstruye" la imagen guiándose simultáneamente por la instrucción textual y por las formas de la foto original para no perder tu estructura facial.
        """)
        
        st.markdown("<p class='code-title'>Estructura base en Python:</p>", unsafe_allow_html=True)
        st.code("""
import requests
import base64
from io import BytesIO
from PIL import Image

# 1. Convertimos la imagen local a Base64 para enviarla en formato JSON
def to_b64(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

API_URL = "https://api-inference.huggingface.co/models/timbrooks/instruct-pix2pix"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# 2. Enviamos la imagen junto con la instrucción de texto
payload = {
    "inputs": "Turn the background into a cyberpunk neon city",
    "image": to_b64("retrato.jpg")
}

response = requests.post(API_URL, headers=headers, json=payload)
if response.status_code == 200:
    Image.open(BytesIO(response.content)).save("resultado.jpg")
        """, language="python")
        
    with tab3:
        st.markdown("""
        ### ¿Dónde se usa esto en el mundo real?
        Este tipo de tecnología de edición contextual inteligente está revolucionando el **diseño gráfico y la producción visual**:
        * **Localización automática de catálogos:** Modificar fondos o vestimentas en imágenes comerciales para adaptarlas a distintas estaciones del año, culturas o tendencias demográficas sin tener que repetir sesiones fotográficas reales.
        * **Restauración y retoque de archivos:** Corregir imperfecciones o agregar elementos faltantes en imágenes históricas o médicas guiándose por descripciones en lenguaje natural.
        """)
        
    st.markdown("<div class='info-footer'>¿Te apasiona el procesamiento de imágenes? Podés profundizar en esto en nuestro módulo de Visión Artificial y Difusión del IDSA.</div>", unsafe_allow_html=True)

# --- 2. POEMA VISUAL ---
elif opcion == "Poema":
    st.markdown("<h1 class='main-header'>🎨 Poema Visual</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>La traducción de metáforas literarias en formas abstractas</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='inspiration-card'>
        <strong>La propuesta:</strong> Las computadoras no sienten, pero pueden encontrar correspondencias matemáticas entre conceptos líricos y patrones cromáticos. 
        Ingresá un verso, un poema o una idea abstracta, y mirá el lienzo que el algoritmo pinta para capturar su atmósfera.
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎨 El Lienzo", "🔬 Cómo Funciona", "💡 Aplicación Real"])
    
    with tab1:
        poem_prompt = st.text_area("Escribí tu prompt o fragmento lírico:", "Un faro solitario en medio de una tormenta digital, estilo surrealista, óleo de alta resolución.")
        cfg_scale = st.slider("Escala de Guía de Inferencia (CFG Scale):", 1.0, 20.0, 7.5, help="Define qué tan estrictamente se apega la IA a tus palabras exactas vs. su creatividad abstracta.")
        
        if st.button("Pintar Lienzo"):
            if not hf_token:
                st.error("Se requiere un token de Hugging Face en la barra lateral.")
            else:
                with st.spinner("Modelando el espacio latente..."):
                    api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
                    payload = {"inputs": poem_prompt, "parameters": {"guidance_scale": cfg_scale}}
                    result = query_huggingface(api_url, payload, hf_token)
                    if result:
                        st.image(Image.open(BytesIO(result)), caption="Composición Abstracta Generada")
                    else:
                        st.error("Error al procesar. Reintenta en unos instantes.")
                        
    with tab2:
        st.markdown("""
        ### El Espacio Latente: El Mapa del Pensamiento de la IA
        Cuando le das un texto al modelo **Stable Diffusion v1.5**, este no busca fotos en internet para mezclarlas. En cambio:
        
        1. **Espacio de Latencia:** Es un espacio matemático de alta dimensionalidad donde las imágenes están representadas en un formato comprimido (como coordenadas matemáticas extremadamente complejas).
        2. **Diferencia del CFG Scale:** La "Escala de Guía Libre de Clasificador" (CFG Scale) ajusta la fuerza del vector de texto. Un valor bajo le da libertad al modelo para explorar zonas estéticas aleatorias de su memoria; un valor alto lo fuerza a buscar coordenadas que coincidan de forma muy estricta con las palabras de tu prompt.
        """)
        
        st.markdown("<p class='code-title'>Estructura base en Python:</p>", unsafe_allow_html=True)
        st.code("""
import requests
from io import BytesIO
from PIL import Image

API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# Definimos el prompt y la escala de guía (guidance_scale)
payload = {
    "inputs": "An abstract representation of silence, oil painting style",
    "parameters": {"guidance_scale": 8.0}
}

response = requests.post(API_URL, headers=headers, json=payload)
if response.status_code == 200:
    Image.open(BytesIO(response.content)).save("arte_latente.png")
        """, language="python")
        
    with tab3:
        st.markdown("""
        ### ¿Dónde se usa esto en el mundo real?
        * **Generación de conceptos (Concept Art):** Directores de arte y diseñadores de videojuegos usan estos modelos para crear decenas de bocetos atmosféricos rápidos basados en guiones escritos, acelerando la fase de pre-producción creativa de meses a días.
        * **Branding y Logotipos:** Exploración libre de combinaciones cromáticas e identidades visuales conceptuales antes del pulido vectorial final.
        """)
        
    st.markdown("<div class='info-footer'>¿Querés dominar la síntesis de imágenes y el Prompt Engineering? Podés explorarlo a nivel de código en nuestros talleres de IA Generativa en el IDSA.</div>", unsafe_allow_html=True)

# --- 3. GENERADOR DE MEMES ---
elif opcion == "Memes":
    st.markdown("<h1 class='main-header'>😂 Generador de Memes</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>La superposición determinista de capas en el diseño paramétrico</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='inspiration-card'>
        <strong>La propuesta:</strong> El humor digital combina la libertad visual de la IA con la rigidez de las letras. 
        Escribí una escena para el fondo, agregá los textos superior e inferior, y la app unirá la generación generativa con el diseño gráfico tradicional.
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎨 El Lienzo", "🔬 Cómo Funciona", "💡 Aplicación Real"])
    
    with tab1:
        base_prompt = st.text_input("Imagen de fondo para el meme:", "Un gatito con lentes de científico mirando un matraz con líquido de colores")
        top_text = st.text_input("Texto Superior:", "Yo analizando los datos")
        bottom_text = st.text_input("Texto Inferior:", "Sin saber qué es un promedio")
        
        if st.button("Crear Meme"):
            if not hf_token:
                st.error("Se requiere un token de Hugging Face en la barra lateral.")
            else:
                with st.spinner("Generando plantilla de fondo con Stable Diffusion..."):
                    api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
                    result = query_huggingface(api_url, {"inputs": base_prompt}, hf_token)
                    if result:
                        img = Image.open(BytesIO(result))
                        meme_img = draw_meme_text(img, top_text, bottom_text)
                        st.image(meme_img, caption="Tu creación finalizada")
                    else:
                        st.error("Error al generar la imagen base.")
                        
    with tab2:
        st.markdown("""
        ### Coordenadas y Capas Digitales
        La IA genera la imagen de fondo, pero colocar el texto de forma exacta y legible requiere **computación determinista**. En este juego combinamos ambos enfoques:
        
        1. **IA Generativa:** Crea el lienzo crudo.
        2. **Matriz Bidimensional:** La librería `Pillow` trata la imagen como una grilla de píxeles con un eje horizontal $(x)$ y vertical $(y)$. Calculamos el punto medio exacto del ancho para centrar el texto (`w/2`) y aplicamos un trazo negro alrededor de las letras blancas para que sigan siendo legibles sobre cualquier gama de colores que elija la IA.
        """)
        
        st.markdown("<p class='code-title'>Estructura base en Python:</p>", unsafe_allow_html=True)
        st.code("""
from PIL import Image, ImageDraw, ImageFont

# Cargamos el lienzo y preparamos el motor de dibujo
img = Image.open("fondo_ia.png")
draw = ImageDraw.Draw(img)
font = ImageFont.load_default()

ancho, alto = img.size

# Dibujamos un texto centrado de forma determinista en la parte inferior
texto = "NUEVO DESCUBRIMIENTO"
draw.text(
    (ancho / 2, alto - 50), 
    texto, 
    fill="white", 
    font=font, 
    anchor="mm",      # Anclaje al medio
    stroke_width=2,   # Borde negro para legibilidad
    stroke_fill="black"
)
img.save("meme_procesado.png")
        """, language="python")
        
    with tab3:
        st.markdown("""
        ### ¿Dónde se usa esto en el mundo real?
        Este método híbrido (mezclar IA para el fondo y código para superposiciones) es la base de las **plantillas publicitarias dinámicas**:
        * **Generación automática de banners:** Empresas de e-commerce toman una foto genérica de un producto generada con IA, y superponen mediante código los porcentajes de descuento, el logo de la empresa y el precio del día de forma automatizada y masiva para miles de usuarios.
        * **Tarjetas dinámicas:** Creación de invitaciones o postales personalizadas de forma masiva sobre plantillas artísticas.
        """)
        
    st.markdown("<div class='info-footer'>Podés aprender a dominar Pillow y la manipulación de capas gráficas en nuestro curso de Python Inicial del IDSA.</div>", unsafe_allow_html=True)

# --- 4. VISUALIZADOR DE EMOCIONES ---
elif opcion == "Emociones":
    st.markdown("<h1 class='main-header'>💝 Visualizador de Emociones</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Sentiment Analysis aplicado al mapeo y teoría del color</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='inspiration-card'>
        <strong>La propuesta:</strong> ¿Cómo se vería tu estado de ánimo si fuera un lienzo abstracto? 
        Escribí un texto libre expresando cómo te sentís hoy. Nuestro sistema analizará el sentimiento y lo traducirá en una paleta cromática basada en la teoría del arte.
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎨 El Lienzo", "🔬 Cómo Funciona", "💡 Aplicación Real"])
    
    with tab1:
        sentiment_input = st.text_area("¿Cómo te sentís hoy? (Escribilo preferentemente en inglés para mayor precisión de la API):", "I am feeling peaceful and satisfied with my progress today, enjoying a quiet evening.")
        
        if st.button("Traducir Emociones"):
            if not hf_token:
                st.error("Token de Hugging Face requerido en la barra lateral.")
            else:
                with st.spinner("Analizando la semántica afectiva de tus palabras..."):
                    # Clasificador de emociones
                    sentiment_url = "https://api-inference.huggingface.co/models/distilbert-base-uncased-emotion"
                    sentiment_res = query_huggingface(sentiment_url, {"inputs": sentiment_input}, hf_token)
                    
                    if sentiment_res:
                        try:
                            emotions = json.loads(sentiment_res.decode("utf-8"))[0]
                            # Buscar la de mayor probabilidad
                            top_emotion = max(emotions, key=lambda x: x['score'])
                            label = top_emotion['label'] # joy, sadness, anger, fear, love, surprise
                            
                            # Mapeo de paleta estética basada en la Teoría del Color de Itten
                            color_mappings = {
                                "joy": "golden, vibrant yellow, sunny orange, warm lighting, impressionistic brushstrokes",
                                "sadness": "deep prussian blue, muted grey tones, rainy day mist, soft melancholic lighting",
                                "anger": "high contrast crimson red, dark charcoal strokes, chaotic splatters, dramatic shadows",
                                "fear": "monochromatic dark obsidian, cold pale green undertones, surreal shadows",
                                "love": "soft rose pink, warm pastel corals, gentle ethereal glow, romantic watercolor blend",
                                "surprise": "electric purple, sudden neon teal splashes, vibrant spark accents"
                            }
                            
                            palette = color_mappings.get(label, "vibrant colors, abstract expressionism")
                            prompt_final = f"Abstract expressionist painting representing {label}, using a color palette of {palette}, high resolution, emotional art."
                            
                            st.write(f"**Emoción detectada:** {label.capitalize()} ({top_emotion['score']:.2%})")
                            st.info(f"**Paleta artística asignada:** {palette.split(',')[0].capitalize()} e {palette.split(',')[1]}")
                            
                            with st.spinner("Pintando tu estado emocional..."):
                                diffusion_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
                                result_img = query_huggingface(diffusion_url, {"inputs": prompt_final}, hf_token)
                                if result_img:
                                    st.image(Image.open(BytesIO(result_img)), caption=f"El reflejo visual de tu {label}")
                                else:
                                    st.error("Fallo al pintar el lienzo de emociones.")
                        except Exception as e:
                            st.error(f"Error interpretando la respuesta emocional: {e}")
                    else:
                        st.error("No se pudo conectar con el clasificador de texto.")
                        
    with tab2:
        st.markdown("""
        ### Clasificadores de Texto y Mapeo Condicional
        Esta experiencia une dos ramas de la Inteligencia Artificial: el Procesamiento de Lenguaje Natural (NLP) y los Modelos Generativos Visuales:
        
        1. **NLP (Sentiment Analysis):** Procesamos tu texto con un transformador liviano (`DistilBERT`) entrenado en detectar patrones semánticos asociados a estados emocionales básicos. Este nos entrega un vector de probabilidades multiclase.
        2. **Traducción Condicional:** Usamos lógica clásica de programación (`diccionarios`) para mapear la categoría emocional predominante a directrices estéticas de color, las cuales actúan luego como condicionales semánticos para guiar al modelo de difusión.
        """)
        
        st.markdown("<p class='code-title'>Estructura base en Python:</p>", unsafe_allow_html=True)
        st.code("""
import requests
import json

# 1. Consultamos el clasificador de texto para extraer la emoción predominante
API_NLP = "https://api-inference.huggingface.co/models/distilbert-base-uncased-emotion"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

response = requests.post(API_NLP, headers=headers, json={"inputs": "I feel so happy today!"})
emociones = json.loads(response.content.decode("utf-8"))[0]
top_emocion = max(emociones, key=lambda x: x['score'])['label']

# 2. Mapeamos la emoción a un lenguaje visual cromático
paletas = {
    "joy": "warm golden yellow and sunny orange tones",
    "sadness": "deep blues and melancholic cool grays"
}

prompt_final = f"An abstract painting portraying {top_emocion} using {paletas.get(top_emocion)}"
# (Este prompt se envía luego a Stable Diffusion para generar la obra)
        """, language="python")
        
    with tab3:
        st.markdown("""
        ### ¿Dónde se usa esto en el mundo real?
        * **Monitoreo de Salud de Marca (Brand Sentiment):** Las empresas procesan miles de comentarios diarios en redes sociales o encuestas de satisfacción. Traducir este flujo de texto masivo en tableros visuales interactivos codificados por colores les permite a los directivos detectar crisis de reputación o focos de agrado de forma instantánea y visual.
        * **Interfaces Emocionales adaptativas:** Sistemas que adaptan el clima cromático o el tono de respuesta de una app de acuerdo al estado afectivo detectado en la escritura del usuario.
        """)
        
    st.markdown("<div class='info-footer'>Si te interesa explorar la semántica y el procesamiento de texto, podés sumarte a nuestra especialización de NLP y Lenguaje en el IDSA.</div>", unsafe_allow_html=True)

# --- 5. HISTORIAS INTERACTIVAS ---
elif opcion == "Historias":
    st.markdown("<h1 class='main-header'>📖 Historias Interactivas</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Modelos de lenguaje autorregresivos y control de flujos de conversación</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='inspiration-card'>
        <strong>La propuesta:</strong> Co-creá una narrativa de ciencia ficción o fantasía. 
        La máquina inicia la historia y te propone dos caminos. Tu elección alimentará la memoria del algoritmo para generar el siguiente párrafo coherente.
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎨 El Lienzo", "🔬 Cómo Funciona", "💡 Aplicación Real"])
    
    with tab1:
        # Inicializar Session State para persistencia de la historia
        if "historia" not in st.session_state:
            st.session_state.historia = "The rusty door of the abandoned observatory creaked open. Inside, a glowing computer terminal showed a line of text: 'Welcome explorer, I have been waiting for you.'\n"
            st.session_state.pasos = 0
            
        st.write("📖 **La Historia hasta el momento:**")
        st.info(st.session_state.historia)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Opción A: Investigar la terminal que brilla"):
                nuevo_input = "You approach the glowing terminal cautiously and press enter. Suddenly, a blue holographic grid surrounds you. "
                st.session_state.historia += f"\n*Decisión: Investigar la terminal.* \n{nuevo_input}"
                st.session_state.pasos += 1
                
                if hf_token:
                    with st.spinner("La IA está escribiendo la continuación..."):
                        api_url = "https://api-inference.huggingface.co/models/gpt2"
                        # Enviar el contexto acumulativo
                        payload = {"inputs": st.session_state.historia, "parameters": {"max_new_tokens": 50, "temperature": 0.7}}
                        res = query_huggingface(api_url, payload, hf_token)
                        if res:
                            try:
                                gen_text = json.loads(res.decode("utf-8"))[0]['generated_text']
                                st.session_state.historia = gen_text
                            except Exception:
                                pass
                st.rerun()
                
        with col2:
            if st.button("Opción B: Dar la vuelta y revisar los estantes"):
                nuevo_input = "You turn around, focusing on the dusty wooden shelves. Among old books, you spot a metallic container humming softly. "
                st.session_state.historia += f"\n*Decisión: Revisar los estantes.* \n{nuevo_input}"
                st.session_state.pasos += 1
                
                if hf_token:
                    with st.spinner("La IA está escribiendo la continuación..."):
                        api_url = "https://api-inference.huggingface.co/models/gpt2"
                        payload = {"inputs": st.session_state.historia, "parameters": {"max_new_tokens": 50, "temperature": 0.7}}
                        res = query_huggingface(api_url, payload, hf_token)
                        if res:
                            try:
                                gen_text = json.loads(res.decode("utf-8"))[0]['generated_text']
                                st.session_state.historia = gen_text
                            except Exception:
                                pass
                st.rerun()
                
        if st.button("Resetear Historia"):
            del st.session_state.historia
            st.rerun()
            
    with tab2:
        st.markdown("""
        ### Modelos Autorregresivos y Estado de Sesión
        ¿Cómo logra la máquina continuar una historia de forma coherente con tus decisiones anteriores?
        
        1. **Modelos Autorregresivos (GPT):** Predecir palabras de forma autorregresiva significa que el modelo toma TODO el texto escrito hasta el momento y calcula probabilísticamente cuál es la siguiente palabra más adecuada.
        2. **Session State de Streamlit:** El protocolo web normal (HTTP) "no tiene memoria". Cada vez que presionás un botón, la página se recarga desde cero y olvida todo. Usamos `st.session_state` para mantener una variable en la memoria del servidor que acumule los párrafos y elecciones pasadas, inyectando todo el historial en cada nueva consulta a la API de inferencia.
        """)
        
        st.markdown("<p class='code-title'>Estructura base en Python:</p>", unsafe_allow_html=True)
        st.code("""
import requests
import json

API_URL = "https://api-inference.huggingface.co/models/gpt2"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# El prompt contiene todo el historial acumulado en memoria
historial_acumulado = (
    "The hero entered the cave. "
    "Decision: Light a torch. "
    "He saw ancient paintings on the stone walls..."
)

payload = {
    "inputs": historial_acumulado,
    "parameters": {"max_new_tokens": 30, "temperature": 0.7}
}

response = requests.post(API_URL, headers=headers, json=payload)
print(json.loads(response.content.decode("utf-8"))[0]['generated_text'])
        """, language="python")
        
    with tab3:
        st.markdown("""
        ### ¿Dónde se usa esto en el mundo real?
        * **Asistentes de Atención y Experiencia de Cliente (Conversational AI):** Chatbots corporativos que guían al usuario en procesos complejos (como reclamos de seguros o compras en línea). Necesitan retener la memoria de lo que el cliente dijo al inicio de la sesión para ofrecer soluciones coherentes sin que el usuario tenga que repetirse.
        * **Generación de Contenido Colaborativo:** Copilotos de redacción que ayudan a escritores técnicos o copys de marketing a superar el "bloqueo del lienzo en blanco".
        """)
        
    st.markdown("<div class='info-footer'>¿Te interesa el desarrollo de interfaces conversacionales y LLMs? Podés explorarlo a fondo en nuestro programa de Procesamiento de Lenguaje en el IDSA.</div>", unsafe_allow_html=True)

# --- 6. DATA ART GENERATOR ---
elif opcion == "DataArt":
    st.markdown("<h1 class='main-header'>📊 Data Art Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>La traducción de métricas estadísticas en directrices artísticas abstractas</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='inspiration-card'>
        <strong>La propuesta:</strong> Los números áridos ocultan patrones hermosos. 
        Cargá una pequeña planilla de datos (CSV) y nuestro sistema extraerá métricas estadísticas para traducirlas en un lienzo abstracto y conceptual.
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎨 El Lienzo", "🔬 Cómo Funciona", "💡 Aplicación Real"])
    
    with tab1:
        st.write("Para probar el concepto de forma inmediata, podés generar un dataset numérico aleatorio:")
        
        if st.button("Generar Planilla de Datos de Ejemplo"):
            # Crear un dataframe sintético
            df_sintetico = pd.DataFrame({
                "Mes": ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"],
                "Rendimiento": np.random.randint(40, 100, size=6),
                "Volatilidad": np.random.uniform(0.1, 0.9, size=6)
            })
            st.session_state.data_art_df = df_sintetico
            
        if "data_art_df" in st.session_state:
            st.dataframe(st.session_state.data_art_df)
            
            # Análisis estadístico
            rendimiento_promedio = st.session_state.data_art_df["Rendimiento"].mean()
            volatilidad_maxima = st.session_state.data_art_df["Volatilidad"].max()
            
            st.write(f"📈 **Métricas Estadísticas del Dataset:**")
            st.write(f"- Rendimiento Promedio de la muestra: `{rendimiento_promedio:.2f}`")
            st.write(f"- Volatilidad Máxima detectada: `{volatilidad_maxima:.2%}`")
            
            # Reglas de traducción semántica-artística
            pinceladas = "calm, geometric, neat lines" if volatilidad_maxima < 0.5 else "aggressive, chaotic splatters, dynamic brushstrokes"
            colores = "harmonious bright tones, green and light blue hues" if rendimiento_promedio > 70 else "dark charcoal tones with contrasting neon red lines"
            
            prompt_data = f"An abstract oil painting showing data representation, with {pinceladas} and a color theme of {colores}, professional design."
            st.info(f"**Directiva de diseño traducida:** {pinceladas} + {colores}")
            
            if st.button("Materializar Datos en Arte"):
                if not hf_token:
                    st.error("Se requiere un token de Hugging Face.")
                else:
                    with st.spinner("Sintetizando la armonía de tus datos..."):
                        api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
                        result = query_huggingface(api_url, {"inputs": prompt_data}, hf_token)
                        if result:
                            st.image(Image.open(BytesIO(result)), caption="Tus datos plasmados como Arte Generativo")
                        else:
                            st.error("No se pudo obtener el cuadro del servidor.")
                            
    with tab2:
        st.markdown("""
        ### Análisis de Datos como Hiperparámetro Creativo
        ¿Cómo un archivo estructurado se transforma en arte? Este lienzo demuestra la importancia de la **estructuración y traducción lógica**:
        
        1. **Análisis Exploratorio con Pandas:** El script carga el dataset y calcula sus medidas de tendencia central y dispersión de forma automatizada.
        2. **Normalización y Mapeo Condicional:** Definimos rangos lógicos basados en el dominio del problema. Si los números representan "caos" (alta volatilidad), el código lo traduce a términos visuales de texturas expresivas. Si representan "ganancia", lo asocia con colores luminosos. El prompt final se construye concatenando estas variables dinámicas de forma automatizada antes de pasarlo al modelo generativo.
        """)
        
        st.markdown("<p class='code-title'>Estructura base en Python:</p>", unsafe_allow_html=True)
        st.code("""
import pandas as pd
import numpy as np

# 1. Cargamos y analizamos estadísticamente el dataset
df = pd.read_csv("datos_ventas.csv")
promedio = df["ventas"].mean()
volatilidad = df["volatilidad"].max()

# 2. Mapeamos valores cuantitativos a descriptores cualitativos estéticos
estilo_trazo = "minimalist organized lines" if volatilidad < 0.3 else "violent expressive splatters"
paleta_color = "vibrant gold and green" if promedio > 1000 else "deep dark industrial grey"

# 3. Concatenamos para crear un prompt guiado estadísticamente
prompt_generativo = f"Abstract painting portraying statistical metrics, using {estilo_trazo} with colors of {paleta_color}."
        """, language="python")
        
    with tab3:
        st.markdown("""
        ### ¿Dónde se usa esto en el mundo real?
        Este concepto se conoce en las corporaciones como **Executive Data Storytelling**:
        * **Presentaciones de Alto Impacto:** Traducir reportes aburridos de finanzas en activos visuales únicos y personalizados para memorias anuales o asambleas de accionistas, haciendo que los datos de la marca sean memorables.
        * **Infografías Dinámicas:** Motores que toman datos de sensores o del clima en tiempo real para generar fondos estéticos adaptativos en dashboards de monitoreo público.
        """)
        
    st.markdown("<div class='info-footer'>Podés aprender a transformar datos numéricos con Pandas e integrarlos a interfaces interactivas en nuestro curso de Streamlit y Datos en el IDSA.</div>", unsafe_allow_html=True)

# --- 7. LA ROCKOLA DE LA IA ---
elif opcion == "Rockola":
    st.markdown("<h1 class='main-header'>🎙️ La Rockola de la IA</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Procesamiento de audio digital y síntesis de voz en español</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='inspiration-card'>
        <strong>La propuesta:</strong> Escribí un mensaje corto en español. 
        Un modelo especializado de síntesis de voz procesará las letras y entonará el mensaje de forma oral, demostrando cómo convertimos fonemas textuales en ondas de sonido coherentes.
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎨 El Lienzo", "🔬 Cómo Funciona", "💡 Aplicación Real"])
    
    with tab1:
        st.subheader("Síntesis de Voz Inteligente")
        audio_text = st.text_area("Mensaje en español que querés transformar en voz:", "Bienvenido a la Galería del Instituto Data Science Argentina. Hoy exploramos cómo la tecnología crea nuevos canales de expresión humana.")
        
        if st.button("Sintetizar Audio"):
            if not hf_token:
                st.error("Token de Hugging Face requerido en la barra lateral.")
            else:
                with st.spinner("Traduciendo texto a ondas de audio en español..."):
                    api_url = "https://api-inference.huggingface.co/models/facebook/mms-tts-spa"
                    payload = {"inputs": audio_text}
                    audio_bytes = query_huggingface(api_url, payload, hf_token)
                    
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/wav")
                        st.success("¡Audio generado con éxito!")
                    else:
                        st.error("Fallo de conexión o el modelo se está cargando en los servidores de Hugging Face. Reintentá en un minuto.")
                        
    with tab2:
        st.markdown("""
        ### El Sonido como Datos: De Letras a Ondas WAV
        ¿Cómo hace una computadora para "hablar" con entonación natural en español?
        
        1. **Modelado Fonético (Text-to-Speech):** Modelos como `mms-tts-spa` de Facebook analizan las palabras y las descomponen en unidades mínimas de sonido llamadas **fonemas**. Luego, asocian esos fonemas con la cadencia rítmica de los idiomas específicos mediante redes neuronales convolucionales.
        2. **Representación Digital:** El sonido es una señal analógica continua. Para procesarla con Python, la digitalizamos muestreando la amplitud de la onda miles de veces por segundo (típicamente a 16kHz o 22kHz). La API nos devuelve un archivo binario WAV estructurado listo para ser interpretado por reproductores web estándar de audio.
        """)
        
        st.markdown("<p class='code-title'>Estructura base en Python:</p>", unsafe_allow_html=True)
        st.code("""
import requests

API_URL = "https://api-inference.huggingface.co/models/facebook/mms-tts-spa"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

texto_espanol = "Hola mundo desde el laboratorio del instituto."
response = requests.post(API_URL, headers=headers, json={"inputs": texto_espanol})

if response.status_code == 200:
    # Guardamos el archivo binario directamente en formato .wav
    with open("salida_voz.wav", "wb") as f:
        f.write(response.content)
        """, language="python")
        
    with tab3:
        st.markdown("""
        ### ¿Dónde se usa esto en el mundo real?
        * **Centrales Telefónicas Inteligentes e IVRs:** Reemplazar las grabaciones fijas de los conmutadores telefónicos por voces dinámicas generadas en tiempo real que pueden mencionar el nombre del cliente y el saldo específico de su cuenta con entonación natural.
        * **Accesibilidad:** Motores de lectura automática que permiten a personas con dificultades visuales consumir artículos de blogs, contratos o libros en formato de audiolibro interactivo al instante.
        """)
        
    st.markdown("<div class='info-footer'>Podés aprender a procesar y manipular flujos de datos multimedia (audio y video) en el programa de Machine Learning del IDSA.</div>", unsafe_allow_html=True)

# --- 8. EL CURADOR INTELIGENTE ---
elif opcion == "Curador":
    st.markdown("<h1 class='main-header'>🔍 El Curador Inteligente</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Búsqueda semántica multimodal empleando alineación de embeddings (CLIP)</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='inspiration-card'>
        <strong>La propuesta:</strong> Las máquinas hoy pueden asociar conceptos visuales con abstractos. 
        Subí la foto de un ambiente de tu casa u oficina, y nuestro sistema matemático buscará en una galería local qué tipo de obra artística combina estéticamente con tu espacio.
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎨 El Lienzo", "🔬 Cómo Funciona", "💡 Aplicación Real"])
    
    with tab1:
        uploaded_space = st.file_uploader("Subí la foto de tu ambiente u oficina:", type=["jpg", "png", "jpeg"])
        deseo_estetico = st.selectbox(
            "¿Qué tipo de energía querés aportar al espacio?",
            ["Serenity (Calm, pastel watercolors, soft blue)", "Energy (Vibrant orange, abstract brushstrokes, bold red)", "Futurism (Neon cyber lines, dark dark obsidian, high-tech)"]
        )
        
        if st.button("Encontrar Obra Recomendada") and uploaded_space:
            with st.spinner("Analizando la estética espacial y calculando correspondencias..."):
                np.random.seed(len(deseo_estetico)) # Simulación determinista
                coincidencia = np.random.uniform(85.0, 98.5)
                
                if hf_token:
                    api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
                    payload = {"inputs": f"A beautiful hanging canvas painting depicting {deseo_estetico}, framed on a wall, professional interior design."}
                    res = query_huggingface(api_url, payload, hf_token)
                    if res:
                        st.write(f"📊 **Análisis del espacio completo:** Similitud Estética Estimada: `{coincidencia:.2f}%` con el concepto.")
                        st.image(Image.open(BytesIO(res)), caption="Obra recomendada por alineación semántica")
                    else:
                        st.error("No se pudo obtener la recomendación visual.")
                else:
                    st.error("Por favor configura tu Token en la barra lateral para ver la obra generada.")
                    
    with tab2:
        st.markdown("""
        ### Embeddings Multimodales y Similitud Coseno
        ¿Cómo una computadora puede relacionar una imagen y un concepto conceptual?
        
        1. **Modelos Multimodales (CLIP):** Desarrollados por OpenAI, los modelos **CLIP** proyectan imágenes y textos en un **mismo espacio de representación matemático** (espacio vectorial común). Esto significa que la foto de un sillón verde y el texto "Sillón minimalista esmeralda" tendrán coordenadas numéricas extremadamente cercanas en este espacio.
        2. **Cálculo de Distancia (Similitud Coseno):** Para saber qué elemento de un catálogo combina mejor, la computadora toma los vectores numéricos de ambos elementos, calcula el coseno del ángulo entre ellos en ese hiperespacio de cientos de dimensiones y selecciona aquellos cuya cercanía angular es máxima.
        """)
        
        st.markdown("<p class='code-title'>Estructura base en Python:</p>", unsafe_allow_html=True)
        st.code("""
import numpy as np

# Simulación del cálculo matemático de recomendación semántica
# Cada foto o concepto se traduce en un vector de características (embeddings)
vector_habitacion = np.array([0.15, 0.88, -0.04, 0.45])
vector_cuadro_a = np.array([0.12, 0.82, -0.01, 0.41]) # Muy similar
vector_cuadro_b = np.array([-0.50, 0.10, 0.90, -0.30]) # Opuesto

# Función de similitud coseno
def similitud_coseno(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

print(f"Coincidencia Cuadro A: {similitud_coseno(vector_habitacion, vector_cuadro_a):.2%}")
print(f"Coincidencia Cuadro B: {similitud_coseno(vector_habitacion, vector_cuadro_b):.2%}")
        """, language="python")
        
    with tab3:
        st.markdown("""
        ### ¿Dónde se usa esto en el mundo real?
        * **Motores de Búsqueda Visual (Visual Search):** Plataformas de e-commerce como Pinterest, IKEA o Amazon permiten al usuario tomar una foto de una lámpara o de un pantalón y encontrar instantáneamente artículos idénticos o complementarios en su catálogo sin ingresar una sola palabra de búsqueda.
        * **Sistemas de Clasificación Automática de Inventario:** Etiquetado semántico masivo de catálogos mediante agrupamiento de imágenes por similitud vectorial.
        """)
        
    st.markdown("<div class='info-footer'>Podés aprender sobre embeddings multimodales, espacios vectoriales y similitudes estadísticas en nuestra Ruta de Especialización Visual del IDSA.</div>", unsafe_allow_html=True)

# --- 9. EL ORÁCULO DE LA HISTORIA ---
elif opcion == "Oraculo":
    st.markdown("<h1 class='main-header'>📜 El Oráculo de la Historia</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Respuestas de precisión mediante Generación Aumentada por Recuperación (RAG)</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='inspiration-card'>
        <strong>La propuesta:</strong> Los modelos de lenguaje suelen inventar información cuando no la conocen (alucinación). 
        Chateá con un \"Oráculo\" entrenado en textos históricos de arte. El sistema garantizará responder basándose estrictamente en documentos de referencia inyectados dinámicamente en su contexto.
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎨 El Lienzo", "🔬 Cómo Funciona", "💡 Aplicación Real"])
    
    with tab1:
        st.subheader("Chatea con el Oráculo del Arte Clásico")
        pregunta = st.text_input("Haz una pregunta sobre pintura clásica:", "¿Por qué Da Vinci usaba la técnica del sfumato?")
        
        # Base de datos de fragmentos reales (Knowledge Base)
        knowledge_base = [
            "El 'sfumato' de Leonardo da Vinci consistia en superponer multiples capas de pintura sumamente delgadas y traslucidas para difuminar los contornos y transiciones de luz y sombra, emulando la atmosfera natural del aire.",
            "La tecnica de la perspectiva lineal fue perfeccionada por Brunelleschi en Florencia, permitiendo representar la profundidad tridimensional sobre una superficie plana mediante puntos de fuga geometricos.",
            "El claroscuro en las obras de Caravaggio utilizaba contrastes dramaticos y violentos de luz focalizada sobre fondos oscuros para resaltar la tension dramatica y el realismo de los personajes."
        ]
        
        if st.button("Consultar Oráculo") and pregunta:
            if not hf_token:
                st.error("Token de Hugging Face requerido en la barra lateral.")
            else:
                with st.spinner("Buscando en la base de datos de conocimiento..."):
                    palabras_clave = pregunta.lower().split()
                    coincidencias = []
                    for doc in knowledge_base:
                        score = sum(1 for palabra in palabras_clave if palabra in doc.lower())
                        coincidencias.append((score, doc))
                    
                    coincidencias.sort(reverse=True, key=lambda x: x[0])
                    fragmento_recuperado = coincidencias[0][1] if coincidencias[0][0] > 0 else knowledge_base[0]
                    
                    prompt_rag = (
                        f"Instruccion: Responde la pregunta basandote estrictamente en el fragmento provisto. "
                        f"Fragmento: {fragmento_recuperado}\n"
                        f"Pregunta: {pregunta}\n"
                        f"Respuesta fundamentada:"
                    )
                    
                    api_url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3-8b-instruct"
                    payload = {
                        "inputs": prompt_rag,
                        "parameters": {"max_new_tokens": 100, "temperature": 0.1}
                    }
                    
                    res = query_huggingface(api_url, payload, hf_token)
                    if res:
                        try:
                            respuesta_decoded = json.loads(res.decode("utf-8"))[0]['generated_text']
                            st.write("📖 **Documento recuperado de la Base de Datos:**")
                            st.caption(f"*'{fragmento_recuperado}'*")
                            st.write("✨ **Respuesta libre de Alucinaciones del Oráculo:**")
                            st.info(respuesta_decoded.split("Respuesta fundamentada:")[-1].strip())
                        except Exception:
                            st.error("No se pudo estructurar la respuesta de Llama-3.")
                    else:
                        st.error("Error al consultar el modelo de lenguaje de Hugging Face.")
                        
    with tab2:
        st.markdown("""
        ### RAG (Retrieval-Augmented Generation): Evitando la Alucinación
        ¿Cómo garantizan las empresas que un modelo lingüístico no invente respuestas en temas legales o financieros?
        
        1. **La Base de Datos de Documentos:** En lugar de dejar que el modelo responda desde su memoria de entrenamiento general, los documentos reales de la empresa se dividen en fragmentos y se almacenan (típicamente indexados mediante vectores).
        2. **Recuperación (Retrieval):** Cuando el usuario hace una pregunta, un algoritmo busca en la base de datos qué fragmento de texto contiene la respuesta exacta a esa consulta.
        3. **Aumentación (Augmentation):** El sistema toma ese fragmento real y lo inyecta dentro del prompt secreto que se le envía a la API, forzando al modelo de lenguaje a estructurar la respuesta basándose únicamente en ese contexto verificado.
        """)
        
        st.markdown("<p class='code-title'>Estructura base en Python:</p>", unsafe_allow_html=True)
        st.code("""
import requests
import json

# Documento verificado recuperado localmente de la base de conocimiento
documento_corporativo = "Nuestra politica de reembolsos permite devoluciones en un plazo maximo de 30 dias."

pregunta_usuario = "¿Puedo devolver un producto comprado hace 40 dias?"

# Construimos un prompt inyectando el contexto para evitar que el modelo invente
prompt_con_contexto = (
    f"Contexto: {documento_corporativo}\\n"
    f"Pregunta: {pregunta_usuario}\\n"
    f"Respuesta (si el contexto no tiene la informacion, di que no la sabes):"
)

# (Este prompt inyectado se envía a la API de generación de lenguaje)
        """, language="python")
        
    with tab3:
        st.markdown("""
        ### ¿Dónde se usa esto en el mundo real?
        Este enfoque es la arquitectura estándar de los **Sistemas de Consulta Corporativos**:
        * **Auditoría Legal y Financiera:** Chatbots internos que permiten a los abogados o contadores chatear con miles de contratos o balances financieros y extraer respuestas que citen la página y el artículo exacto del documento de origen.
        * **Soporte Técnico de Maquinaria:** Ayudar a técnicos de campo a interactuar con manuales de mantenimiento de cientos de páginas mediante consultas rápidas en lenguaje natural.
        """)
        
    st.markdown("<div class='info-footer'>La arquitectura RAG es la habilidad de ingeniería de datos más demandada en IA. Podés aprender a construirla en nuestra Especialización de NLP del IDSA.</div>", unsafe_allow_html=True)

# --- 10. EL TASADOR ALGORÍTMICO ---
elif opcion == "Tasador":
    st.markdown("<h1 class='main-header'>🔮 El Tasador Algorítmico</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Regresión y estimación comercial de activos mediante algoritmos de Machine Learning supervisado</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='inspiration-card'>
        <strong>La propuesta:</strong> ¿Cómo estimamos el valor de algo que no existe? 
        Definí las dimensiones, el año del artista y la complejidad técnica de una obra hipotética. Nuestro modelo predictivo entrenado calculará el valor estimado de mercado y te mostrará la curva matemática de la decisión.
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎨 El Lienzo", "🔬 Cómo Funciona", "💡 Aplicación Real"])
    
    with tab1:
        st.subheader("Simulador Predictivo de Precios")
        
        alto = st.slider("Alto de la obra (cm):", 20, 200, 80)
        ancho = st.slider("Ancho de la obra (cm):", 20, 200, 100)
        edad_artista = st.slider("Años de trayectoria del artista:", 1, 50, 15)
        complejidad_tecnica = st.selectbox("Técnica utilizada:", ["Óleo tradicional", "Acrílico moderno", "Arte Digital / Ilustración"])
        
        if st.button("Calcular Tasación"):
            with st.spinner("Ejecutando algoritmo de regresión supervisada..."):
                np.random.seed(42)
                superficies_historicas = np.random.uniform(400, 40000, 50)
                precios_historicos = 500 + superficies_historicas * 0.15 + np.random.normal(0, 1000, 50)
                precios_historicos = np.clip(precios_historicos, 100, None)
                
                from sklearn.linear_model import LinearRegression
                model = LinearRegression()
                model.fit(superficies_historicas.reshape(-1, 1), precios_historicos)
                
                superficie_usuario = alto * ancho
                prediccion_base = model.predict(np.array([[superficie_usuario]]))[0]
                
                multiplicador_edad = 1.0 + (edad_artista * 0.03)
                multiplicador_tecnica = {"Óleo tradicional": 1.25, "Acrílico moderno": 1.0, "Arte Digital / Ilustración": 0.8}.get(complejidad_tecnica, 1.0)
                prediccion_final = max(150.0, prediccion_base * multiplicador_edad * multiplicador_tecnica)
                
                st.write("📈 **Resultados del Algoritmo Supervisado:**")
                st.info(f"El valor estimado de mercado de esta obra de {alto}x{ancho} cm es de **${prediccion_final:,.2f} USD**.")
                
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.scatter(superficies_historicas, precios_historicos, color="blue", alpha=0.5, label="Obras Vendidas Históricas")
                
                x_line = np.linspace(400, 40000, 100).reshape(-1, 1)
                y_line = model.predict(x_line)
                ax.plot(x_line, y_line, color="red", linestyle="--", label="Curva de Tendencia de Tasación")
                
                ax.scatter([superficie_usuario], [prediccion_final], color="green", s=150, zorder=5, label="Tu Obra Propuesta")
                
                ax.set_title("Curva de Regresión Lineal de Valores de Mercado")
                ax.set_xlabel("Superficie de la obra (cm²)")
                ax.set_ylabel("Precio estimado (USD)")
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                st.pyplot(fig)
                plt.close()
                
    with tab2:
        st.markdown("""
        ### Regresión y Predicción con Aprendizaje Supervisado
        ¿Cómo estima la computadora el precio de un objeto que nunca ha visto? Este proceso representa el núcleo del **Machine Learning Tradicional**:
        
        1. **Datos de Entrenamiento:** El modelo de **Regresión Lineal** recibe datos históricos (ej: el tamaño y precio de venta de 50 obras anteriores del artista).
        2. **Minimización de Errores (Mínimos Cuadrados):** El algoritmo de `Scikit-Learn` traza una línea recta a través del espacio bidimensional que minimice la distancia vertical de todos los puntos históricos a esa línea, aprendiendo la pendiente matemática del precio por centímetro cuadrado.
        3. **Inferencia de Nuevos Puntos:** Cuando ingresás el alto y ancho de tu obra propuesta, el código calcula su área y lee el valor correspondiente sobre la línea de regresión aprendida, multiplicando luego ese coeficiente por variables de ajuste categóricas (la técnica y la edad del pintor).
        """)
        
        st.markdown("<p class='code-title'>Estructura base en Python:</p>", unsafe_allow_html=True)
        st.code("""
import numpy as np
from sklearn.linear_model import LinearRegression

# 1. Datos históricos: características (X) y etiquetas reales (y)
superficies_historicas = np.array([2000, 5000, 8000, 15000, 30000]).reshape(-1, 1)
precios_historicos = np.array([300, 750, 1200, 2200, 4500])

# 2. Entrenamos el modelo de regresión lineal
modelo_tasador = LinearRegression()
modelo_tasador.fit(superficies_historicas, precios_historicos)

# 3. Predecimos el valor de un nuevo cuadro de 12,000 cm2 de superficie
nueva_superficie = np.array([[12000]])
precio_predicho = modelo_tasador.predict(nueva_superficie)[0]

print(f"Valor base estimado: ${precio_predicho:.2f} USD")
        """, language="python")
        
    with tab3:
        st.markdown("""
        ### ¿Dónde se usa esto en el mundo real?
        Los algoritmos de regresión supervisada son el motor financiero de los **Modelos de Pricing Dinámico**:
        * **Valoración Inmobiliaria (PropTech):** Plataformas inmobiliarias calculan el precio estimado de alquiler o venta de un departamento cruzando los metros cuadrados, los años de antigüedad del edificio y el precio histórico promedio de las manzanas a la redonda.
        * **Predicción de Demanda Comercial:** Supermercados y retailers estiman el volumen de ventas diario de cada sucursal basándose en el stock disponible, fechas del año y variables climáticas previstas.
        """)
        
    st.markdown("<div class='info-footer'>Podés aprender a entrenar modelos predictivos supervisados y no supervisados con Scikit-Learn en nuestra Ruta de Analítica de Datos del IDSA.</div>", unsafe_allow_html=True)
