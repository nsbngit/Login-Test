import streamlit as st
import yaml
from yaml.loader import SafeLoader
import _pages.try_day as try_day
import _pages.home as home

import msal
import requests

CLIENT_ID = st.secrets["client_id"]
AUTHORITY = st.secrets["authority"]
CLIENT_SECRET = st.secrets["client_secret"]
SCOPES = st.secrets["scopes"]
REDIRECT_URI = st.secrets["redirect_uri"]

# MSAL-App initialisieren
app = msal.ConfidentialClientApplication(
    CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
)

# Authentifizierungs-URL generieren
def get_auth_url():
    return app.get_authorization_request_url(SCOPES, redirect_uri=REDIRECT_URI)

# Token abrufen
def get_token_from_code(code):
    result = app.acquire_token_by_authorization_code(
        code,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    return result

def login():
    if 'token' in st.session_state:
        token = st.session_state['token']
        
        # Überprüfe, ob der 'username'-Schlüssel im Token existiert
        username = token.get('username', 'Unbekannter Benutzer')
        
        st.write(f"Willkommen, {username}!")
        
# Handle die Authentifizierung
def handle_auth():
    if "code" in st.query_params:
        code = st.query_params["code"][0]
        token_response = get_token_from_code(code)
        if "access_token" in token_response:
            st.session_state["token"] = token_response
            st.experimental_rerun()

    if "token" not in st.session_state:
        auth_url = get_auth_url()
        st.markdown(f"[Logge dich hier ein]({auth_url})")
    else:
        login()

# Rufe die Authentifizierungsmethoden auf
handle_auth()

# st.set_page_config(page_title="Viessmann Clean & Cold Solutions", page_icon="❄️")
# st.sidebar.image('VCCS.png')

# class index():

#     def __init__(self):
#         try:
#             with open('configdata/st_user_credentials.yaml') as file:
#                 self.config = yaml.load(file, Loader=SafeLoader)
#             self.permission =   self.config['credentials']['user'][st.experimental_user['email']]['permission']

#             self.page_names_to_funcs = {} 
#             self.page_names_to_funcs['Home'] = home.home
#             self.set_authorized_pages()
#             self.selected_page = st.sidebar.selectbox("Select a task", self.page_names_to_funcs.keys())
#             self.page_names_to_funcs[self.selected_page]()
#         except KeyError:
#             print(f"Keine Berechtigung für E-Mail: {st.experimental_user['email']}")
#             # Setzen Sie eine Standardberechtigung oder handhaben Sie den Fehler entsprechend.git push origin --delete login-test

#             self.permission = None

#     def set_authorized_pages(self):
#         if 'admin' in self.permission:
#             self.page_names_to_funcs['tryday'] = try_day.try_day

# index()
