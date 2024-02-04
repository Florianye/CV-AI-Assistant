# Main execution block for Streamlit app
import streamlit as st
from ai_assistant import initialize_bot, interact_with_bot
import csv
from datetime import datetime

st.title("Florian Ye's AI Assistant")
#qa_with_source = initialize_bot()

# Store LLM generated responses
start_message = "Hi, I'm happy to answer any questions you may have about Florian's professional and educational background!"
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": start_message}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": start_message}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)
st.sidebar.write("""Please frame your questions clearly since my assistant starts fresh with every interaction and doesn't recall past exchanges. 
                 A bit more detail can go a long way in helping us help you. Thanks for your understanding and happy chatting!""")

chat_history_row = []

# User-provided prompt
prompt = st.chat_input()
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

        # Save date, questions and answers to defined empty list
        datetime_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        chat_history_row.append(datetime_now)
        chat_history_row.append(prompt)

#st.write(st.session_state.messages)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = interact_with_bot(prompt)
            st.write(response)
            chat_history_row.append(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)

# Save chat_history_row as row in chat_history.csv
with open('chat_history/chat_history.csv', 'a', newline='') as file:
    csvwriter = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL) # Create a writer object
    csvwriter.writerow(chat_history_row) # Write the new row