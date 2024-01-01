import streamlit as st
import re
import hashlib
<<<<<<< HEAD
import secrets
from sqlalchemy import text

st.set_page_config(page_title="Bienvenue", page_icon="👋")

# Connexion à la base de données MySQL
conn = st.connection('mysql', type='sql')
=======
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import secrets

# Utiliser st.secrets pour accéder aux informations sensibles
secrets_dict = st.secrets["connections_gsheets"]

st.set_page_config(page_title="Bienvenue", page_icon="👋")

# Connexion à la base de données GSheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(secrets_dict, scope)
client = gspread.authorize(creds)

#st.set_page_config(page_title="Bienvenue", page_icon="👋")

# Connexion à la base de donnée GSheets

#scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#creds = ServiceAccountCredentials.from_json_keyfile_name('analyzevoice-b1811-d13b8a17b1e3.json', scope)
#client = gspread.authorize(creds)
>>>>>>> 3441968 (Premier commit)

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

<<<<<<< HEAD
def create_user(user_name, user_surname, user_mail, user_number, user_club, user_level, user_password, salt):
    salt = secrets.token_hex(16)
    hashed_password = hash_password(user_password, salt)
    
    with conn.session as s :
        query = text("INSERT INTO av_users (user_name, user_surname, user_mail, user_number, user_club, user_level, user_password, salt) VALUES (:name, :surname, :email, :number, :club, :level, :password, :salt)")
        s.execute(query, {"name": user_name, "surname": user_surname, "email": user_mail, "number": user_number, "club": user_club, "level": user_level, "password": hashed_password, "salt": salt})
    
    return salt

def get_user(user_mail, user_password):
    query = text("SELECT * FROM av_users WHERE user_mail = :user_mail AND user_password = :user_password")
    params = {"user_mail": user_mail, "user_password": user_password}

    with conn.session as s:
        result = s.execute(query, params)
        user = result.fetchone()
    
    return user
=======
def create_user(user_name, user_surname, user_mail, user_number, user_sport, user_club, user_level, user_password, salt):
    
    # Accéder à la feuille de calcul par son nom
    sheet = client.open("Database")
    
    # Générer un sel pour le nouvel utilisateur
    salt = secrets.token_hex(16)

    # Hacher le mot de passe avec le sel
    hashed_password = hash_password(user_password, salt)

    # Accéder à la feuille principale
    main_sheet = sheet.sheet1

    # Insérer le nouvel utilisateur dans la feuille de calcul
    user_data = [user_name, user_surname, user_mail, user_number, user_sport, user_club, user_level, hashed_password, salt]
    main_sheet.insert_row(user_data, index=2)

    # Créer une nouvelle feuille de calcul pour les raccourics de l'utisateur
    new_sheet_title = f"Shortcut_{user_mail}"
    new_sheet = sheet.add_worksheet(title=new_sheet_title, rows=1000, cols=3)
    new_sheet.append_row(["index_shortcut", "shortcut_key", "shortcut_letter"])

    # Retourner le sel (éventuellement pour une utilisation future)
    return salt

def get_user(user_mail, user_password):
    
    # Accéder à la feuille de calcul par son nom
    sheet = client.open("Database").sheet1
    
    all_records = sheet.get_all_records()

    for user_data in all_records:
        if user_data["user_mail"] == user_mail and user_data["user_password"] == hash_password(user_password, user_data["salt"]):
            return user_data
    
    # Retourner None si l'utilisateur n'est pas trouvé
    return None
>>>>>>> 3441968 (Premier commit)

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
<<<<<<< HEAD
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
=======
            if not validate_email(email):
                st.error("Veuillez saisir un email valide")
                return
            
            # Utiliser la connexion à Google Sheets pour obtenir l'utilisateur
            user = get_user(email, password_entry)

            if user:
                st.success("Connexion réussie")
                st.session_state.username = user["user_name"]
                st.session_state.useremail = user["user_mail"]
                st.session_state.signedout = True
                st.session_state.signout = True
                #st.session_state['user_id'] = user["user_id"]
            else:
                st.error("E-mail ou mot de passe incorrect")

>>>>>>> 3441968 (Premier commit)
    def signup():
        with st.form("signup_form", clear_on_submit=True):
            user_name = st.text_input(label="", value="", placeholder="Prénom")
            user_surname = st.text_input(label="", value="", placeholder="Nom")
            user_mail = st.text_input(label="", value="", placeholder="E-mail")
            user_number = st.text_input(label="", value="", placeholder="Téléphone")
<<<<<<< HEAD
=======
            user_sport = st.text_input(label="", value="", placeholder="Votre sport")
>>>>>>> 3441968 (Premier commit)
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
<<<<<<< HEAD
            create_user(user_name, user_surname, user_mail, user_number, user_club, user_level, user_password, salt=secrets.token_hex(16))
            
            with conn.session as s:
                query_select = text('SELECT id_user FROM av_users ORDER BY id_user DESC LIMIT 1')
                result = s.execute(query_select)
                user_id = result.fetchone()[0]
                
                nom_table = f"table_shortcut_{user_id}"

                query_create_table = text(f"CREATE TABLE IF NOT EXISTS {nom_table} (index_shorcut INT AUTO_INCREMENT PRIMARY KEY, shortcut_key CHAR(255), shortcut_letter CHAR(1))")
                s.execute(query_create_table)

            #id_users = result.fetchall()
            #id = [user[0] for user in id_users]
            #id = [user['id_user'] for user in id_users]
            #nom_table = "table_shortcut_" + str(id[-1])
            #conn.query(f"CREATE TABLE IF NOT EXISTS {nom_table} (index_shorcut INT AUTO_INCREMENT PRIMARY KEY, shortcut_key CHAR(255), shortcut_letter CHAR(1))")
=======
            
            # Enregistrer les données dans la feuille de calcul
            create_user(user_name, user_surname, user_mail, user_number, user_sport, user_club, user_level, user_password, salt=secrets.token_hex(16))
>>>>>>> 3441968 (Premier commit)
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