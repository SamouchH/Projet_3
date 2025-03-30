import streamlit as st


st.set_page_config(
    page_title="Assistant vendeur",
    page_icon="👩‍💻",
)

st.subheader("Analyse du set de données d'entrainement")

st.markdown(
    """
    Dans le cadre de notre projet, **Jimmy**, **Haroune** et **Alexandre** ont exploré plusieurs modèles de classification afin d’évaluer la meilleure approche pour notre jeu de données.

    L’objectif de ce benchmark est de comparer :
    - La **précision** des modèles
    - Le **temps d'entraînement**
    - La **capacité à généraliser** (via validation croisée)
    - Et leur **facilité d’intégration** dans notre application Streamlit

    👇 Retrouvez ci-dessous un aperçu de leurs travaux. Les détails techniques et résultats seront complétés au fur et à mesure de l’analyse.
    """
    )

    col_alex, col_haroune, col_jimmy = st.columns(3)

    with col_alex:
        st.write('bla bla')

    with col_haroune:
        st.write('bla bla')
    
    with col_jimmy:
        st.write('bla bla')