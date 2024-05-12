import streamlit as st
import json
from st_login_form import login_form
from supabase import create_client, Client

# Configurações do Supabase para login/cadastro
USER_PROJECT_URL = st.secrets["USER_PROJECT_URL"]
USER_PROJECT_KEY = st.secrets["USER_PROJECT_KEY"]
USER_TABLE = "users"

# Configurações do Supabase para o dashboard
DATA_PROJECT_URL = st.secrets["DATA_PROJECT_URL"]
DATA_PROJECT_KEY = st.secrets["DATA_PROJECT_KEY"]
DATA_TABLE = "alura_gemini"

# Função para conectar ao Supabase
def connect_to_supabase(url, key) -> Client:
    """Conecta ao Supabase e retorna o cliente."""
    supabase = create_client(url, key)
    return supabase

# Função para carregar os dados do Supabase e retornar como JSON
@st.cache_data(ttl=60)  # Cache dos dados por 60 segundos
def load_data(supabase: Client, table: str) -> str:
    """Carrega os dados da tabela especificada e retorna como JSON."""
    data = supabase.table(table).select("*").execute()
    return json.dumps(data.data)

# Tela de Login/Cadastro
def login_page():
    st.title("Login/Cadastro")
    user, authenticated = login_form(USER_PROJECT_URL, USER_PROJECT_KEY, USER_TABLE)
    if authenticated:
        st.session_state.user = user
        st.success("Logado com sucesso!")
        st.experimental_rerun()
    else:
        st.warning("Usuário não autenticado.")

# Tela do Dashboard
def dashboard_page():
    st.title("Dashboard Alura Gemini")

    # Conexão com o Supabase
    supabase = connect_to_supabase(DATA_PROJECT_URL, DATA_PROJECT_KEY)

    # Carregar os dados da tabela como JSON
    data_json = load_data(supabase, DATA_TABLE)
    dados = json.loads(data_json)

    # Configuração da galeria com 2 colunas e 4 linhas
    cols = st.columns(2)
    current_page = st.number_input("Página:", min_value=1, max_value=(len(dados) // 8) + 1, value=1, step=1)
    start_index = (current_page - 1) * 8
    end_index = start_index + 8

    # Loop pelos dados para criar os minicards
    for i, item in enumerate(dados[start_index:end_index]):
        with cols[i % 2]:
            with st.container():
                st.markdown(f"**{item['nome']}**")
                st.markdown(f"{item['reacoes']} reações")
                st.markdown(f"Postado em: {item['data']}")
                if st.button(f"Ver projeto - {item['nome']}"):
                    st.session_state.selected_link = item['link']

    # Área principal para exibir o iframe
    if 'selected_link' in st.session_state:
        st.markdown("---")
        st.subheader("Projeto selecionado:")
        st.components.v1.iframe(st.session_state.selected_link, height=600, scrolling=True)

# Configuração da multipage
PAGES = {
    "Login/Cadastro": login_page,
    "Dashboard": dashboard_page
}

# Seleção da página
st.sidebar.title("Navegação")
selection = st.sidebar.radio("Ir para", list(PAGES.keys()))

# Execução da página selecionada
page = PAGES[selection]

# Verificação de login e permissão (mantém a mesma lógica)
if 'user' in st.session_state:
    if st.session_state.user['role'] == 'admin':
        page()
    else:
        st.error("Você precisa ser um administrador para acessar o dashboard.")
else:
    page()
