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

# Global variable to hold the QA system once initialized
qa_with_source = None
# Initialization function: sets up the bot by loading documents, creating embeddings, and configuring the QA system.
def initialize_bot(OPENAI_API_KEY=None):
    global qa_with_source  # Use the global variable to store the initialized QA system

    if OPENAI_API_KEY == None:
        dotenv.load_dotenv(".env", override=True)
    else:
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    
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

    #return qa_with_source

# Function to interact with the bot: takes user input and generates responses.
def interact_with_bot(user_input):
    global qa_with_source

    if qa_with_source is None:
        initialize_bot()
        
    response = qa_with_source.invoke(user_input)
    return response["result"]