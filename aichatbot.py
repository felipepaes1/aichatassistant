import os
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from groq import Groq
from environs import Env
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

DATABASE_URL = st.secrets["DATABASE_URL"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# Inicialize primeiro o cliente Groq sem proxies ou parâmetros extras
client = Groq(api_key=GROQ_API_KEY)

# Agora passe o cliente já configurado para o ChatGroq
# Verifique se ChatGroq precisa de 'model' ou 'model_name'.
# Pela documentação do Groq, usamos 'model'. Caso dê erro, tente 'model_name'.
chat = ChatGroq(
    client=client,
    temperature=0,
    model="llama3-8b-8192"
)

system_message = "Você é o assistente de um gestor de produção na indústria que conhece dados de controle de estoque e produção"
prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("user", "{text}")
])

chain = prompt | chat

# Teste de conexão com o banco
engine = sqlalchemy.create_engine(DATABASE_URL, pool_size=5, max_overflow=10)
try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        if result.scalar() == 1:
            print("Conexão com o banco de dados bem-sucedida!")
        else:
            print("Falha na consulta ao banco de dados.")
except OperationalError as e:
    print(f"Erro ao conectar ao banco de dados: {e}")

def container_chat(streamlit_visual):
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Exibe o histórico de mensagens
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada do usuário
    if user_input := st.chat_input("Como posso te ajudar hoje?"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        response_stream = chain.stream({"text": user_input})
        full_response = ""

        response_container = st.chat_message("assistant")
        response_text = response_container.empty()

        for partial_response in response_stream:
            full_response += str(partial_response.content)
            response_text.markdown(full_response + "▌")

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
