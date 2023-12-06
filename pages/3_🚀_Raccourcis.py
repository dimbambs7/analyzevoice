import streamlit as st
import pymysql
from config import DB_CONFIG

# Connexion à la base de données MySQL
db = pymysql.connect(**DB_CONFIG)
cursor = db.cursor()

if not st.session_state['signedout']:
        st.write(":red[Veuillez vous connecter]")
else:
    st.set_page_config(page_title="Raccourcis", page_icon="🚀")
    st.markdown("""
<style>
header
{
    visibility: hidden;
}
.css-eh5xgm.e1ewe7hr3
{
    visibility: hidden;
}
.css-cio0dv.e1g8pov61
{
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)
    st.title("🚀 Vos Raccourcis")
    st.write("---")
    options = ["Voir mes raccourcis", "Créer un raccourci", "Modifier un raccourci", "Supprimer un raccourci"]
    selected_options = st.selectbox("Sélectionner une opération :", options)
    user_id = st.session_state['user_id']

    if selected_options == "Voir mes raccourcis":
      st.text("Vos raccourcis :")
      query = f"SELECT * FROM table_shortcut_{user_id}"
      cursor.execute(query)
      shortcuts = cursor.fetchall()
      st.dataframe(shortcuts, width=800)
      if len(shortcuts) == 0:
          st.warning("Vous n'avez aucun raccourci pour l'instant. Créer vore premier raccourci dans l'opération 'Créer un raccourci.")

    elif selected_options == "Supprimer un raccourci":
         shortcut_id = st.number_input("Entrer l'index du raccourci", min_value=1)
         st.warning("L'index du raccourci se trouve sur la colonne de gauche dans l'opération 'Voir mes raccourcis'. ")
         if st.button("Supprimer"):
                  query = f"DELETE FROM table_shortcut_{user_id} WHERE index_shortcut = {shortcut_id}"
                  cursor.execute(query)
                  st.success("Votre raccourci a été supprimé")

    elif selected_options == "Modifier un raccourci":
        shortcut_id = st.number_input("Entrer l'ID du raccourci", min_value=1)
        st.warning("L'index du raccourci se trouve sur la colonne tout à gauche dans l'opération 'Voir mes raccourcis'. ")
        with st.form("modify_shortcut_form", clear_on_submit=True):
          new_shorcut_key = st.text_input(label="", value="", placeholder="Entrer le nouveau mot clé ")
          new_shorcut_letter = st.text_input(label="", value="", placeholder="Entrer la nouvelle lettre associée")
          submit_button = st.form_submit_button("Modifier")
        if submit_button:
             query = f"UPDATE table_shortcut_{user_id} SET shortcut_key = '{new_shorcut_key}', shortcut_letter = '{new_shorcut_letter}' WHERE index_shortcut = {shortcut_id}"
             cursor.execute(query)
             st.success("Votre raccourci a été modifié")

    elif selected_options == "Créer un raccourci":
     with st.form("create_shortcut_form", clear_on_submit=True):
          shorcut_key = st.text_input(label="", value="", placeholder="Mot clé ")
          shortcut_letter = st.text_input(label="", value="", placeholder="Lettre associée")
          submit_button = st.form_submit_button("Créer")
          st.warning("Seulement une seule lettre est acceptée et n'utilisez pas deux fois la même lettre.")

          if submit_button:
               query = f"INSERT INTO table_shortcut_{user_id} (shortcut_key, shortcut_letter) VALUES ('{shorcut_key}', '{shortcut_letter}')"
               cursor.execute(query)
               db.commit()
               st.success("Votre raccourci a été créé !")
