import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.stoggle import stoggle
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_option_menu import option_menu
import hashlib

# Utiliser st.secrets pour accéder aux informations sensibles
secrets_dict = st.secrets["connections_gsheets"]

def hash_password(password, salt):
    hashed_password = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hashed_password


# Connexion à la base de données GSheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(secrets_dict, scope)
client = gspread.authorize(creds)

if not st.session_state['signedout']:
        st.write(":red[Veuillez vous connecter]")
else:
    st.set_page_config(page_title="Paramètres", page_icon="⚙️")
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
    st.title("⚙️ Paramètres")
    st.write("---")
    selected = option_menu(
          menu_title=None,
          options=["Informations", "FAQ", "Contact", "À propos"],
          orientation="horizontal"
    )
    user_email = st.session_state['useremail']

    sheet = client.open("Database")

    if selected == "Informations":
        user_email_column = 3
        user_worksheet = sheet.get_worksheet(0)
        user_info = None

        for row in range(1, user_worksheet.row_count):
            if user_worksheet.cell(row, user_email_column).value == user_email:
                user_info = user_worksheet.row_values(row)
                break

        if user_info:
            st.markdown(f"Prénom : {user_info[0]}")
            st.write(f"Nom : {user_info[1]}")
            st.write(f"Email : {user_info[2]}")
            st.write(f"Votre numéro : {user_info[3]}")
            st.write(f"Votre club : {user_info[5]}")
            st.write(f"Niveau de votre équipe : {user_info[6]}")
            st.write("---")
            options = ["Prénom", "Nom", "Téléphone", "Club", "Mot de passe", "Niveau équipe"]
            selected_options = st.selectbox("Modifier vos informations :", options)
        else:
            st.warning("Utilisateur non trouvé")
        
        if selected_options == "Prénom":
            with st.form("prenom_form", clear_on_submit=True):
                new_name = st.text_input(label="", placeholder="Nouveau prénom")
                submit_button = st.form_submit_button("Modifier")

                if submit_button:
                    user_worksheet.update_cell(user_email, 1, new_name)  # Mise à jour de la colonne correspondante
                    st.success("Le prénom a été modifié avec succès.")
        
        if selected_options == "Nom":
            with st.form("nom_form", clear_on_submit=True):
                new_surname = st.text_input(label="", placeholder="Nouveau nom")
                submit_button = st.form_submit_button("Modifier")
                
                if submit_button:
                    cell = user_worksheet.find(user_email)
                    user_worksheet.update_cell(cell.row, 2, new_surname)  # Mise à jour de la colonne correspondante
                    st.success("Le nom a été modifié avec succès.")

        if selected_options == "Téléphone":
            with st.form("telephone_form", clear_on_submit=True):
                new_number = st.text_input(label="", placeholder="Nouveau numéro de téléphone")
                submit_button = st.form_submit_button("Modifier")
                
                if submit_button:
                    cell = user_worksheet.find(user_email)
                    user_worksheet.update_cell(cell.row, 4, new_number)  # Mise à jour de la colonne correspondante
                    st.success("Le numéro de téléphone a été modifié avec succès.")

        if selected_options == "Club":
            with st.form("club_form", clear_on_submit=True):
                new_club = st.text_input(label="", placeholder="Nouveau club")
                submit_button = st.form_submit_button("Modifier")
                
                if submit_button:
                    cell = user_worksheet.find(user_email)
                    user_worksheet.update_cell(cell.row, 6, new_club)  # Mise à jour de la colonne correspondante
                    st.success("Le club a été modifié avec succès.")

        if selected_options == "Mot de passe":
            with st.form("mot_de_passe_form", clear_on_submit=True):
                password1 = st.text_input(label="", placeholder="Nouveau mot de passe", type="password")
                password2 = st.text_input(label="", placeholder="Confirmer le mot de passe", type="password")
                submit_button = st.form_submit_button("Modifier")
                
                if submit_button:
                    if password1 == '' and password2 == '':
                        st.warning("Veuillez saisir le nouveaux not de passe")
                    elif password1 != password2:
                     st.error("Les mots de passe ne correspondent pas.") 
                    else:
                        cell = user_worksheet.find(user_email)
                        hashed_password = hash_password(password1, user_worksheet.cell(cell.row, 8).value)  # Utilisez la colonne correspondante pour le sel
                        user_worksheet.update_cell(cell.row, 7, hashed_password)  # Mise à jour de la colonne correspondante
                        st.success("Le mot de passe a été modifié avec succès.")

    
        if selected_options == "Niveau équipe":
                with st.form("niv_equipe_form", clear_on_submit=True):
                    new_level = st.text_input(label="", placeholder="Niv. équipe")
                    submit_button = st.form_submit_button("Modifier")
                    
                    if submit_button:
                        cell = user_worksheet.find(user_email)
                        user_worksheet.update_cell(cell.row, 6, new_level)  # Mise à jour de la colonne correspondante
                        st.success("Le niveau de l'équipe a été modifié avec succès.")

        
    elif selected == "FAQ":
          stoggle("Comment combiner AnalyzeVoice avec mon logiciel d'analyse vidéo ?",
                  """<br>Pour combiner AnalyzeVoice avec votre logiciel d'analyse vidéo tel que Dartfish, vous pouvez suivre cette approche en trois étapes :

Étape 1 : Configuration des raccourcis clavier dans votre logiciel d'analyse vidéo
Ouvrez votre logiciel et suivez les instructions pour configurer vos raccourcis clavier personnalisés. Cela vous permettra d'effectuer des actions spécifiques rapidement lors de l'analyse vidéo.

<br>Pour Dartfish : suivez les instructions du lien suivant pour créer un panneau de marquage avec des raccourcis clavier (page 10-11) : https://support.dartfish.tv/en/support/solutions/articles/27000048169-create-a-tagging-panel.

<br>Pour Hudl SportsCode : utilisez ce lien pour configurer vos raccourcis clavier personnalisés : https://www.hudl.com/support/hudl-sportscode/build/button-behavior/create-a-button-hotkey/fr.

<br>Pour LongoMatch : consultez cette ressource pour configurer vos raccourcis clavier : https://fluendo.atlassian.net/wiki/spaces/LPD/pages/9142618/Dashboard+buttons.

<br>Pour NacSport : suivez ce lien pour découvrir des astuces pour améliorer votre productivité avec NacSport : https://www.nacsport.com/blog/en-us/Tips/nacsport-productivity-hacks.


Étape 2 : Ouvrir AnalyzeVoice
Accédez à AnalyzeVoice via votre navigateur Internet. Rendez-vous dans l'onglet "🎙️ Analyze", puis appuyez sur "Start" pour lancer l'analyse de votre voix.

Étape 3 : Démarrer l'analyse vidéo
Une fois AnalyzeVoice activé, ouvrez votre logiciel d'analyse vidéo et lancez la lecture de la vidéo que vous souhaitez analyser en utilisant votre voix. AnalyzeVoice fonctionnera en arrière-plan sur votre ordinateur.

REMARQUE : Assurez-vous d'être sur la fenêtre de votre logiciel d'analyse vidéo, sinon AnalyzeVoice risque de ne pas détecter vos commandes vocales. """)

          st.write("###")
          stoggle(
            "Qu'est-ce qu'AnalyzeVoice et en quoi consiste notre logiciel ?",
            """<br>AnalyzeVoice est une plateforme innovante qui permet aux professionnels du sport d'utiliser leur voix pour exécuter des tâches complexes et accéder aux fonctionnalités avancées des logiciels d'analyse vidéo et de performance sportive. Notre logiciel révolutionnaire offre une interface rapide, intuitive et mains libres pour une analyse vidéo et une amélioration des performances sportives plus accessibles et efficaces.""",
        )
          st.write("##")
          stoggle(
            "Comment fonctionne AnalyzeVoice ?",
            """<br>AnalyzeVoice utilise une technologie de reconnaissance vocale avancée pour comprendre les commandes vocales des utilisateurs. En utilisant des mots-clés et des phrases spécifiques, les utilisateurs peuvent effectuer des actions telles que la navigation dans les vidéos, l'ajout de marqueurs, la création de statistiques, etc. Notre logiciel est conçu pour être facile à utiliser, offrant une expérience fluide et pratique.""",
        )
          st.write("##")
          stoggle("Quels sports sont pris en charge par AnalyzeVoice ?",
                  """<br>AnalyzeVoice est conçu pour être polyvalent et peut être utilisé dans une variété de sports, tels que le football, le basketball, le tennis, le hockey, le rugby, le baseball, etc. Notre logiciel est personnalisable pour répondre aux besoins spécifiques de chaque sport et offre des fonctionnalités adaptées à chaque discipline.""")
          
          st.write("##")
          stoggle("Est-ce que AnalyzeVoice est compatible avec les plateformes mobiles ?",
                  """<br>Non, actuellement AnalyzeVoice n'est pas compatible avec les plateformes mobiles. Notre logiciel est uniquement disponible sur les ordinateurs. Cependant, vous pouvez accéder à AnalyzeVoice à partir de votre ordinateur portable ou de bureau, ce qui vous permet de profiter pleinement de ses fonctionnalités avancées pour l'analyse vidéo et la performance sportive. """
                  )
          
          st.write("##")
          stoggle("Est-ce que AnalyzeVoice enregistre ce que vous dîtes ?",
                  """<br>Non, AnalyzeVoice n'enregistre pas ce que vous dites. Notre logiciel fonctionne en temps réel pour interpréter vos commandes vocales et exécuter les actions correspondantes. Une fois que vos commandes sont traitées, elles ne sont pas stockées ou enregistrées par AnalyzeVoice. Nous respectons votre confidentialité et nous nous engageons à protéger vos données."""
                  )
          
          st.write("##")
          stoggle("Avec quel logiciel AnalyzeVoice est compatible ?",
                  """<br>AnalyzeVoice est compatible avec différents logiciels d'analyse vidéo et de performance sportive, offrant ainsi une grande flexibilité d'utilisation. Voici quelques exemples de logiciels avec lesquels AnalyzeVoice peut être utilisé :

Dartfish, NacSport, Hudl SportsCode, LongoMatch.

Cependant, veuillez noter que la compatibilité précise peut varier en fonction des versions et des configurations spécifiques des logiciels. Il est recommandé de vérifier la compatibilité d'AnalyzeVoice avec votre logiciel spécifique ou de contacter notre équipe d'assistance pour obtenir des informations détaillées sur la compatibilité avec votre logiciel d'analyse vidéo préféré.""")
          
          stoggle("Comment puis-je personnaliser les commandes vocales dans AnalyzeVoice pour répondre à mes besoins spécifiques ?",
                  """Pour personnaliser les commandes vocales dans AnalyzeVoice, suivez ces étapes simples :

Accédez à l'onglet "🚀 Raccourcis" : Dans l'interface d'AnalyzeVoice, recherchez et cliquez sur l'onglet "Raccourcis" pour accéder aux options de personnalisation des commandes vocales.

Choisissez l'opération "Créer un raccourci" : Dans la section des raccourcis, recherchez l'option permettant de créer un nouveau raccourci personnalisé et sélectionnez-la.

Définissez vos propres mots-clés et lettres associées : Lors de la création d'un nouveau raccourci, saisissez les mots-clés ou les expressions spécifiques que vous souhaitez utiliser pour déclencher une action particulière. Vous pouvez également associer une seule lettre à chaque raccourci, en vous assurant d'utiliser la même lettre que celle utilisée dans votre logiciel d'analyse vidéo.

Testez et ajustez : Une fois que vous avez défini vos commandes vocales personnalisées, effectuez des tests pour vous assurer qu'AnalyzeVoice les reconnaît correctement. N'hésitez pas à apporter des ajustements supplémentaires si nécessaire, afin d'améliorer la précision de la reconnaissance.

Veuillez noter que la possibilité de personnaliser les commandes vocales peut varier en fonction du logiciel spécifique que vous utilisez avec AnalyzeVoice. Certains logiciels peuvent accepter toutes les lettres de l'alphabet, les chiffres de 0 à 9, ainsi que d'autres caractères spécifiques. Pour obtenir des instructions précises sur la personnalisation des commandes vocales dans votre environnement, veuillez vous référer à la documentation de votre logiciel d'analyse vidéo.
""")
          
          st.write("##")
          stoggle("Comment AnalyzeVoice garantit-il la sécurité et la confidentialité des données des utilisateurs ?",
                  """<br>Chez AnalyzeVoice, nous accordons une grande importance à la sécurité et à la confidentialité des données de nos utilisateurs. Voici comment nous garantissons la protection de vos données :

Chiffrement des données : Toutes les données que vous transmettez à travers AnalyzeVoice sont chiffrées à l'aide de protocoles de sécurité avancés. Cela garantit que vos informations restent confidentielles et ne peuvent pas être consultées par des tiers non autorisés.

Accès sécurisé : Nous mettons en place des mesures de sécurité strictes pour contrôler l'accès à vos données. Seuls les membres autorisés de notre équipe ont accès aux informations nécessaires pour assurer le bon fonctionnement du service et le support client.

Respect de la vie privée : Nous respectons votre vie privée et nous ne partageons pas vos données personnelles avec des tiers sans votre consentement explicite. Nous utilisons vos informations uniquement dans le but de fournir les services d'AnalyzeVoice et de vous offrir la meilleure expérience possible.

Conformité aux réglementations : Nous nous conformons aux lois et réglementations en vigueur concernant la protection des données personnelles. Nous nous engageons à respecter les normes de confidentialité et à mettre en place des mesures de sécurité appropriées pour prévenir toute violation de données.

Sauvegarde des données : Nous effectuons régulièrement des sauvegardes de vos données pour assurer leur disponibilité continue et pour minimiser tout risque de perte de données.

Nous prenons la sécurité et la confidentialité très au sérieux et nous travaillons en permanence pour maintenir et améliorer nos mesures de protection des données. Si vous avez des préoccupations spécifiques ou des questions supplémentaires concernant la sécurité des données, n'hésitez pas à nous contacter. Votre confiance est essentielle pour nous, et nous ferons tout notre possible pour protéger vos données.""")
          
          stoggle("Quels sont les caractères spécifiques pris en charge par AnalyzeVoice ?",
                  """<br>AnalyzeVoice prend en charge un large éventail de caractères spécifiques pour personnaliser les commandes vocales. Voici quelques exemples de caractères pris en charge par AnalyzeVoice :

Lettres de l'alphabet : AnalyzeVoice accepte les lettres de l'alphabet, que ce soit en majuscules ou en minuscules. Vous pouvez utiliser ces lettres pour créer des commandes vocales personnalisées en fonction de vos besoins.

Chiffres : AnalyzeVoice reconnaît également les chiffres de 0 à 9. Vous pouvez les utiliser dans vos commandes vocales pour effectuer des actions numériques spécifiques, comme marquer des points ou définir des valeurs de mesure.

Caractères spéciaux : Certaines versions d'AnalyzeVoice peuvent également prendre en charge des caractères spéciaux, tels que les symboles de ponctuation (!, ?, &, etc.) ou les caractères spécifiques à une langue particulière.

Il est important de noter que la disponibilité des caractères spécifiques peut varier en fonction des configurations spécifiques de votre logiciel d'analyse vidéo. Veuillez consulter la documentation de votre logiciel d'analyse vidéo ou contacter l'assistance pour obtenir des informations précises sur les caractères pris en charge dans votre cas particulier.

""")
          st.write("---")

          
    
    elif selected == "Contact":
         st.write("""
Hey beta-utilisateur,

Si tu rencontres un problème ou un bug lors de l'utilisation de notre application, n'hésite pas à me contacter par e-mail à l'adresse dimbambuandy7@gmail.com. Nous sommes là pour t'aider et résoudre rapidement tous les problèmes que tu pourrais rencontrer.

Décris-nous en détail le problème que tu rencontres, en fournissant autant d'informations que possible. Cela nous permettra de mieux comprendre la situation et de trouver la meilleure solution pour toi.

Nous nous engageons à traiter toutes les demandes dans les plus brefs délais et à te fournir une assistance de qualité. Ta satisfaction est notre priorité absolue.

Merci pour ta compréhension et ta collaboration. Nous sommes impatients de résoudre tes problèmes et de te offrir une expérience utilisateur exceptionnelle.

Cordialement,
L'équipe de support technique
""")
         st.write("---")
          
    
    elif selected == "À propos":
          st.subheader("Version beta")
          st.write("Qu'est-ce qu'une version bêta ?")
          st.write("Une version bêta est une version d'un logiciel ou d'une application qui est encore en cours de développement et qui est mise à disposition pour les tests et les commentaires des utilisateurs avant sa sortie officielle.")
          st.write("---")
          st.subheader("Hey! Je m'apelle Andy 👋")
          st.write("""Passionné de handball, de sport en général et d'informatique, je suis en quête perpétuelle de nouvelles expériences et de défis pour continuer à grandir tant sur le plan personnel que professionnel.""")
          st.write("[En savoir un peu plus sur moi](https://www.linkedin.com/in/andy-dimbambu/)")
