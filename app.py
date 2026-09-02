import streamlit as st
import requests
import time
from PIL import Image
from io import BytesIO
import base64

# ============================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Galería Algorítmica | Instituto Data Science Argentina",
    page_icon="🎨",
    layout="centered"
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
    .section-title {
        font-family: 'Georgia', serif;
        color: #2c3e50;
        margin-top: 1rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
    }
    .footer {
        text-align: center;
        color: #95a5a6;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #ecf0f1;
    }
    .sidebar-info {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
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
    ["🏠 Inicio", "📸 Opción A: Retrato Algorítmico", "🎨 Opción C: Poema Visual"]
)

st.sidebar.markdown("---")

# Configuración del token (solo si no está en secrets.toml)
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
        response = requests.post(api_url, headers=headers, json=payload)
        
        if response.status_code == 503:
            estimated_time = response.json().get("estimated_time", 20)
            st.warning(f"🎨 El modelo está despertando... esperando {estimated_time:.0f} segundos (Intento {attempt + 1}/{retries})")
            time.sleep(estimated_time)
            continue
        elif response.status_code == 200:
            return response.content
        else:
            st.error(f"Error en la API: {response.status_code} - {response.text}")
            return None
            
    st.error("El modelo tardó demasiado en responder. Por favor, inténtalo de nuevo en unos momentos.")
    return None

def image_to_base64(image):
    """Convierte una imagen PIL a base64 para enviarla a la API."""
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

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
            Explora la intersección entre la inteligencia artificial y la creatividad humana.
            <br>Elige una experiencia en el menú lateral para comenzar.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📸 Retrato Algorítmico")
        st.markdown("""
        Sube tu foto y transforma tu rostro en una obra de arte digital.
        El algoritmo reinterpretará tu imagen según tus instrucciones creativas.
        """)
        st.info("💡 Prueba: 'Conviértelo en una pintura al óleo renacentista'")
    
    with col2:
        st.markdown("### 🎨 Poema Visual")
        st.markdown("""
        Escribe una palabra, frase o verso. El algoritmo lo traducirá
        en una pieza de arte abstracto única y evocadora.
        """)
        st.info("💡 Prueba: 'Melancolía digital' o 'Café y código'")
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #95a5a6; font-size: 0.9rem;">
        <p>Proyecto del <strong>Instituto Data Science Argentina</strong></p>
        <p>Tecnología: Hugging Face Inference API · Stable Diffusion · InstructPix2Pix</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# OPCIÓN A: RETRATO ALGORÍTMICO (InstructPix2Pix)
# ============================================================
elif opcion == "📸 Opción A: Retrato Algorítmico":
    st.markdown("<h1 class='main-header'>📸 Retrato Algorítmico</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Transforma tu rostro en una obra de arte digital</p>", unsafe_allow_html=True)
    
    st.markdown("### 📤 Sube tu imagen")
    uploaded_file = st.file_uploader(
        "Elige una imagen (preferentemente un retrato)",
        type=["jpg", "jpeg", "png"],
        help="Sube una foto clara de tu rostro para mejores resultados"
    )
    
    st.markdown("### ✍️ Describe tu transformación")
    instruction = st.text_area(
        "¿Cómo quieres que el algoritmo transforme tu imagen?",
        placeholder="Ej: 'Conviértelo en una pintura al óleo', 'Añade un sombrero de copa', 'Hazlo parecer un personaje de cyberpunk'...",
        height=100
    )
    
    if st.button("🎨 Generar Retrato Algorítmico", type="primary", use_container_width=True):
        if not hf_token:
            st.warning("⚠️ Por favor, configura tu Hugging Face Token en la barra lateral.")
        elif not uploaded_file:
            st.warning("⚠️ Por favor, sube una imagen primero.")
        elif not instruction.strip():
            st.warning("⚠️ Por favor, describe cómo quieres transformar tu imagen.")
        else:
            with st.spinner("🌌 El algoritmo está trabajando en tu retrato..."):
                # Cargar y preparar la imagen
                input_image = Image.open(uploaded_file).convert("RGB")
                input_image = input_image.resize((512, 512))
                
                # API de InstructPix2Pix
                api_url = "https://api-inference.huggingface.co/models/timbrooks/instruct-pix2pix"
                
                payload = {
                    "inputs": instruction,
                    "parameters": {
                        "image": image_to_base64(input_image),
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5,
                        "image_guidance_scale": 1.5
                    }
                }
                
                image_bytes = query_huggingface(api_url, payload, hf_token)
                
                if image_bytes:
                    st.success("¡Tu retrato algorítmico ha sido creado!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Imagen Original**")
                        st.image(input_image, use_container_width=True)
                    
                    with col2:
                        st.markdown("**Resultado Algorítmico**")
                        result_image = Image.open(BytesIO(image_bytes))
                        st.image(result_image, use_container_width=True)
                    
                    # Botón de descarga
                    buf = BytesIO()
                    result_image.save(buf, format="PNG")
                    st.download_button(
                        label="📥 Descargar tu Retrato Algorítmico",
                        data=buf.getvalue(),
                        file_name="retrato_algoritmico.png",
                        mime="image/png",
                        use_container_width=True
                    )
    
    st.markdown("<div class='footer'>Galería Algorítmica · Instituto Data Science Argentina</div>", unsafe_allow_html=True)

# ============================================================
# OPCIÓN C: POEMA VISUAL (Stable Diffusion 2.1)
# ============================================================
elif opcion == "🎨 Opción C: Poema Visual":
    st.markdown("<h1 class='main-header'>🎨 Generador de Poemas Visuales</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Escribe una palabra, frase o verso. El algoritmo lo traducirá en una pieza de arte abstracta única.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        user_input = st.text_input(
            "✨ Tu poema o palabra clave:",
            placeholder="Ej: 'Melancolía digital', 'Café y código', 'Atardecer en los datos'..."
        )
        
        generate_btn = st.button("Generar Poema Visual", type="primary", use_container_width=True)
    
    if generate_btn:
        if not hf_token:
            st.warning("⚠️ Por favor, configura tu Hugging Face Token en la barra lateral.")
        elif not user_input.strip():
            st.warning("⚠️ Por favor, escribe una palabra o frase para inspirar al algoritmo.")
        else:
            with st.spinner("🌌 Tejiendo tu poema visual..."):
                enhanced_prompt = f"abstract art, visual poetry, generative art, {user_input}, vibrant colors, fluid shapes, digital masterpiece, highly detailed, ethereal, conceptual art, trending on artstation"
                negative_prompt = "text, watermark, realistic, photographic, ugly, deformed, low quality, signature, letters"
                
                api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
                
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
                    st.success("¡Tu poema visual ha sido creado!")
                    image = Image.open(BytesIO(image_bytes))
                    st.image(image, caption=f"Interpretación visual de: '{user_input}'", use_container_width=True)
                    
                    buf = BytesIO()
                    image.save(buf, format="PNG")
                    safe_filename = "".join(c for c in user_input if c.isalnum() or c in (' ', '_')).rstrip()[:20]
                    
                    st.download_button(
                        label="📥 Descargar tu Poema Visual",
                        data=buf.getvalue(),
                        file_name=f"poema_visual_{safe_filename.replace(' ', '_')}.png",
                        mime="image/png",
                        use_container_width=True
                    )
    
    st.markdown("<div class='footer'>Galería Algorítmica · Instituto Data Science Argentina</div>", unsafe_allow_html=True)
