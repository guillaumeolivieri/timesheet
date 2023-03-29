import time
import threading
import requests
import streamlit as st
from msal import ConfidentialClientApplication

# Set Microsoft Teams app credentials and the target user's email
client_id = "your_client_id"
client_secret = "your_client_secret"
tenant_id = "your_tenant_id"
target_user_email = "target_user_email@example.com"

# Set the API endpoint
GRAPH_API_BASE = 'https://graph.microsoft.com/v1.0'

# Set up the Microsoft Graph API client
app = ConfidentialClientApplication(
    client_id,
    authority=f"https://login.microsoftonline.com/{tenant_id}",
    client_credential=client_secret,
)

# Request access token for Microsoft Graph API
def get_access_token():
    token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return token["access_token"]

# Get the ID of the target user
def get_user_id(access_token, email):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f"{GRAPH_API_BASE}/users/{email}", headers=headers)
    response.raise_for_status()
    return response.json()["id"]

# Send a chat message to the target user
def send_message_to_user(access_token, user_id, message):
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    data = {
        "message": {
            "content": {
                "contentType": "html",
                "content": message
            }
        }
    }
    response = requests.post(f"{GRAPH_API_BASE}/users/{user_id}/chats/$ref", json=data, headers=headers)
    response.raise_for_status()

# Function to send messages periodically
def send_messages_periodically():
    access_token = get_access_token()
    user_id = get_user_id(access_token, target_user_email)

    while send_messages:
        try:
            send_message_to_user(access_token, user_id, "Numero de PO")
            with st.empty():
                st.write("Message sent")
                time.sleep(3)
                st.write("")
        except Exception as e:
            st.write(f"Error: {e}")
            st.stop()

# Streamlit app
st.title("Teams Auto Messenger")
send_messages = False
send_message_button = st.button("Start Sending Messages")
stop_message_button = st.button("Stop Sending Messages")

if send_message_button:
    send_messages = True
    threading.Thread(target=send_messages_periodically).start()
elif stop_message_button:
    send_messages = False
