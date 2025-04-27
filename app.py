import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
from crewai import Crew, Agent
import os
import json

# Load Firebase credentials from environment variable
firebase_key = os.getenv('FIREBASE_KEY_JSON')

if not firebase_admin._apps:
    cred = credentials.Certificate(json.loads(firebase_key))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Streamlit app
st.title("CrewAI Chat App")

user_message = st.text_input("Write your message:")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.button("Send"):
    if user_message:
        # Add user's message
        st.session_state.chat_history.append(
            {"sender": "User", "message": user_message})

        # CrewAI agent setup
        agent = Agent(name="Responder",
                      role="Reply to user queries intelligently")
        crew = Crew(agents=[agent])
        response = crew.run(task=user_message)

        # Add agent's response
        st.session_state.chat_history.append(
            {"sender": "Agent", "message": response})

        # Save both messages to Firestore
        message_id = str(uuid.uuid4())
        db.collection('messages').document(message_id).set({
            'user_message': user_message,
            'agent_response': response
        })

# Display conversation
st.subheader("Conversation:")
for msg in st.session_state.chat_history:
    st.write(f"**{msg['sender']}**: {msg['message']}")
