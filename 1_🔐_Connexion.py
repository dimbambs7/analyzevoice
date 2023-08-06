import streamlit as st
import pymysql
from config import DB_CONFIG
import re
import hashlib
import secrets

# Connexion à la base de données MySQL
db = pymysql.connect(**DB_CONFIG)
cursor = db.cursor()

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def validate_password(password):
    # Vérifier la longueur minimale du mot de passe
    if len(password) < 8:
        return False

    # Vérifier la présence d'au moins une lettre majuscule
    if not re.search(r'[A-Z]', password):
        return False

    # Vérifier la présence d'au moins une lettre minuscule
    if not re.search(r'[a-z]', password):
        return False

    # Vérifier la présence d'au moins un chiffre
    if not re.search(r'\d', password):
        return False

    # Vérifier la présence d'au moins un caractère spécial
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False

    return True
def hash_password(password, salt):
    hashed_password = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hashed_password

def create_user(user_name, user_surname, user_mail, user_number, user_club, user_level, user_password, salt):
    salt = secrets.token_hex(16)
    hashed_password = hash_password(user_password, salt)
    query = "INSERT INTO av_users (user_name, user_surname, user_mail, user_number, user_club, user_level, user_password, salt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (user_name, user_surname, user_mail, user_number, user_club, user_level, hashed_password, salt)
    cursor.execute(query, values)
    db.commit()
    return salt

def get_user(user_mail, user_password):
    query = "SELECT * FROM av_users WHERE user_mail = %s AND user_password = %s"
    values = (user_mail, user_password)
    cursor.execute(query, values)
    return cursor.fetchone()

def app():
    st.set_page_config(page_title="Bienvenue", page_icon="👋")
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
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    st.title("Bienvenue sur :blue[AnalyzeVoice]")
    st.write("---")
    
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''

    def login():
        with st.form("login_form", clear_on_submit=True):
            email = st.text_input(label="", value="", placeholder="E-mail")
            password_entry = st.text_input(label="", value="", placeholder="Mot de passe", type="password")
            submit_button = st.form_submit_button("Connexion")

        if submit_button:
            query = "SELECT * FROM av_users WHERE user_mail = %s"
            values = (email,)
            cursor.execute(query, values)
            user = cursor.fetchone()
            
            salt = user['salt']  # Récupérez le sel de la base de données pour cet utilisateur
            hashed_password_entry = hash_password(password_entry, salt=salt)
            user = get_user(email, hashed_password_entry)
            
            if not validate_email(email):
                st.error("Veuillez saisir un email valide")
                return
            if user is None:
                st.error("E-mail ou mot de passe incorrect")
                return
            if user is not None :
                salt = user['salt']
                if hashed_password_entry == user['user_password']:  # Vérifiez avec le mot de passe haché stocké dans la base de données
                    st.success("Connexion réussie")
                    st.session_state.username = user['user_name']
                    st.session_state.useremail = user['user_mail']
                    st.session_state.signedout = True
                    st.session_state.signout = True
                    st.session_state['user_id'] = user['id_user']
                else:
                    st.error('Connexion échouée')

    def signup():
        with st.form("signup_form", clear_on_submit=True):
            user_name = st.text_input(label="", value="", placeholder="Prénom")
            user_surname = st.text_input(label="", value="", placeholder="Nom")
            user_mail = st.text_input(label="", value="", placeholder="E-mail")
            user_number = st.text_input(label="", value="", placeholder="Téléphone")
            user_club = st.text_input(label="", value="", placeholder="Club")
            user_level = st.text_input(label="", value="", placeholder="Niveau de votre équipe")
            user_password = st.text_input(label="", value="", placeholder="Mot de passe", type="password")
            st.warning("Le mot de passe doit contenir au moins 8 caractères, une lettre majuscule, une lettre minuscule, un chiffre et un caractère spécial.")

            submit_button2 = st.form_submit_button("Créer un compte")

        if submit_button2:
            if not validate_email(user_mail):
                st.error("Veuillez saisir un email valide")
                return
            if not validate_password(user_password):
                st.error("Veuillez saisir un mot de passe valide")
                return
            create_user(user_name, user_surname, user_mail, user_number, user_club, user_level, user_password, salt=secrets.token_hex(16))
            cursor.execute('SELECT id_user FROM av_users')
            id_users = cursor.fetchall()
            id = [user['id_user'] for user in id_users]
            nom_table = "table_shortcut_" + str(id[-1])
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {nom_table} (index_shorcut INT AUTO_INCREMENT PRIMARY KEY, shortcut_key CHAR(255), shortcut_letter CHAR(1))")
            st.success("Votre compte a été créé avec succès")

    if 'signedout' not in st.session_state:
        st.session_state.signedout = False
    if 'signout' not in st.session_state:
        st.session_state.signout = False

    if not st.session_state['signedout']:
        choice = st.selectbox("Connexion/S'inscrire", ["Connexion", "S'inscrire"])
        st.write("##")

        if choice == 'Connexion':
            login()
        else:
            signup()

    if st.session_state.signout:
        st.text("Nom : " + st.session_state.username)
        st.text("E-mail : " + st.session_state.useremail)
        if st.button("Déconnexion"):
            st.session_state.signout = False
            st.session_state.signedout = False
            st.session_state.username = ""
    db.close()

if __name__ == "__main__":
    app()