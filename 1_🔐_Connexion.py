import streamlit as st
import pymysql
import re
import hashlib
import secrets
from sqlalchemy import text

st.set_page_config(page_title="Bienvenue", page_icon="👋")

# Connexion à la base de données MySQL
conn = st.connection('mysql', type='sql')

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
    conn.query(query, values)
    conn.commit()
    return salt

def get_user(user_mail, user_password):
    query = text("SELECT * FROM av_users WHERE user_mail = :user_mail AND user_password = :user_password")
    params = {"user_mail": user_mail, "user_password": user_password}

    with conn.session as s:
        result = s.execute(query, params)
        user = result.fetchone()
    
    return user

def app():
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
            with conn.session as s:
                query = text("SELECT * FROM av_users WHERE user_mail = :email")
                av_users = s.execute(query, {"email": email})
                user = av_users.fetchone()
                #av_users = s.execute("SELECT * FROM av_users WHERE user_mail = :email", {"email": email})
                #user = av_users.fetchone()
            
            salt = user[8]  # Récupérez le sel de la base de données pour cet utilisateur
            hashed_password_entry = hash_password(password_entry, salt=salt)
            user = get_user(email, hashed_password_entry)
            
            if not validate_email(email):
                st.error("Veuillez saisir un email valide")
                return
            if user is None:
                st.error("E-mail ou mot de passe incorrect")
                return
            if user is not None :
                salt = user[8]
                if hashed_password_entry == user[7]:  # Vérifiez avec le mot de passe haché stocké dans la base de données
                    st.success("Connexion réussie")
                    st.session_state.username = user[1]
                    st.session_state.useremail = user[3]
                    st.session_state.signedout = True
                    st.session_state.signout = True
                    st.session_state['user_id'] = user[0]
                else:
                    st.error('Connexion échouée')
####ok ici
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
            resultats = conn.query('SELECT id_user FROM av_users')
            id_users = resultats.fetchall()
            id = [user[0] for user in id_users]
            #id = [user['id_user'] for user in id_users]
            nom_table = "table_shortcut_" + str(id[-1])
            conn.query(f"CREATE TABLE IF NOT EXISTS {nom_table} (index_shorcut INT AUTO_INCREMENT PRIMARY KEY, shortcut_key CHAR(255), shortcut_letter CHAR(1))")
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

if __name__ == "__main__":
    app()