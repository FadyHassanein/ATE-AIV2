from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Get the API key
openai_api_key = os.getenv("OPENAI_API_KEY")

chat_model= ChatOpenAI(
    model="gpt-4.1", 
    temperature=0.0, 
    streaming= True,
    api_key=openai_api_key)
