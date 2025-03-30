import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Assistant vendeur",
    page_icon="👩‍💻",
)

def main():
    st.write("# Assistant de création d'annonce pour vendeur particulier")
    git_alex = ""
    git_armelle = "https://github.com/D41g0na"
    git_haroune = "https://github.com/SamouchH"
    git_jimmy = ""
    st.markdown(
        """
    Ce projet s'inscrit dans le cadre de notre **année de Master**, avec pour objectif de **faciliter la création d'annonces pour les vendeurs particuliers**.

    Publier une annonce en ligne peut être **fastidieux**, notamment lorsqu'il faut **renseigner manuellement la catégorie du produit, décrire ses caractéristiques et rédiger un texte attractif**.
    Notre solution propose **un assistant intelligent**, capable de **préremplir automatiquement la fiche produit**, en s’appuyant sur :

    - 📷 **Analyse d’images** : identification automatique de la **catégorie du produit** pour un gain de temps.

    Grâce à cette application, la création d’annonces devient **plus rapide, plus efficace et plus intuitive**.


    Auteur.e.s: 
    """
    )
    st.write("[Alexandre](%s)" % git_alex)
    st.write("[Armelle](%s)" % git_armelle)
    st.write("[Haroune](%s)" % git_haroune )
    st.write("[Jimmy](%s)" % git_jimmy)
    #- 📝 **OCR (Reconnaissance de Texte)** : extraction des **informations clés** à partir d'une image (étiquette, facture…).
    #- ✍ **Génération automatique de description** : proposition d'un **texte optimisé pour l'annonce**, basé sur les éléments extraits.
        
if __name__ == "__main__":
    main()
