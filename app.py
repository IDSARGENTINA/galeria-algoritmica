import streamlit as st
from PIL import Image

st.set_page_config(page_title="Galería Algorítmica", page_icon="🎨", layout="centered")

st.title("🎨 Galería Algorítmica")
st.markdown("### Transforma tu rostro en arte generado por IA")

st.info("⚠️ Versión de demostración. La transformación con IA estará activa próximamente.")

uploaded_file = st.file_uploader("Sube una foto", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    imagen = Image.open(uploaded_file)
    
    # Mostramos la imagen de forma lineal (sin columnas para evitar el bug)
    st.image(imagen, caption="Tu foto original", use_column_width=True)
    
    st.markdown("---")
    st.markdown("""
    **¿Cómo funciona?**
    
    Próximamente: Transformación real con IA usando Hugging Face API.
    
    *¿Quieres aprender a crear esto? [Ver micro-curso](#)*
    """)
