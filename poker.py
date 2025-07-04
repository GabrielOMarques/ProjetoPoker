import pandas as pd
import streamlit as st
import time
from datetime import datetime
import subprocess
import socket
import webbrowser
import threading
import os
import sys  

class datas:
   def __init__(self, hoje=None, dia=None, semana=None, mes=None, ano=None):
        self.hoje = hoje
        self.dia = dia
        self.semana = semana
        self.mes = mes
        self.ano = ano

   def set_datas(self):
        agora = datetime.now()
        self.hoje = agora.strftime("%d/%m/%Y")
        self.dia = agora.date()  # Guarda um objeto date ao invés de string
        self.semana = agora.isocalendar().week
        self.mes = agora.strftime("%m")
        self.ano = agora.strftime("%Y")

class filtros:
    def __init__(self, data=None, plataforma=None, tipo=None):
        self.data = data
        self.plataforma = plataforma
        self.tipo = tipo

    def selecionar_filtros(self):
        self.data = st.selectbox("Qual o Filtro?",
                                   ["Dia", "Semana", "Mês", "Ano"],
                                   index=None,
                                   placeholder="Escolha uma Opção"
                                   )
        
        self.plataforma = st.selectbox(
            "Qual a plataforma?",
            sheets_existentes,
            index=None,
            placeholder="Plataforma"
            )
        
        self.tipo = st.selectbox(
            "Escolha uma opção:",
            [ "Buy in", "Saldo"],
            index=None,
            placeholder="Escolha uma opção"
            )

    
def porta_ja_em_uso(porta):
    """Verifica se a porta já está ocupada."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", porta)) == 0
    
# Função que espera abrir o Localhost
def esperar_e_abrir(url, porta, timeout=15):
    """Espera o servidor iniciar e abre o navegador."""
    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            with socket.create_connection(("localhost", porta), timeout=1):
                webbrowser.open_new(url)
                return
        except OSError:
            time.sleep(0.5)

# Função de animação de carregamento
def animacao_de_upload():
    placeholder = st.empty()
    placeholder.markdown("""
    <style>
    .spinner-container {
      display: flex;
      align-items: center;
      font-size: 24px;
      font-weight: bold;
    }
    .spinner-icon {
      animation: spin 1s linear infinite;
      margin-right: 10px;
    }
    .loading-dots span {
      animation: blink 1.4s infinite both;
    }
    .loading-dots span:nth-child(2) {
      animation-delay: 0.2s;
    }
    .loading-dots span:nth-child(3) {
      animation-delay: 0.4s;
    }
    @keyframes blink {
      0% { opacity: 0.2; }
      20% { opacity: 1; }
      100% { opacity: 0.2; }
    }
    @keyframes spin {
      100% { transform: rotate(360deg); }
    }
    </style>

    <div class="spinner-container">
      <div class="spinner-icon">🔄</div>
      <div class="loading-dots">Carregando<span>.</span><span>.</span><span>.</span></div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(2.5)
    placeholder.empty()

# Função de layout da aplicação
def exibir_tela_inicial():
  # Titulo
  st.title("Poker Tracker: Ganhos e Perdas 🃏")

  # Cabeçalho
  st.header("♣️♥️♠️♦️")

  #SubCabeçalho
  st.subheader("O jogo...")


  # Colocando as infomações de Marina.
  st.markdown("""
                O "jogo do bicho", hoje conhecido como poker, é uma atividade que envolve estratégia, riscos e muita determinação. Desde o seu surgimento, esse jogo desperta grandes desafios e promete aventuras no universo das cartas.

                O caminho dentro do jogo é cheio de obstáculos a serem superados, exigindo habilidade para dominar suas complexidades.

                A seguir, um gráfico apresenta os ganhos e perdas relacionados a essa atividade. O resultado: o jogo está sendo vencido… ou está vencendo?
              """)

# Dicionário de tradução 
dias_pt = {
    "Monday": "Segunda-feira",
    "Tuesday": "Terça-feira",
    "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira",
    "Friday": "Sexta-feira",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}

# Inicio do processo.
exibir_tela_inicial()

# Variável para controlar o carregamento.
if "df_processado" not in st.session_state:
    st.session_state.df_processado = False
    st.session_state.df = None


# Upload do arquivo.
upload = st.file_uploader(
    label="Envie o arquivo",
    type="xlsx",
)

# Só executa animação e leitura se ainda não processou.
if upload is not None and not st.session_state.df_processado:
    animacao_de_upload()
    st.session_state.df = pd.read_excel(upload)
    st.session_state.df_processado = True

