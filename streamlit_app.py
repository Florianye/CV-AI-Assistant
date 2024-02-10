# Main execution block for Streamlit app
import streamlit as st
from ai_assistant import initialize_bot, interact_with_bot
from gs_db import init_gs_conn, update_gs
from datetime import datetime

st.header("Florian Ye")

# Store LLM generated responses
start_message = "Hi, my name is Proficia. I am Florian's AI Assistant and happy to answer any questions you may have about his professional and educational background!"
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

chat_history_row = {}

# User-provided prompt
prompt = st.chat_input()
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

        # Save date, questions and answers to defined empty list
        datetime_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        chat_history_row["datetime"] = datetime_now # Save in dict
        chat_history_row["question"] = prompt.replace("'", "") # Save in dict

#st.write(st.session_state.messages)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = interact_with_bot(prompt)
            chat_history_row["answer"] = response.replace("'", "") # Save in dict
            # Save chat_history_row as row in gs
            try:
                update_gs(chat_history_row)
            except:
                pass
            st.write(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)


    



