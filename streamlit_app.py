# Main execution block for Streamlit app
import streamlit as st
from ai_assistant import initialize_bot, interact_with_bot

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

# User-provided prompt
prompt = st.chat_input()
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

#st.write(st.session_state.messages)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = interact_with_bot(prompt)
            st.write(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)