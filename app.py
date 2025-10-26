import os
import pandas as pd
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
import time

# Importar herramientas
from tools.registrar_reembolso import registrar_reembolso
from tools.consultar_estado import consultar_estado
from tools.actualizar_solicitud import actualizar_solicitud

# --- CONFIGURACIÓN DE PÁGINA Y LLM ---
st.set_page_config(page_title="Agente de Reembolsos Médicos", layout="wide")

# Leer clave API desde archivo
with open("clave_api.txt") as f:
    os.environ["OPENAI_API_KEY"] = f.read().strip()

# Iniciar modelo y memoria
@st.cache_resource
def setup_agent_llm():
    """Configura el modelo LLM y el checkpointer para el agente."""
    model = ChatOpenAI(model="gpt-4o-mini")
    memory = MemorySaver()
    return model, memory

model, memory = setup_agent_llm()

# --- FUNCIONES DE AGENTE ---

def create_agent_for_role(rol):
    """Crea el agente de LangGraph con el conjunto de herramientas apropiado según el rol."""
    
    # Capturamos el usuario
    usuario_logueado = st.session_state.get('username', 'Usuario Desconocido')
    
    if rol == "Administrador":
        toolkit = [registrar_reembolso, consultar_estado, actualizar_solicitud]
        st.session_state.rol_info = "🩺 Usuario **Administrador** (Acceso total)"
        prompt_instruccion = (
            f"El usuario logueado es **{usuario_logueado}** y tiene acceso total. "
            "Cuando uses la herramienta 'consultar_estado', **NO incluyas el argumento 'nombre_asegurado'** en la llamada. "
            f"Para la herramienta 'registrar_reembolso', utiliza **{usuario_logueado}** automáticamente para el argumento 'nombre_asegurado'."
        )
    elif rol == "General":
        toolkit = [registrar_reembolso, consultar_estado]
        st.session_state.rol_info = "👤 Usuario **General** (Solo registro y consulta)"
        prompt_instruccion = (
            f"El usuario logueado es **{usuario_logueado}**. "
            f"Para las herramientas 'registrar_reembolso' y 'consultar_estado', utiliza **'{usuario_logueado}'** automáticamente para el argumento 'nombre_asegurado'. "
            "Solo puedes consultar solicitudes asociadas a tu nombre."
        )
    else:
        toolkit = [] # Sin herramientas para otros roles
        st.session_state.rol_info = "⚠️ Rol desconocido."

    prompt = ChatPromptTemplate.from_messages([
        ("system", 
         f"Eres un asistente de soporte para reembolsos médicos. {prompt_instruccion} "
         "Si el usuario menciona un 'Beneficiario', úsalo para el argumento 'nombre_beneficiario'. "
         "Céntrate siempre en responder únicamente a la última pregunta del usuario. NO repitas ni resumas acciones o confirmaciones de solicitudes ya procesadas en turnos anteriores de la conversación si es que el usuario no te las pide."
         "Usa las herramientas disponibles solo cuando sea necesario y sé cortés."),
        ("human", "{messages}")
    ])

    agent_instance = create_react_agent(model, toolkit, checkpointer=memory, prompt=prompt)
    return agent_instance

# --- VISTAS DE STREAMLIT ---

def login_view():
    """Muestra el formulario de login y maneja la autenticación."""
    st.title("Sistema de Reembolsos Médicos")
    st.header("Inicio de Sesión")

    if st.session_state.login_attempt_successful:
        st.info("Iniciando sesión...")
        return

    # Cargar csv de usuarios
    df_users = pd.read_csv("dataUsuarios.csv")

    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit_button = st.form_submit_button("Ingresar")

        if submit_button:
            # Buscar credenciales
            user_data = df_users[(df_users['Usuario'] == username) & (df_users['Contrasena'] == password)]

            if not user_data.empty:
                # Éxito: Guardar estado y cambiar a la vista de chat
                user_row = user_data.iloc[0]
                st.session_state.logged_in = True
                st.session_state.username = user_row['Nombres'] + " " + user_row['ApellidoPaterno'] + " " + user_row['ApellidoMaterno']
                st.session_state.user_role = user_row['TipoUsuario']
                #st.success(f"Bienvenido(a), {user_row['Nombres']}. Rol: {user_row['TipoUsuario']}")
                
                # Crear el agente para la sesión y el rol
                st.session_state.agent = create_agent_for_role(st.session_state.user_role)
                st.session_state.login_attempt_successful = True
                st.rerun()
                return
            else:
                st.error("Usuario o contraseña incorrectos.")

def chat_view():
    """Muestra la interfaz de chat con el agente."""
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        # Limpieza de la sesión
        if 'messages' in st.session_state:
            del st.session_state.messages
        if 'agent' in st.session_state:
            del st.session_state.agent
        if 'user_role' in st.session_state:
            del st.session_state.user_role
            
        st.success("Finalizando sesión...")
        time.sleep(1.5)
        st.rerun()

    st.sidebar.markdown(st.session_state.rol_info)

    st.title(f"🩺 Agente de Soporte de Reembolsos")
    
    # Iniciar historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Mensaje de bienvenida del agente
        st.session_state.messages.append({"role": "assistant", "content": "¡Hola! Soy tu agente de reembolsos. ¿En qué puedo ayudarte hoy?"})

    # Mostrar mensajes anteriores
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada de usuario
    if user_input := st.chat_input("Pregunta al agente"):
        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Invocar al agente
        with st.spinner("Pensando en la respuesta..."):
            
            # La configuración de la sesión
            config = {"configurable": {"thread_id": "session_xxx15"}} 

            # Prepara el historial de mensajes para el agente
            langchain_messages = [HumanMessage(content=user_input)]
            
            try:
                respuesta = st.session_state.agent.invoke(
                    {"messages": langchain_messages},
                    config=config
                )
                
                # Respuesta del agente
                output = respuesta["messages"][-1].content
                
            except Exception as e:
                output = f"⚠️ Ocurrió un error al ejecutar el agente: {e}"
                
        # Mostrar respuesta del agente
        with st.chat_message("assistant"):
            st.markdown(output)
        st.session_state.messages.append({"role": "assistant", "content": output})


def logout():
    """Maneja el cierre de sesión."""
    st.session_state.logged_in = False
    del st.session_state.messages
    del st.session_state.agent
    st.success("Sesión finalizada con éxito.")
    time.sleep(1.5)
    st.rerun()

# --- LÓGICA PRINCIPAL ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "loggin_attempt_successful" not in st.session_state:
    st.session_state.login_attempt_successful = False
if st.session_state.logged_in:
    chat_view()
else:
    login_view()