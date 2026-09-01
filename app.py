import streamlit as st
from PIL import Image

# Configuración básica
st.set_page_config(page_title="Galería Algorítmica", page_icon="🎨", layout="centered")

# Título
st.title("🎨 Galería Algorítmica")
st.markdown("### Transforma tu rostro en arte generado por IA")

# Mensaje de estado
st.info("⚠️ Esta es una versión de demostración. La funcionalidad completa de IA estará disponible próximamente.")

# Subida de archivo
uploaded_file = st.file_uploader("Sube una foto", type=['jpg', 'jpeg', 'png'])

# Lógica simple sin columnas complejas
if uploaded_file is not None:
    imagen = Image.open(uploaded_file)
    
    # Mostrar imagen directamente (evita st.columns que a veces causan el error removeChild)
    st.image(imagen, caption="Tu foto original", use_column_width=True)
    
    st.markdown("---")
    st.markdown("""
    **¿Cómo funciona?**
    
    Próximamente: Transformación real con IA usando Hugging Face API.
    
    *¿Quieres aprender a crear esto? [Ver micro-curso](#)*
    """)
