import streamlit as st
import requests
from PIL import Image
import io
import os

# Configuración de la página
st.set_page_config(
    page_title="Galería Algorítmica - Arte y Datos",
    page_icon="🎨",
    layout="wide"
)

# Título principal
st.title("🎨 Galería Algorítmica")
st.markdown("""
### Transforma tu rostro en una obra de arte generada por IA

Sube una foto y elige un estilo artístico. Cada transformación es única e irrepetible.
""")

# Token de Hugging Face (opcional pero recomendado)
HF_TOKEN = os.environ.get("HF_TOKEN", "")

# Prompts para cada estilo
PROMPTS = {
    "Puntillismo": "Transform this portrait into a pointillism painting with vibrant dots",
    "Van Gogh": "Transform this portrait into a Van Gogh style painting with swirling brushstrokes",
    "Glitch Art": "Transform this portrait into a digital glitch art with pixel distortion",
    "Acuarela": "Transform this portrait into a soft watercolor painting",
    "Pop Art": "Transform this portrait into a pop art style with bold colors"
}

def transformar_imagen_api(imagen_pil, prompt):
    """
    Transforma la imagen usando la API de Hugging Face
    """
    # Convertir imagen a bytes
    buffer = io.BytesIO()
    imagen_pil.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()
    
    # URL de la API (usamos instruct-pix2pix)
    api_url = "https://api-inference.huggingface.co/models/timbrooks/instruct-pix2pix"
    
    # Headers
    headers = {}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"
    
    # Hacer la petición
    try:
        response = requests.post(
            api_url,
            headers=headers,
            data=image_bytes
        )
        
        # Si el modelo está cargándose, esperar
        if response.status_code == 503:
            st.warning("El modelo se está cargando por primera vez. Espera 30-60 segundos e intenta de nuevo.")
            return None
        
        if response.status_code != 200:
            st.error(f"Error de la API: {response.status_code}. Intenta de nuevo en unos segundos.")
            return None
        
        # Convertir respuesta a imagen
        resultado = Image.open(io.BytesIO(response.content))
        return resultado
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Interfaz
col1, col2 = st.columns(2)

with col1:
    st.subheader("📸 Tu foto")
    uploaded_file = st.file_uploader(
        "Sube una foto",
        type=['jpg', 'jpeg', 'png'],
        help="Formatos aceptados: JPG, JPEG, PNG"
    )
    
    if uploaded_file is not None:
        imagen = Image.open(uploaded_file)
        st.image(imagen, caption="Tu foto original", use_column_width=True)
    
    st.subheader("🎨 Elige un estilo")
    estilo = st.selectbox(
        "Estilo artístico",
        ["Puntillismo", "Van Gogh", "Glitch Art", "Acuarela", "Pop Art"]
    )
    
    if uploaded_file is not None:
        if st.button("✨ Transformar", type="primary", use_container_width=True):
            prompt = PROMPTS[estilo]
            
            with st.spinner("Generando tu obra de arte... (puede tardar 20-40 segundos)"):
                resultado = transformar_imagen_api(imagen, prompt)
            
            if resultado is not None:
                with col2:
                    st.subheader("🖼️ Tu obra de arte")
                    st.image(resultado, caption=f"Estilo: {estilo}", use_column_width=True)
                    
                    # Botón para descargar
                    buffer = io.BytesIO()
                    resultado.save(buffer, format="PNG")
                    st.download_button(
                        "⬇️ Descargar obra",
                        data=buffer.getvalue(),
                        file_name=f"obra_{estilo.lower().replace(' ', '_')}.png",
                        mime="image/png"
                    )
                    
                    st.markdown("""
                    ---
                    **¿Cómo funciona esto?**
                    
                    Esta obra no es un filtro. Es una red neuronal que analiza las características de tu rostro 
                    y las reinterpreta a través de un algoritmo de difusión. Cada píxel es una decisión matemática.
                    
                    *¿Quieres entender la magia detrás del código? [Ver micro-curso relacionado](#)*
                    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
Powered by Hugging Face API • Arte generado por IA • Ciencia de Datos creativa
</div>
""", unsafe_allow_html=True)