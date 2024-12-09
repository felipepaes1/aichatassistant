import os
import streamlit as st
from groq import Groq
from langchain_groq import ChatGroq
from environs import Env
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

DATABASE_URL = st.secrets["DATABASE_URL"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# Inicializa o cliente da Groq
client = Groq(api_key=GROQ_API_KEY)

# Cria a instância do modelo (ChatGroq)
chat = ChatGroq(
    client=client,
    temperature=0,
    model="llama3-8b-8192"
)

# Definição da mensagem de sistema e prompt
system_message = "Você é o assistente de um gestor de produção na indústria que conhece dados de controle de estoque e produção."
# Montamos o prompt de forma simples: primeiro a mensagem de sistema, depois a pergunta do usuário.
human_prompt_template = system_message + "\n\nUsuário: {text}\nAssistente:"

prompt = PromptTemplate(template=human_prompt_template, input_variables=["text"])
chain = LLMChain(llm=chat, prompt=prompt)

# Testa conexão com o banco
engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10)
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

    # Exibe mensagens anteriores
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada do usuário
    if user_input := st.chat_input("Como posso te ajudar hoje?"):
        # Adiciona mensagem do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Executa a chain para obter resposta do modelo
        response = chain.run(text=user_input)
        # Adiciona resposta ao histórico
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

def streamlit_visual():
    st.set_page_config(page_title="Chatbot", layout="wide")
    st.title("AI Chat Bot :robot_face:")
    st.write("Como posso te ajudar hoje? Exemplo: Como posso deixar a minha produção mais eficiente?")

    container_chat(streamlit_visual)

def main():
    streamlit_visual()

if __name__ == "__main__":
    main()
