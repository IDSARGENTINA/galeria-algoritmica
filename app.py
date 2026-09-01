import streamlit as st

st.set_page_config(page_title="Galería Algorítmica", page_icon="🎨", layout="centered")

st.title("🎨 Galería Algorítmica")
st.markdown("### Transforma tu rostro en arte generado por IA")

st.info("⚠️ Versión de demostración. La transformación con IA estará activa próximamente.")

uploaded_file = st.file_uploader("Sube una foto", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # Streamlit muestra el archivo subido directamente, ¡sin necesidad de Pillow!
    st.image(uploaded_file, caption="Tu foto original", use_column_width=True)
    
    st.markdown("---")
    st.markdown("""
    **¿Cómo funciona?**
    
    Próximamente: Transformación real con IA usando Hugging Face API.
    
    *¿Quieres aprender a crear esto? [Ver micro-curso](#)*
    """)
