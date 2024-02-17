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

    # Load OpenAI API key from environment variables or use the provided one.
    if OPENAI_API_KEY == None:
        dotenv.load_dotenv(".env", override=True)
    else:
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    
    # Load PDF documents from the specified directory
    loader = DirectoryLoader('./txt/', glob="**/*.txt", loader_cls=TextLoader)
    doc = loader.load()

    # Select the GPT model and initialize the tokenizer for that model
    gpt_model = "gpt-3.5-turbo-0125" #"gpt-3.5-turbo-1106"
    tokenizer_name = tiktoken.encoding_for_model(gpt_model)
    tokenizer = tiktoken.get_encoding(tokenizer_name.name)

    # Define a function to calculate the token length of a text.
    def tiktoken_len(text):
        tokens = tokenizer.encode(text, disallowed_special=())
        return len(tokens)

    # Split the loaded documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, chunk_overlap=20, length_function=tiktoken_len,
        separators=["\n\n", "\n", " ", ""]
    )
    data = text_splitter.split_documents(doc)

    # Create embeddings for the document chunks
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])

    # Create a Chroma store from the document chunks and embeddings
    store = Chroma.from_documents(
        data, embeddings, 
        ids=[f"{item.metadata['source']}-{index}" for index, item in enumerate(data)],
        collection_name="resume-embedding", persist_directory='db'
    )
    store.persist()

    # Prepare a prompt template with dynamic content including today's date.
    todays_date = f"Today's date is {datetime.now().date()}."
    template =  """As an AI assistant with up-to-date knowledge from Florian's CV, I'm here to share insights into his education and professional life.
                I respond based on Florian's CV details, and for questions in German, I'll reply in German for accuracy.
                If a question goes beyond my knowledge or Florian's CV, I'll aim to redirect our focus to what I can discuss or offer guidance on where to find answers.
                My aim is to provide a helpful dialogue and clarify Florian's career aspects.
                For queries unrelated to Florian's background, I'll kindly suggest reframing the question to align with the information Florian has chosen to share.
                This keeps our conversation focused and informative.
    {context}
    Question: {question}"""

    PROMPT = PromptTemplate(template=todays_date+template, input_variables=["context", "question"])

    # Initialize the ChatGPT language model
    llm = ChatOpenAI(temperature=0, model=gpt_model, openai_api_key=os.environ["OPENAI_API_KEY"])

    # Set up the QA system with the language model and the Chroma store as the retriever
    qa_with_source = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=store.as_retriever(),
        chain_type_kwargs={"prompt": PROMPT}, return_source_documents=True
    )

# Function to interact with the bot: takes user input and generates responses.
def interact_with_bot(user_input):
    global qa_with_source

    # Initialize the bot with an API key if it hasn't been initialized already
    if qa_with_source is None:
        initialize_bot(st.secrets["OPENAI_API_KEY"])
    
    # Invoke the QA system with the user input and return the generated response
    response = qa_with_source.invoke(user_input)
    return response["result"]