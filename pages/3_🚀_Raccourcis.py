import streamlit as st
<<<<<<< HEAD
from sqlalchemy import text


st.set_page_config(page_title="Raccourcis", page_icon="🚀")

# Connexion à la base de données MySQL
conn = st.connection('mysql', type='sql')
#db_config = st.secrets["mysql"]
#db = pymysql.connect(**db_config)
#cursor = db.cursor()
=======
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

# Utiliser st.secrets pour accéder aux informations sensibles
secrets_dict = st.secrets["connections_gsheets"]

st.set_page_config(page_title="Raccourcis", page_icon="🚀")

# Connexion à la base de données GSheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(secrets_dict, scope)
client = gspread.authorize(creds)
>>>>>>> 3441968 (Premier commit)

if not st.session_state['signedout']:
        st.write(":red[Veuillez vous connecter]")
else:
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
<<<<<<< HEAD
    user_id = st.session_state['user_id']

    if selected_options == "Voir mes raccourcis":
      st.text("Vos raccourcis :")
      query = text(f"SELECT * FROM table_shortcut_{user_id}")
      with conn.session as s:
           result = s.execute(query)
           shortcuts = result.fetchall()
           st.dataframe(shortcuts, width=800)
           if len(shortcuts) == 0:
               st.warning("Vous n'avez aucun raccourci pour l'instant. Créer vore premier raccourci dans l'opération 'Créer un raccourci.")

    elif selected_options == "Supprimer un raccourci":
         shortcut_id = st.number_input("Entrer l'index du raccourci", min_value=1)
         st.warning("L'index du raccourci se trouve sur la colonne de gauche dans l'opération 'Voir mes raccourcis'. ")
         if st.button("Supprimer"):
                with conn.session as s:
                    query = text(f"DELETE FROM table_shortcut_{user_id} WHERE index_shortcut = {shortcut_id}")
                    s.execute(query)
                st.success("Votre raccourci a été supprimé")

    elif selected_options == "Modifier un raccourci":
        shortcut_id = st.number_input("Entrer l'ID du raccourci", min_value=1)
        st.warning("L'index du raccourci se trouve sur la colonne tout à gauche dans l'opération 'Voir mes raccourcis'. ")
        with st.form("modify_shortcut_form", clear_on_submit=True):
          new_shorcut_key = st.text_input(label="", value="", placeholder="Entrer le nouveau mot clé ")
          new_shorcut_letter = st.text_input(label="", value="", placeholder="Entrer la nouvelle lettre associée")
          submit_button = st.form_submit_button("Modifier")
        if submit_button:
            with conn.session as s:
                query = text(f"UPDATE table_shortcut_{user_id} SET shortcut_key = '{new_shorcut_key}', shortcut_letter = '{new_shorcut_letter}' WHERE index_shortcut = {shortcut_id}")
                s.execute(query,{"new_shortcut_key": new_shorcut_key , "new_shortcut_letter": new_shorcut_letter, "shortcut_id": shortcut_id})
            st.success("Votre raccourci a été modifié")

    elif selected_options == "Créer un raccourci":
     with st.form("create_shortcut_form", clear_on_submit=True):
          shorcut_key = st.text_input(label="", value="", placeholder="Mot clé ")
          shortcut_letter = st.text_input(label="", value="", placeholder="Lettre associée")
          submit_button = st.form_submit_button("Créer")
          st.warning("Seulement une seule lettre est acceptée et n'utilisez pas deux fois la même lettre.")

          if submit_button:
               with conn.session as s:
                   query = text(f"INSERT INTO table_shortcut_{user_id} (shortcut_key, shortcut_letter) VALUES ('{shorcut_key}', '{shortcut_letter}')")
                   s.execute(query, {"shortcut_key": shorcut_key, "shortcut_letter": shortcut_letter})
                   st.success("Votre raccourci a été créé !")
=======
    user_email = st.session_state['useremail']

    def get_worksheet():
        try:
            main_sheet = client.open("Database")
            worksheet = main_sheet.worksheet(f"Shortcut_{user_email}")
            return worksheet
        except gspread.exceptions.WorksheetNotFound:
            st.error("La feuille de calcul n'existe pas.")
            return None

    if selected_options == "Voir mes raccourcis":
        worksheet = get_worksheet()
        if worksheet:
            shortcuts = worksheet.get_all_records()
            st.dataframe(shortcuts, width=800)
            if not shortcuts:
                st.warning("Vous n'avez aucun raccourci pour l'instant. Créez votre premier raccourci dans l'opération 'Créer un raccourci'.")

    elif selected_options == "Supprimer un raccourci":
        worksheet = get_worksheet()
        if worksheet:
            shortcut_id = st.number_input("Entrer l'index du raccourci", min_value=2)
            st.warning("L'index du raccourci se trouve sur la colonne de gauche dans l'opération 'Voir mes raccourcis'. ")
            if st.button("Supprimer"):
                # Récupérez toutes les valeurs dans la colonne "index_shortcut"
                index_shortcut = worksheet.col_values(1)

                # Recherchez l'index dans la liste des "index_shortcut"
                try:
                    row_to_delete = index_shortcut.index(str(shortcut_id)) + 1
                except ValueError:
                    st.warning("L'index spécifié n'existe pas.")
                    
                worksheet.delete_rows(row_to_delete)
                st.success("Votre raccourci a été supprimé")

    elif selected_options == "Modifier un raccourci":
        worksheet = get_worksheet()
        if worksheet:
            shortcut_id = st.number_input("Entrer l'ID du raccourci", min_value=2)
            st.warning("L'index du raccourci se trouve sur la colonne tout à gauche dans l'opération 'Voir mes raccourcis'. ")
            with st.form("modify_shortcut_form", clear_on_submit=True):
                new_shorcut_key = st.text_input(label="", value="", placeholder="Entrer le nouveau mot clé ")
                new_shorcut_letter = st.text_input(label="", value="", placeholder="Entrer la nouvelle lettre associée")
                submit_button = st.form_submit_button("Modifier")
            if submit_button:
                worksheet.update(f"B{shortcut_id}", new_shorcut_key)
                worksheet.update(f"C{shortcut_id}", new_shorcut_letter)
                st.success("Votre raccourci a été modifié")

    elif selected_options == "Créer un raccourci":
        worksheet = get_worksheet()
        if worksheet:
            with st.form("create_shortcut_form", clear_on_submit=True):
                shortcut_key = st.text_input(label="", value="", placeholder="Mot clé ")
                shortcut_letter = st.text_input(label="", value="", placeholder="Lettre associée")
                submit_button = st.form_submit_button("Créer")
                st.warning("Seulement une seule lettre est acceptée et n'utilisez pas deux fois la même lettre.")

                if submit_button:
                    # Obtenez le nombre de lignes actuel dans la feuille de calcul
                    current_rows = len(worksheet.get_all_values())

                    # Calculez la nouvelle valeur pour "index_shortcut"
                    index_shortcut = current_rows + 1

                    # Ajoutez une nouvelle ligne avec "=ROW()" pour "index_shortcut"
                    worksheet.append_row([index_shortcut, shortcut_key, shortcut_letter])
                    
                    st.success("Votre raccourci a été créé !")
>>>>>>> 3441968 (Premier commit)
