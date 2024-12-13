from flask import Flask, request,send_from_directory
from langchain_core.output_parsers import StrOutputParser
from twilio.twiml.messaging_response import MessagingResponse
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

import json
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()
# Initialize Flask app
app = Flask(__name__)

# Set up OpenAI model
llm = ChatOpenAI(model_name="gpt-3.5-turbo",temperature=0.3)

output_parser = StrOutputParser()

def create_documents_from_json(data):
    documents = []
    for entry in data:
        # Concatenate fields into a meaningful document content
        metadata_text = (
            f"{entry['subject']} {entry['type']} - {entry['paper']} "
            f"for the  {entry['year']}, term of ({entry['term']} in {entry['language']})"
        )
        document = Document(page_content=metadata_text, metadata=entry)
        documents.append(document)
    return documents


def load_json_file(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
    return create_documents_from_json(data)

json_file = "./exam_papers_meta_data.json"

docs = load_json_file(json_file)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
LIVE_SERVER_URL = os.getenv('LIVE_SERVER_URL')



# Embed
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
# Create a LangChain LLMChain

template = """
You are an AI assistant that helps users find and download specific exam PDF files by converting their input into the exact file name or giving a relevant response.  

### Key Rules:
1. Your answer must be a single word:  
   - The file path (e.g., '2018/2018-Feb-March-Mathematics-Paper-2-English.pdf').  
   - 'file not found'.  
   - 'greetings' (if the user sends greetings like 'Hi', 'Hello', etc.).  

2. Available Content:  
   - Exam years: 2018–2023 only.  
   - Subjects: Mathematics only.  
   - Languages: Afrikaans and English.  

3. File Naming Rules:  
   - Question paper: `year/term-Mathematics-Paper-paperNumber-language.pdf`.  
   - Memo: `year-term-Mathematics-Memo-paperNumber-Afrikaans-and-English.pdf`.  
   - Maintain the exact filepath structure (e.g., 'Afrikaans-and-English' is not the same as 'English-and-Afrikaans').  

4. Default Options:  
   - If the term is not specified, default to November.  
   - If the year is not specified, default to 2023.  

5. Responding to Greetings:  
   - Input: 'Hi', 'Hello', 'Good morning', etc.  
   - Output: 'greetings'.  

6. Required: Choose the closest match from the file list provided in , `{context}`.  

Examples:  
Input: 'please download maths paper 2 march english'  
Output: '2018/2018-Feb-March-Mathematics-Paper-2-English.pdf'  

Input: 'maths paper 1'  
Output: '2022/2022-November-Mathematics-Paper-1-English.pdf'  

Input: 'memo for maths paper 1 2021'  
Output: '2021-November-Mathematics-Memo-Paper-1-Afrikaans-and-English.pdf'  

### Context:  
The available files are listed in `{context}`.  

Now, respond to this user input:  
{user_input}  
"""

greeting_message = (
    "Hi there! 😊 I'm Neli, your friendly learning companion on WhatsApp, here to help you achieve your best in school. "
    "I specialize in providing downloadable math question papers and memos from 2018 to 2023 to make your exam prep a breeze. "
    "Exciting upcoming features may include syllabus overviews, interactive quizzes, competitions, and so much more. "
    "Stay motivated, and let's ace those exams together! 🌟"
)

def retrieve_and_generate(query):
    # Retrieve relevant documents
    docs = retriever.get_relevant_documents(query)
    
    # Generate a response based on the retrieved content
    response = "\n".join([f"{doc.page_content}\nPath: {doc.metadata['path']}" for doc in docs])
    return response

prompt = ChatPromptTemplate.from_template(template)

chain = prompt | llm | output_parser

# Simple route: Home page
@app.route('/')
def home():
    return "Welcome to EduElevators!"

# Route: Handle POST requests with JSON data
@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.form.get('Body').strip() 
    sender = request.form.get('From') 

    print(f"Message from {sender}: {incoming_msg}")

    context = retrieve_and_generate(incoming_msg)
 
    response = MessagingResponse()
    msg = response.message()

    answer = chain.invoke({"user_input":incoming_msg,"context":context})
    print(f"answer {answer}")
    cleaned_answer = answer.replace("'", "").replace('"', "").strip()

    if "file not found" in cleaned_answer:
        msg.body("Sorry, I couldn't find the requested paper. Please try specifying the subject, term, paper number, and language.")
    elif "greeting" in cleaned_answer:
        msg.body(greeting_message)
    else:
        msg.body(f"Here is your requested paper 📄: {cleaned_answer}")
        # Construct the correct media URL
        media_url = f"{LIVE_SERVER_URL}/past-exam-papers/{cleaned_answer}"
        print(cleaned_answer)
        print(f"Sending media from: {media_url}")  # Debugging log
        msg.media(media_url)
    return str(response) 

@app.route('/past-exam-papers/<path:filename>')
def serve_paper(filename):
    return send_from_directory('past-exam-papers', filename)

# Run the Flask app
if __name__ == '__main__':
    app.run(port=5000, debug=True)