# Usa o dataframe armazenado após o carregamento.
if st.session_state.df_processado:
    df = st.session_state.df

    # lista dos sheets existentes
    sheets_existentes = pd.ExcelFile(upload).sheet_names

    filtros = filtros()
    filtros.selecionar_filtros()

    f = datas()
    f.set_datas()

    filtro = st.radio("Você deseja fazer filtro? [Dia/Semana/Mês/Ano]",
         ["Sim", "Não"],
         index=None)
    
    mes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

    # Cria um df do arquivo .xlsx
    df = pd.read_excel(upload, sheet_name=filtros.plataforma)

    # Verifica se o filtro foi selecionado e mostra as opções de filtro.
    if filtro == "Sim":        
        if filtros.data == "Dia":
            # Tenta encontrar a coluna de data automaticamente
            col_data = None
            for col in df.columns:
                if "data" in col.lower():
                    col_data = col
                    break

            if col_data:
                # Converte a coluna para datetime
                df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
                hoje = datetime.now().date()

                # Filtra pela data de hoje
                df_hoje = df[df[col_data].dt.date == hoje]

                if not df_hoje.empty:
                    # Verifica se existe a coluna "Tipo"
                    if "Tipo" in df_hoje.columns:
                        tipos_disponiveis = df_hoje["Tipo"].dropna().unique().tolist()
                        tipo_escolhido = st.selectbox("Escolha o tipo:", tipos_disponiveis)

                        # Aplica o filtro de tipo
                        df_hoje = df_hoje[df_hoje["Tipo"] == tipo_escolhido]

                    if not df_hoje.empty:
                        if filtros.tipo in df_hoje.columns:
                            st.write(f"{filtros.tipo} - Hoje ({datas.hoje}) - Tipo: {tipo_escolhido}")
                            st.line_chart(df_hoje[filtros.tipo])
                        else:
                            st.warning(f"A coluna '{filtros.tipo}' não foi encontrada no arquivo.")
                    else:
                        st.warning(f"Nenhum dado encontrado para o tipo selecionado na data de hoje.")
                else:
                    st.warning("Nenhum dado encontrado para o dia de hoje.")
            else:
                st.error("Nenhuma coluna com nome parecido com 'Data' foi encontrada.")


        elif filtros.data == "Semana":
            f = datas()
            f.set_datas()
            dias_semana = [datetime.fromisocalendar(int(f.ano), int(f.semana), i).date() for i in range(1, 8)]
            # filtra dias até o dia atual (inclusive)
            dias_passados = [
                f"{dias_pt[d.strftime('%A')]} - {d.strftime('%d/%m/%Y')}"
                for d in dias_semana if d <= f.dia
            ]
            if dias_passados:
                dia_escolhido = st.selectbox("Escolha um dia da semana atual:", dias_passados, index=None, placeholder="Escolha o dia")
            else:
                st.error("Nenhum dia da semana atual disponível.")

            # Garante que a coluna "Data" esteja em datetime
            df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

            # Pega a data escolhida em formato datetime
            if dia_escolhido is not None:
                if dia_escolhido:
                    data_str = dia_escolhido.split(" - ")[1]
                    data_escolhida = datetime.strptime(data_str, "%d/%m/%Y").date()

                # Filtra as linhas do DataFrame com essa data
                df_filtrado = df[df["Data"].dt.date == data_escolhida]

                if not df_filtrado.empty:
                    # Verifica se a coluna Tipo existe
                    if "Tipo" in df_filtrado.columns:
                        tipos_disponiveis = df_filtrado["Tipo"].dropna().unique().tolist()
                        tipo_escolhido = st.selectbox("Escolha o tipo:", tipos_disponiveis)

                    # Filtra pelo tipo selecionado
                    df_filtrado = df_filtrado[df_filtrado["Tipo"] == tipo_escolhido]
                    
                    # Exibe o gráfico com as linhas da data escolhida
                    if not df_filtrado.empty:
                        if filtros.tipo == "Saldo":
                            dados = df_filtrado["Saldo"]
                            dados = dados.dropna()
                            dados = dados[dados != 0]
                            if not dados.empty:
                                st.write("Saldo")
                                st.line_chart(dados)
                            else:
                                st.warning("Não há valores de Saldo para mostrar.")

                        elif filtros.tipo == "Buy in":
                            dados = df_filtrado["Buy in"]
                            dados = dados.dropna()
                            dados = dados[dados != 0]
                            if not dados.empty:
                                st.write("Buy in")
                                st.line_chart(dados)
                            else:
                                st.warning("Não há valores de Buy in para mostrar.")
                    else:
                        st.warning("Nenhum dado encontrado para o dia escolhido.")
    

        elif filtros.data == "Mês":
            escolher_mes = st.selectbox("Escolha o Mês:", mes)

            mes_dict = {
                "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
                "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
                "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
            }
            mes_num = mes_dict[escolher_mes]  # mês escolhido
            ano_atual = datetime.now().year  # pega ano atual

            if "Data" in df.columns:
                df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
                df["Mes_num"] = df["Data"].dt.month
                df["Ano"] = df["Data"].dt.year

                # Filtra só do mês escolhido e ano atual
                df_filtrado = df[(df["Mes_num"] == mes_num) & (df["Ano"] == ano_atual)]

                if not df_filtrado.empty:
                    # Verifica se a coluna Tipo existe
                    if "Tipo" in df_filtrado.columns:
                        tipos_disponiveis = df_filtrado["Tipo"].dropna().unique().tolist()
                        tipo_escolhido = st.selectbox("Escolha o tipo:", tipos_disponiveis)

                        # Filtra pelo tipo selecionado
                        df_filtrado = df_filtrado[df_filtrado["Tipo"] == tipo_escolhido]

                    if not df_filtrado.empty:
                        if filtros.tipo == "Saldo":
                            dados = df_filtrado["Saldo"]
                            dados = dados.dropna()
                            dados = dados[dados != 0]
                            if not dados.empty:
                                st.write("Saldo")
                                st.line_chart(dados)
                            else:
                                st.warning("Não há valores de Saldo para mostrar.")

                        elif filtros.tipo == "Buy in":
                            dados = df_filtrado["Buy in"]
                            dados = dados.dropna()
                            dados = dados[dados != 0]
                            if not dados.empty:
                                st.write("Buy in")
                                st.line_chart(dados)
                            else:
                                st.warning("Não há valores de Buy in para mostrar.")
                    else:
                        st.warning(f"Não há dados para o mês de {mes} no ano {ano_atual}.")
            else:
                st.error("Coluna 'Data' não encontrada no arquivo.")

        elif filtros.data == "Ano":
            # Garante que a coluna 'Data' existe e está no formato datetime
            if "Data" in df.columns:
                df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
                df = df.dropna(subset=["Data"])  # opcional: remove linhas com Data inválida
                df["Ano"] = df["Data"].dt.year

                anos_disponiveis = df["Ano"].dropna().unique()
                ano = st.selectbox("Escolha o Ano:", sorted(anos_disponiveis), index=None, placeholder="Escolha o ano")

                if ano is not None:
                    # Filtra só do ano escolhido
                    df_filtrado = df[df["Ano"] == ano]

                    if not df_filtrado.empty:
                        # Verifica se a coluna Tipo existe
                        if "Tipo" in df_filtrado.columns:
                            tipos_disponiveis = df_filtrado["Tipo"].dropna().unique().tolist()
                            tipo_escolhido = st.selectbox("Escolha o tipo:", tipos_disponiveis)

                            # Filtra pelo tipo selecionado
                            df_filtrado = df_filtrado[df_filtrado["Tipo"] == tipo_escolhido]

                    if not df_filtrado.empty:
                        if filtros.tipo == "Saldo":
                            dados = df_filtrado["Saldo"]
                            dados = dados.dropna()
                            dados = dados[dados != 0]
                            if not dados.empty:
                                st.write("Saldo")
                                st.line_chart(dados)
                            else:
                                st.warning("Não há valores de Saldo para mostrar.")

                        elif filtros.tipo == "Buy in":
                            dados = df_filtrado["Buy in"]
                            dados = dados.dropna()
                            dados = dados[dados != 0]
                            if not dados.empty:
                                st.write("Buy in")
                                st.line_chart(dados)
                            else:
                                st.warning("Não há valores de Buy in para mostrar.")
                        else:
                            st.warning(f"Não há dados para o tipo selecionado no ano {ano}.")
                    else:
                        st.warning(f"Não há dados para o ano {ano}.")
            else:
                st.error("Coluna 'Data' não encontrada no arquivo.")

    # Se Não deixa
    elif filtro != None and filtro == "Não":
        if filtros.tipo == None:
            pass
        else:
            st.write(f"Você selecionou: {filtros.tipo}")
            

        if filtros.tipo == "Saldo":
            st.write("Gráfico de Saldo Geral")
            if df is not None and "Saldo" in df.columns:
                df_saldo = df["Saldo"]
                st.line_chart(df_saldo)

        elif filtros.tipo == "Buy in":
            st.write("Gráfico de Buy in Geral")
            if df is not None and "Buy in" in df.columns:
                df_buy = df["Buy in"]
                st.line_chart(df_buy)

if __name__ == "__main__":
    porta = 8502
    url = f"http://localhost:{porta}"

    if porta_ja_em_uso(porta):
        print(f"Já existe uma instância rodando na porta {porta}. Encerrando.")
        sys.exit(0)

    if not os.environ.get("STREAMLIT_BROWSER_OPENED"):
        os.environ["STREAMLIT_BROWSER_OPENED"] = "1"
        threading.Thread(target=esperar_e_abrir, args=(url, porta), daemon=True).start()

    subprocess.run([sys.executable, "-m", "streamlit", "run", "poker.py", "--server.port", str(porta)])