import os
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
#from langchain.agents import AgentType
#from langchain.agents import load_tools
#from langchain.agents import initialize_agent
from groq import Groq, DefaultHttpxClient
from environs import Env
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from httpx import Client

# Inicializar environs
#env = Env()
#env.read_env()  # Ler o arquivo .env no diretório raiz do projeto

# Verificar se a variável de ambiente está carregada
#groq_api_key = st.secrets["GROQ_API_KEY"]
DATABASE_URL = st.secrets["DATABASE_URL"]

#if not groq_api_key:
#    raise ValueError("GROQ_API_KEY environment variable not set.")

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"],
)

engine = sqlalchemy.create_engine(DATABASE_URL, pool_size=5, max_overflow=10)

try:
    with engine.connect() as connection:
        # Executando uma consulta simples
        result = connection.execute(text("SELECT 1"))
        # Verificando o resultado
        if result.scalar() == 1:
            print("Conexão com o banco de dados bem-sucedida!")
        else:
            print("Falha na consulta ao banco de dados.")
except OperationalError as e:
    print(f"Erro ao conectar ao banco de dados: {e}")

# Configuração do prompt e do modelo
system = "You are a helpful assistant."
human = "{text}"
prompt = ChatPromptTemplate.from_messages([("system", "Você é o assistente de um gestor de produção na indústria que conhece dados de controle de estoque e produção"), ("human", human)])
chat = ChatGroq(temperature=0, model_name="llama3-8b-8192")
chain = prompt | chat

def container_chat(streamlit_visual):
   # messages = st.container(height=800)
   # prompt_input = st.chat_input("Pergunte algo ao assistente!")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Exibe mensagens do histórico
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Caixa de entrada para o usuário
    if user_input := st.chat_input("Como posso te ajudar hoje?"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Adiciona um container para a resposta do modelo
        response_stream = chain.stream({"text": user_input})
        full_response = ""

        response_container = st.chat_message("assistant")
        response_text = response_container.empty()

        for partial_response in response_stream:
            full_response += str(partial_response.content)
            response_text.markdown(full_response + "▌")

        # Salva a resposta completa no histórico
        st.session_state.messages.append({"role": "assistant", "content": full_response})

def streamlit_visual():
    st.set_page_config(page_title="Chatbot", layout="wide")
    st.title("AI Chat Bot :robot_face:")
    st.write("Como posso te ajudar hoje? Exemplo: Como posso deixar a minha produção mais eficiente?")

    container_chat(streamlit_visual)

def main():
    streamlit_visual()

if __name__ == "__main__":
    main()
