# Main execution block for Streamlit app
import streamlit as st
from ai_assistant import initialize_bot, interact_with_bot
from gs_db import init_gs_conn, update_gs
from datetime import datetime
import random

# Initialize a welcome message from the AI assistant
start_message = "Hi, my name is Proficia. I am Florian's AI Assistant and happy to answer any questions you may have about his professional and educational background!"
# Check if the 'messages' list exists in the session state, if not, initialize it with the start message
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": start_message}]

# Display the chat history or clear it based on user actions
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function to clear the chat history, resetting it to just the start message
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": start_message}]
# Add a button in the sidebar to clear the chat history
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)
st.sidebar.markdown("---")
# Sidebar welcome message
st.sidebar.header("Florian Ye")
st.sidebar.write("""Hello and welcome! Feel free to chat here with my AI assistant, Proficia, who is on hand to share insights about my professional and educational journey.
                 Proficia will do her best to answer your questions accurately and helpfully!""")
st.sidebar.markdown("---")
st.sidebar.write("You can reach out to me through the following channels:")
st.sidebar.write("E-Mail: florian-ye@hotmail.com")
st.sidebar.write("LinkedIn: https://www.linkedin.com/in/florianye")

# Dictionary to store the current chat message details
chat_history_row = {}

# User-provided prompt
prompt = st.chat_input()
if prompt:
    # Append user's message to the session state for display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

        # Record the current date and time, and the user's question, in the chat history dictionary
        datetime_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        chat_history_row["datetime"] = datetime_now # Save in dict
        chat_history_row["question"] = prompt.replace("'", "") # Save in dict

#st.write(st.session_state.messages)
loading_messages = [
    "Processing request...",
    "Thinking...",
    "Crunching numbers...",
    "Analyzing..",
    "Compiling results..."]
loading_message = random.choice(loading_messages)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner(loading_message):
            response = interact_with_bot(prompt) # Get response from the AI assistant
            chat_history_row["answer"] = response.replace("'", "") # Save in dict
            # Save chat_history_row as row in gs
            try:
                update_gs(chat_history_row)
            except:
                pass
            st.write(response)
    # Append the assistant's response to the session state for display
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)


    



