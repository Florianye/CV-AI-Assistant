import dotenv
import os
import settings
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import tiktoken
import streamlit as st

# Initialization function: sets up the bot by loading documents, creating embeddings, and configuring the QA system.
def initialize_bot():
    dotenv.load_dotenv(".env", override=True)
    # Load PDF documents from the specified directory.
    loader = DirectoryLoader('./pdf/', glob="**/*.pdf", loader_cls=PyPDFLoader)
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
        chunk_size=250, chunk_overlap=10, length_function=tiktoken_len,
        separators=["\n\n", "\n", " ", ""]
    )

    data = text_splitter.split_documents(doc)

    # Create embeddings for the document chunks.
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])

    # Create a Chroma store from the document chunks and embeddings.
    store = Chroma.from_documents(
        data, embeddings, 
        ids=[f"{item.metadata['source']}-{index}" for index, item in enumerate(data)],
        collection_name="CV-Embeddings", persist_directory='db'
    )
    store.persist()

    # Define a template for the QA system's prompts.
    template = """You are an AI assistant equipped with up-to-date details from your creator's CV. The information you have are not your skills and can not provide assistance.
                I provide accurate and positive responses to recruiters' inquiries for given information about the creator. For questions in German, I respond in German.
                If you don't know the answer, simply state that you don't know and are happy to answer further questions.
    {context}
    Question: {question}"""

    PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])

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

    user_input = st.text_input("Ask a question about the CV:", "")
    with st.chat_message("user"):
        st.write(user_input)




    # if user_input:
    #     response = interact_with_bot(qa_with_source, user_input)
    #     st.text_area("Response:", response, height=200)




    # prompt = st.chat_input("Say something")
    # if prompt:
    #     st.write(f"User has sent the following prompt: {prompt}")

        

if __name__ == "__main__":
    main()