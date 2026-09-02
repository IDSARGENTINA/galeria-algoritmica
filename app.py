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
    page_icon="",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. ESTILOS CSS CON CLIMA ARTÍSTICO
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Lora:ital@0;1&display=swap');
    
    .main-header { 
        text-align: center; 
        font-family: 'Playfair Display', serif; 
        color: #2c3e50; 
        margin-bottom: 0.5rem; 
        font-size: 2.8rem;
        font-weight: 700;
    }
    .sub-header { 
        text-align: center; 
        color: #7f8c8d; 
        font-family: 'Lora', serif;
        font-style: italic; 
        margin-bottom: 2rem; 
        font-size: 1.2rem; 
    }
    .welcome-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    .welcome-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        margin-bottom: 1rem;
    }
    .welcome-text {
        font-family: 'Lora', serif;
        font-size: 1.1rem;
        line-height: 1.6;
        opacity: 0.95;
    }
    .project-intro {
        background: linear-gradient(to right, #f8f9fa, #e9ecef);
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border-left: 5px solid #667eea;
    }
    .project-title {
        font-family: 'Playfair Display', serif;
        color: #2c3e50;
        font-size: 1.5rem;
        margin-bottom: 0.8rem;
    }
    .project-description {
        font-family: 'Lora', serif;
        color: #34495e;
        font-size: 1.05rem;
        line-height: 1.7;
        margin-bottom: 1rem;
    }
    .inspiration-box {
        background: #fff9e6;
        border: 2px dashed #f1c40f;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-family: 'Lora', serif;
        font-style: italic;
        color: #7f6c00;
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
        font-family: 'Lora', serif;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# 3. GESTIÓN DE TOKEN Y NAVEGACIÓN
# ============================================================
hf_token = st.secrets.get("HF_TOKEN", "")

st.sidebar.title("️ Galería Algorítmica")
st.sidebar.markdown("**Instituto Data Science Argentina**")
st.sidebar.markdown("---")

menu_keys = ["Inicio", "Retrato", "Poema", "Memes", "Emociones", "Historias", "DataArt"]

menu_labels = {
    "Inicio": "🏠 Inicio",
    "Retrato": "📸 Retrato Algorítmico",
    "Poema": "🎨 Poema Visual",
    "Memes": "😂 Generador de Memes",
    "Emociones": "💝 Visualizador de Emociones",
    "Historias": "📖 Historias Interactivas",
    "DataArt": " Data Art Generator"
}

opcion = st.sidebar.radio(
    "Elige una experiencia:",
    menu_keys,
    format_func=lambda x: menu_labels[x]
)

st.sidebar.markdown("---")
if not hf_token:
    with st.sidebar.expander("⚙️ Configurar Token"):
        hf_token = st.text_input("Hugging Face Token", type="password")
        st.info("💡 Guárdalo en Secrets para producción.")
else:
    st.sidebar.success("✅ Token configurado")

st.sidebar.caption("🎨 Arte con IA · 100% Gratuito")

# ============================================================
# 4. FUNCIONES AUXILIARES
# ============================================================
def query_huggingface(api_url, payload, token, retries=3):
    headers = {"Authorization": f"Bearer {token}"}
    for attempt in range(retries):
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            if response.status_code == 503:
                wait_time = response.json().get("estimated_time", 20)
                st.warning(f"⏳ El modelo está despertando... esperando {wait_time:.0f}s (Intento {attempt+1}/{retries})")
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
    st.markdown("<p class='sub-header'>Donde el código se convierte en poesía visual</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="welcome-box">
        <div class="welcome-title">✨ Bienvenido al futuro del arte</div>
        <div class="welcome-text">
            Esta no es una galería común. Aquí los algoritmos son los artistas, los datos son los pinceles, 
            y vos sos el curador. Cada obra que vas a crear es única, irrepetible, nacida de la colaboración 
            entre tu imaginación y la inteligencia artificial.<br><br>
            <b>¿Listo para crear algo que nadie más en el mundo ha visto?</b>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ️ Tu recorrido por la galería")
    
    experiencias = [
        ("📸", "Retrato Algorítmico", "Transformá tu selfie en una obra maestra. ¿Cómo te verías pintado por Van Gogh o en estilo cyberpunk?"),
        ("🎨", "Poema Visual", "Escribí una palabra, un verso, un sentimiento. Mirá cómo la IA lo traduce en colores y formas abstractas."),
        ("😂", "Generador de Memes", "Porque el humor también es arte. Describí una situación y dejá que la IA cree el meme perfecto."),
        ("", "Visualizador de Emociones", "¿Cómo se ve la alegría? ¿Y la melancolía? Escribí lo que sentís y observá cómo la IA lo pinta."),
        ("📖", "Historias Interactivas", "Vos elegís el género, la IA escribe. Vos decidís qué pasa después. Una novela colaborativa con una máquina."),
        ("📊", "Data Art Generator", "Subí un CSV aburrido y miralo transformarse en arte abstracto. Los datos nunca fueron tan bellos.")
    ]
    
    for icon, titulo, desc in experiencias:
        st.markdown(f"""
        <div class="project-intro">
            <div class="project-title">{icon} {titulo}</div>
            <div class="project-description">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem;">
        <p style="font-family: 'Lora', serif; font-style: italic; color: #7f8c8d; font-size: 1.1rem;">
            "El arte es la mentira que nos permite ver la verdad." — Pablo Picasso<br>
            <span style="font-size: 0.9rem;">(Ahora con un toque de algoritmos)</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- OPCIÓN A: RETRATO ---
elif opcion == "Retrato":
    st.markdown("<h1 class='main-header'>📸 Retrato Algorítmico</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Tu rostro, reinterpretado por una máquina que sueña</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="project-intro">
        <div class="project-title">️ La experiencia</div>
        <div class="project-description">
            ¿Alguna vez te preguntaste cómo te verías si fueras pintado por un maestro renacentista? 
            ¿O si vivieras en un universo cyberpunk? Acá tenés la oportunidad de descubrirlo. 
            Subí tu foto, describí la transformación que imaginás, y dejá que el algoritmo haga su magia. 
            Cada resultado es una pieza única de arte digital que podés descargar y compartir.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="inspiration-box">
         <b>Inspiración:</b> Probá con "Convierteme en una pintura al óleo del siglo XVII", 
        "Hazme parecer un personaje de Blade Runner", o "Transformame en acuarela japonesa"
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='tech-box'><div class='tech-title'> Detrás de escena:</div><div class='tech-item'>🤖 <b>Modelo:</b> InstructPix2Pix — un algoritmo que entiende instrucciones en lenguaje natural para editar imágenes</div><div class='tech-item'>🧠 <b>Conceptos:</b> Computer Vision, Image-to-Image Translation, Transfer Learning</div><div class='tech-item'>📚 <b>Perfecto para el curso:</b> Fundamentos de Visión por Computadora y Edición de Imágenes con IA</div></div>", unsafe_allow_html=True)
    
    uploaded = st.file_uploader(" Subí tu imagen (preferentemente un retrato)", type=["jpg", "png"])
    prompt = st.text_area("✍️ Describí la transformación que imaginás", placeholder="Ej: 'Convierteme en una pintura al óleo renacentista'", height=100)
    
    if st.button("🎨 Crear mi retrato algorítmico", type="primary", use_container_width=True):
        if not hf_token or not uploaded or not prompt:
            st.warning("⚠️ Completá todos los campos para comenzar la magia.")
        else:
            with st.spinner("🌌 El algoritmo está interpretando tu visión..."):
                img = Image.open(uploaded).convert("RGB").resize((512, 512))
                res = query_huggingface(
                    "https://api-inference.huggingface.co/models/timbrooks/instruct-pix2pix",
                    {"inputs": prompt, "parameters": {"image": image_to_base64(img), "num_inference_steps": 25}},
                    hf_token
                )
                if res:
                    st.success("✨ ¡Tu retrato algorítmico está listo!")
                    st.image(Image.open(BytesIO(res)), caption=f"Tu visión: '{prompt}'", use_container_width=True)
                    buf = BytesIO()
                    Image.open(BytesIO(res)).save(buf, format="PNG")
                    st.download_button("📥 Descargar mi obra de arte", data=buf.getvalue(), file_name="retrato_algoritmico.png", mime="image/png")

# --- OPCIÓN C: POEMA ---
elif opcion == "Poema":
    st.markdown("<h1 class='main-header'>🎨 Poema Visual</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Cuando las palabras se transforman en colores y formas</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="project-intro">
        <div class="project-title"> La experiencia</div>
        <div class="project-description">
            Hay palabras que no se pueden explicar, solo se pueden sentir. "Melancolía". "Euforia". 
            "Nostalgia digital". Escribí una palabra, una frase, un verso que te represente, 
            y observá cómo la inteligencia artificial lo traduce en una pieza de arte abstracto única. 
            Cada generación es irrepetible, como una huella digital del alma.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="inspiration-box">
        💡 <b>Inspiración:</b> Probá con "Melancolía digital", "Café y código a las 3am", 
        "El sonido del silencio", o tu verso favorito de un poema
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='tech-box'><div class='tech-title'>🔬 Detrás de escena:</div><div class='tech-item'>🤖 <b>Modelo:</b> Stable Diffusion v1.5 — el modelo de generación de imágenes más popular del mundo</div><div class='tech-item'>🧠 <b>Conceptos:</b> Diffusion Models, Latent Space, Prompt Engineering, Text-to-Image</div><div class='tech-item'>📚 <b>Perfecto para el curso:</b> Generative AI y Modelos de Difusión</div></div>", unsafe_allow_html=True)
    
    texto = st.text_input("✨ Escribí tu palabra, frase o verso", placeholder="Ej: 'Melancolía digital'")
    
    if st.button("🎨 Transformar en arte visual", type="primary", use_container_width=True):
        if not hf_token or not texto:
            st.warning("⚠️ Escribí algo que te inspire para comenzar.")
        else:
            with st.spinner("🌌 Tejiendo tu poema visual..."):
                res = query_huggingface(
                    "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
                    {"inputs": f"abstract art, visual poetry, {texto}, vibrant colors, fluid shapes, digital masterpiece, ethereal, conceptual art", "parameters": {"negative_prompt": "text, watermark, realistic, ugly", "num_inference_steps": 30, "guidance_scale": 7.5}},
                    hf_token
                )
                if res:
                    st.success("✨ ¡Tu poema visual ha nacido!")
                    st.image(Image.open(BytesIO(res)), caption=f"Interpretación de: '{texto}'", use_container_width=True)
                    buf = BytesIO()
                    Image.open(BytesIO(res)).save(buf, format="PNG")
                    st.download_button("📥 Descargar mi poema visual", data=buf.getvalue(), file_name=f"poema_{texto[:20].replace(' ', '_')}.png", mime="image/png")

# --- OPCIÓN D: MEMES ---
elif opcion == "Memes":
    st.markdown("<h1 class='main-header'>😂 Generador de Memes</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Porque el humor también es una forma de arte digital</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="project-intro">
        <div class="project-title">🎭 La experiencia</div>
        <div class="project-description">
            Los memes son el folklore del siglo XXI. Son cómo nos reímos de nosotros mismos, 
            cómo compartimos experiencias, cómo creamos cultura colectiva. Acá tenés el poder 
            de crear memes únicos que nadie más en internet ha visto. Describí una situación 
            cotidiana, absurda o hilarante, y dejá que la IA genere la imagen perfecta. 
            Después agregale texto y compartilo con el mundo.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="inspiration-box">
        💡 <b>Inspiración:</b> "Cuando el código compila a la primera", "Lunes a las 9am", 
        "Cuando el cliente pide cambios el viernes a las 18hs"
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='tech-box'><div class='tech-title'>🔬 Detrás de escena:</div><div class='tech-item'> <b>Modelo:</b> Stable Diffusion + PIL ImageDraw — generación de imágenes + composición de texto</div><div class='tech-item'>🧠 <b>Conceptos:</b> Text-to-Image, Image Composition, Text Rendering, Cultural Pattern Recognition</div><div class='tech-item'> <b>Perfecto para el curso:</b> Procesamiento de Imágenes y Composición Visual</div></div>", unsafe_allow_html=True)
    
    desc = st.text_area(" Describí la situación del meme", placeholder="Ej: 'Cuando el código compila a la primera'", height=100)
    t1 = st.text_input("Texto superior (opcional)", placeholder="Ej: 'YO:'")
    t2 = st.text_input("Texto inferior (opcional)", placeholder="Ej: 'EL CÓDIGO:'")
    
    if st.button(" Crear mi meme", type="primary", use_container_width=True):
        if not hf_token or not desc:
            st.warning("⚠️ Describí una situación para comenzar.")
        else:
            with st.spinner("🎨 Generando tu meme..."):
                res = query_huggingface(
                    "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
                    {"inputs": f"meme style, funny image, {desc}, humorous, viral, simple background", "parameters": {"negative_prompt": "text, watermark, realistic, ugly", "num_inference_steps": 25}},
                    hf_token
                )
                if res:
                    img = Image.open(BytesIO(res))
                    if t1 or t2:
                        img = draw_meme_text(img, t1, t2)
                    st.success("✨ ¡Meme creado! Listo para viralizar")
                    st.image(img, caption=f"Meme: '{desc}'", use_container_width=True)
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button("📥 Descargar meme", data=buf.getvalue(), file_name="meme_ia.png", mime="image/png")

# --- OPCIÓN E: EMOCIONES ---
elif opcion == "Emociones":
    st.markdown("<h1 class='main-header'>💝 Visualizador de Emociones</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>¿Cómo se vería lo que sentís? Descubrilo acá</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="project-intro">
        <div class="project-title">🎭 La experiencia</div>
        <div class="project-description">
            Las emociones son universales, pero cada una tiene su propio color, su propia textura, 
            su propia forma. La alegría es cálida y brillante. La tristeza es fría y profunda. 
            La ira es intensa y roja. Escribí lo que sentís en este momento —un tweet, un poema, 
            un mensaje— y observá cómo la inteligencia artificial detecta tu emoción dominante 
            y la traduce en una pieza de arte abstracto. Es como un espejo emocional, pero pintado por una máquina.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="inspiration-box">
        💡 <b>Inspiración:</b> Escribí algo auténtico. "Hoy me siento en paz", "Extraño a alguien", 
        "Estoy furioso con el tráfico", "No puedo creer lo que pasó"
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='tech-box'><div class='tech-title'> Detrás de escena:</div><div class='tech-item'>🤖 <b>Modelo:</b> NLP (análisis de sentimientos) + Stable Diffusion — detección de emociones + generación de arte</div><div class='tech-item'>🧠 <b>Conceptos:</b> Natural Language Processing, Sentiment Analysis, Emotion Detection, Color Theory, Data Visualization</div><div class='tech-item'>📚 <b>Perfecto para el curso:</b> Procesamiento de Lenguaje Natural y Análisis de Sentimientos</div><div class='tech-item'>💡 <b>Próximo nivel:</b> Modelos como RoBERTa o BERT para análisis más preciso</div></div>", unsafe_allow_html=True)
    
    texto = st.text_area(" Escribí lo que sentís (un tweet, un poema, un mensaje)", placeholder="Ej: 'Hoy me siento en paz, todo fluye'", height=100)
    
    if st.button("💝 Visualizar mis emociones", type="primary", use_container_width=True):
        if not hf_token or not texto:
            st.warning("⚠️ Escribí lo que sentís para comenzar.")
        else:
            with st.spinner("🎨 Analizando tus emociones..."):
                emots = {
                    "alegría": ["feliz", "alegre", "contento", "maravilloso", "excelente", "genial", "paz", "amor"],
                    "tristeza": ["triste", "melancólico", "deprimido", "llorar", "dolor", "extraño", "soledad"],
                    "ira": ["enojado", "furioso", "molesto", "irritado", "odio", "rabia", "frustrado"],
                    "miedo": ["miedo", "terror", "asustado", "pánico", "ansiedad", "nervioso"],
                    "sorpresa": ["sorprendido", "asombrado", "increíble", "wow", "impresionado", "no puedo creer"]
                }
                text_lower = texto.lower()
                detected = {k: sum(1 for w in v if w in text_lower) for k, v in emots.items()}
                dom = max(detected, key=detected.get) if any(detected.values()) else "neutral"
                
                styles = {
                    "alegría": "bright yellow and orange colors, sunny, cheerful, warm, radiant",
                    "tristeza": "blue and gray colors, melancholic, rainy, somber, deep",
                    "ira": "red and black colors, fiery, intense, dramatic, explosive",
                    "miedo": "dark purple and black, mysterious, shadowy, eerie, tense",
                    "sorpresa": "vibrant multicolor, explosive, dynamic, energetic, shocking",
                    "neutral": "balanced colors, calm, peaceful, serene, harmonious"
                }
                
                res = query_huggingface(
                    "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
                    {"inputs": f"abstract art, {styles[dom]}, emotion visualization, expressive, artistic, masterpiece", "parameters": {"negative_prompt": "text, watermark, realistic, ugly", "num_inference_steps": 30}},
                    hf_token
                )
                if res:
                    st.markdown("###  Análisis emocional:")
                    for emotion, count in detected.items():
                        if count > 0:
                            st.write(f"- **{emotion.capitalize()}**: {'❤️' * count}")
                    st.markdown(f"**Emoción dominante:** {dom.capitalize()}")
                    st.image(Image.open(BytesIO(res)), caption=f"Visualización de tu emoción: {dom}", use_container_width=True)
                    buf = BytesIO()
                    Image.open(BytesIO(res)).save(buf, format="PNG")
                    st.download_button("📥 Descargar mi emoción visualizada", data=buf.getvalue(), file_name=f"emocion_{dom}.png", mime="image/png")

# --- OPCIÓN F: HISTORIAS ---
elif opcion == "Historias":
    st.markdown("<h1 class='main-header'>📖 Historias Interactivas</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Vos elegís el género, la IA escribe. Vos decidís qué pasa después.</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="project-intro">
        <div class="project-title">📚 La experiencia</div>
        <div class="project-description">
            Imaginá una novela donde vos sos el co-autor. Elegís el género —ciencia ficción, fantasía, terror— 
            y la inteligencia artificial escribe el primer capítulo. Después, vos decidís qué hace el protagonista: 
            ¿abre la puerta misteriosa o huye del lugar? La historia continúa según tus decisiones. 
            Es como un libro de "Elige tu propia aventura", pero escrito en tiempo real por una máquina 
            que aprendió de millones de historias. Cada lectura es única, cada decisión cuenta.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="inspiration-box">
        💡 <b>Inspiración:</b> Elegí un género que te apasione. ¿Siempre quisiste leer una historia de 
        terror en una estación espacial? ¿O una fantasía épica con dragones? Acá podés crearla.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='tech-box'><div class='tech-title'>🔬 Detrás de escena:</div><div class='tech-item'> <b>Modelo:</b> GPT-2 (Generative Pre-trained Transformer) — un modelo de lenguaje que genera texto coherente</div><div class='tech-item'>🧠 <b>Conceptos:</b> Natural Language Processing, Language Modeling, Text Generation, Transformers, Attention Mechanism, Temperature Sampling</div><div class='tech-item'>📚 <b>Perfecto para el curso:</b> Modelos de Lenguaje y Generación de Texto con Transformers</div><div class='tech-item'>💡 <b>Próximo nivel:</b> GPT-3, GPT-Neo, o fine-tuning en datasets de historias</div></div>", unsafe_allow_html=True)
    
    if "story" not in st.session_state:
        st.session_state.story = ""
    
    genero = st.selectbox("🎭 Elegí el género de tu historia", ["Ciencia Ficción", "Fantasía", "Terror", "Romance", "Aventura"])
    
    if st.button("📖 Iniciar una nueva historia", type="primary", use_container_width=True):
        if hf_token:
            with st.spinner(" La IA está escribiendo el primer capítulo..."):
                res = query_huggingface(
                    "https://api-inference.huggingface.co/models/gpt2",
                    {"inputs": f"En un mundo de {genero.lower()}, ", "parameters": {"max_new_tokens": 150, "temperature": 0.8, "top_p": 0.9}},
                    hf_token
                )
                if res:
                    try:
                        st.session_state.story = json.loads(res)[0]["generated_text"]
                        st.success("✨ ¡El primer capítulo está listo!")
                    except:
                        st.error("❌ Error al generar la historia. Intentá de nuevo.")
    
    if st.session_state.story:
        st.markdown("###  Tu historia:")
        st.write(st.session_state.story)
        
        st.markdown("###  ¿Qué hace el protagonista ahora?")
        decision = st.text_input("Escribí la próxima acción", placeholder="Ej: 'Abre la puerta misteriosa' o 'Huye del lugar'")
        
        if st.button("🔄 Continuar la historia"):
            if decision and hf_token:
                with st.spinner("📚 La IA está escribiendo el próximo capítulo..."):
                    res = query_huggingface(
                        "https://api-inference.huggingface.co/models/gpt2",
                        {"inputs": st.session_state.story + f" Entonces, {decision}", "parameters": {"max_new_tokens": 100, "temperature": 0.8}},
                        hf_token
                    )
                    if res:
                        try:
                            st.session_state.story = json.loads(res)[0]["generated_text"]
                            st.rerun()
                        except:
                            st.error("❌ Error al continuar. Intentá de nuevo.")

# --- OPCIÓN G: DATA ART ---
elif opcion == "DataArt":
    st.markdown("<h1 class='main-header'> Data Art Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Cuando los datos aburridos se transforman en arte abstracto</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="project-intro">
        <div class="project-title">📈 La experiencia</div>
        <div class="project-description">
            Los datos son el nuevo petróleo, pero también pueden ser el nuevo lienzo. Subí un archivo CSV 
            —ventas mensuales, temperaturas anuales, estadísticas de cualquier cosa— y observá cómo 
            la inteligencia artificial analiza los patrones estadísticos y los transforma en una pieza 
            de arte abstracto única. Las medias, las desviaciones estándar, las correlaciones, todo se 
            convierte en colores, formas y texturas. Es la belleza oculta de los datos, revelada por un algoritmo.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="inspiration-box">
        💡 <b>Inspiración:</b> Subí cualquier CSV que tengas a mano. Datos de ventas, clima, deportes, 
        redes sociales. Cuanto más variados los datos, más interesante el arte resultante.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='tech-box'><div class='tech-title'>🔬 Detrás de escena:</div><div class='tech-item'> <b>Modelo:</b> Stable Diffusion + Pandas/NumPy — análisis estadístico + generación de arte basado en datos</div><div class='tech-item'>🧠 <b>Conceptos:</b> Data Analysis, Statistical Measures (mean, std), Exploratory Data Analysis (EDA), Data Visualization, Data-Driven Art, Pattern Recognition</div><div class='tech-item'>📚 <b>Perfecto para el curso:</b> Análisis de Datos y Visualización Creativa con Python</div><div class='tech-item'>💡 <b>Próximo nivel:</b> PCA, t-SNE para reducción dimensional, clustering con K-Means</div></div>", unsafe_allow_html=True)
    
    csv = st.file_uploader("📤 Subí tu archivo CSV", type=["csv"])
    
    if csv:
        try:
            df = pd.read_csv(csv)
            st.success(f"✅ Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
            
            st.markdown("### 📊 Vista previa de tus datos:")
            st.write(df.head())
            
            st.markdown("### 📈 Estadísticas:")
            st.write(df.describe())
            
            if st.button("🎨 Transformar datos en arte", type="primary", use_container_width=True):
                if hf_token:
                    with st.spinner(" Analizando patrones y generando arte..."):
                        num_cols = df.select_dtypes(include=[np.number]).columns
                        stats = []
                        if len(num_cols) > 0:
                            for col in num_cols[:3]:
                                mean_val = df[col].mean()
                                std_val = df[col].std()
                                stats.append(f"{col}: media={mean_val:.2f}, std={std_val:.2f}")
                        
                        data_desc = ", ".join(stats) if stats else "datos variados"
                        
                        res = query_huggingface(
                            "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
                            {"inputs": f"abstract data visualization art, {data_desc}, geometric patterns, data-driven art, modern, colorful, digital masterpiece", "parameters": {"negative_prompt": "text, watermark, realistic, ugly", "num_inference_steps": 30}},
                            hf_token
                        )
                        if res:
                            st.success("✨ ¡Tu Data Art está listo!")
                            st.image(Image.open(BytesIO(res)), caption="Arte generado desde tus datos", use_container_width=True)
                            buf = BytesIO()
                            Image.open(BytesIO(res)).save(buf, format="PNG")
                            st.download_button("📥 Descargar mi Data Art", data=buf.getvalue(), file_name="data_art.png", mime="image/png")
        except Exception as e:
            st.error(f"❌ Error al procesar el CSV: {str(e)}")
    else:
        st.info("📤 Subí un archivo CSV para comenzar la experiencia")

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class='footer'>
    🎨 Galería Algorítmica · Instituto Data Science Argentina · 2026<br>
    <span style='font-size: 0.8rem;'>Donde el código se convierte en poesía visual</span>
</div>
""", unsafe_allow_html=True)
