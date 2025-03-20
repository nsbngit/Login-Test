import streamlit as st
import yaml
from yaml.loader import SafeLoader
import _pages.try_day as try_day
import _pages.home as home

import msal
import requests

st.set_page_config(page_title="Viessmann Clean & Cold Solutions", page_icon="❄️")
st.sidebar.image('VCCS.png')

# Konfiguriere die App mit den Werten aus Azure AD
client_id = st.secrets.auth["client_id"]
client_secret = st.secrets.auth["client_secret"]
tenant_id = st.secrets.auth["tenant_id"]
redirect_uri = "http://localhost:8501"  # Stelle sicher, dass dies mit der in Azure AD registrierten URI übereinstimmt

authority = f"https://login.microsoftonline.com/{tenant_id}"
scopes = ["User.Read"]

# MSAL-App initialisieren
app = msal.ConfidentialClientApplication(
    client_id, authority=authority, client_credential=client_secret
)

# Authentifizierungs-URL generieren
def get_auth_url():
    return app.get_authorization_request_url(scopes, redirect_uri=redirect_uri)

# Token abrufen
def get_token_from_code(code):
    result = app.acquire_token_by_authorization_code(
        code,
        scopes=scopes,
        redirect_uri=redirect_uri
    )
    return result

# Streamlit UI für den Login
def login():
    if "token" in st.session_state:
        username = st.session_state["token"]["id_token_claims"]["preferred_username"]
        index()
        st.write("Erfolgreich eingeloggt!")
        st.write(f"Willkommen, {username}!")
        return True
    else:
        return False

# Handle die Authentifizierung
def handle_auth():
    if "code" in st.query_params:
        code = st.query_params["code"]
        token_response = get_token_from_code(code)
        if "access_token" in token_response:
            st.session_state["token"] = token_response
            st.rerun()


    if "token" not in st.session_state:
        auth_url = get_auth_url()
        st.markdown(f"[Logge dich hier ein]({auth_url})")
    else:
        login()

# Rufe die Authentifizierungsmethoden auf

def index():
    try:
        with open('configdata/st_user_credentials.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)
        permission =   config['credentials']['user'][st.session_state['token']["id_token_claims"]["preferred_username"]]['permission']

        page_names_to_funcs = {} 
        page_names_to_funcs['Home'] = home.home
        if 'admin' in permission:
            page_names_to_funcs['tryday'] = try_day.try_day
        
        selected_page = st.sidebar.selectbox("Select a task", page_names_to_funcs.keys())
        page_names_to_funcs[selected_page]()
    except KeyError:
        print(f"Keine Berechtigung für E-Mail: {st.session_state['token']["id_token_claims"]["preferred_username"]}")
        # Setzen Sie eine Standardberechtigung oder handhaben Sie den Fehler entsprechend.git push origin --delete login-test

        permission = None



handle_auth()
