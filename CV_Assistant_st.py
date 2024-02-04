import dotenv
import os
import settings
from langchain_community.document_loaders import DirectoryLoader, TextLoader #,PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import tiktoken
import streamlit as st
from datetime import datetime

# Initialization function: sets up the bot by loading documents, creating embeddings, and configuring the QA system.
def initialize_bot():
    dotenv.load_dotenv(".env", override=True)
    # Load PDF documents from the specified directory.
    loader = DirectoryLoader('./txt/', glob="**/*.txt", loader_cls=TextLoader)
    doc = loader.load()

    # Select the GPT model and initialize the tokenizer for that model.
    gpt_model = "gpt-3.5-turbo-1106"
    tokenizer_name = tiktoken.encoding_for_model(gpt_model)
    tokenizer = tiktoken.get_encoding(tokenizer_name.name)

    # Define a function to calculate the token length of a text.
    def tiktoken_len(text):
        tokens = tokenizer.encode(text, disallowed_special=())
        return len(tokens)

    # Split the loaded documents into smaller chunks.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, chunk_overlap=20, length_function=tiktoken_len,
        separators=["\n\n", "\n", " ", ""]
    )

    data = text_splitter.split_documents(doc)

    # Create embeddings for the document chunks.
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])

    # Create a Chroma store from the document chunks and embeddings.
    store = Chroma.from_documents(
        data, embeddings, 
        ids=[f"{item.metadata['source']}-{index}" for index, item in enumerate(data)],
        collection_name="resume-embedding", persist_directory='db'
    )
    store.persist()
    

    # Define a template for the QA system's prompts.
    todays_date = f"Today's date is {datetime.now().date()}."
    template = """You are an highly intelligent AI assistant equipped with up-to-date details from your creator's CV. The information you have are not your skills and can not provide assistance.
                You provide accurate and positive responses to recruiters' inquiries for given information about the creator. When you refer to the creater, always refer him as "he" or his name.
                For questions in German, you respond in German. If you don't know the answer, simply state that you don't know and are happy to answer further questions.
    {context}
    Question: {question}"""

    PROMPT = PromptTemplate(template=todays_date+template, input_variables=["context", "question"])

    # Initialize the ChatGPT language model.
    llm = ChatOpenAI(temperature=0, model=gpt_model, openai_api_key=os.environ["OPENAI_API_KEY"])

    # Set up the QA system with the language model and the Chroma store as the retriever.
    qa_with_source = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=store.as_retriever(),
        chain_type_kwargs={"prompt": PROMPT}, return_source_documents=True
    )

    return qa_with_source

# Function to interact with the bot: takes user input and generates responses.
def interact_with_bot(qa_with_source, user_input):
    response = qa_with_source.invoke(user_input)
    return response["result"]

# Main execution block for Streamlit app
def main():
    st.title("CV Chatbot")
    st.write("Ask questions about the CV and get answers from the chatbot.")

    qa_with_source = initialize_bot()

    # Store LLM generated responses
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
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
                response = interact_with_bot(qa_with_source, prompt)
                st.write(response)
        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)        

if __name__ == "__main__":
    main()