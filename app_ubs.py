# Instalação
#!pip install geopy folium streamlit

# Bibliotecas
from geopy.geocoders import Nominatim
import requests
import os
import pandas as pd
import folium
import streamlit as st

# abertura
with st.container():
    col3,col4,col5 = st.columns([.5,1.5,.5])
    with col4:
        st.markdown("""
<h5 style='text-align: center; color:#ffffff;font-family:Segoe UI,sans-serif; background-color: #578CA9;'>Projeto desenvolvido para o <br>III Encontro de Ciência de Dados das Fatecs</h5>
""", unsafe_allow_html=True)

st.markdown("""
<br>
<h1 style='text-align: center; color:#202020;font-family:helvetica'>Agregador de pesquisas eleitorais por<br>gênero e raça</br></h1>
<br>
<h4 style='text-align: center; color:#54595F;font-family:Segoe UI, sans-serif'>Consolidação de pesquisas para as eleições presidenciais de 2022</h4>
""", unsafe_allow_html=True)
st.markdown("---")

##retira o made streamlit no fim da página##
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Função para converter CEP
def converter_cep(cep):
    link = f'http://viacep.com.br/ws/{cep}/json/'
    request = requests.get(link)

    end_dic = request.json()
    
    rua = end_dic['logradouro']
    cidade = end_dic['localidade']
    estado = end_dic['uf']
    localizar = f'{rua}, {cidade}, {estado}, Brazil'
    
    geolocator = Nominatim(user_agent="my_app")
    location = geolocator.geocode(localizar, addressdetails=True)

    end_final = [location.latitude, location.longitude]
    
    return end_final

# Função para buscar informações em CSV
def buscar_informacao_em_csv(informacao_desejada, cep):
    end_ubs = []
    global dados_med_ubs
    dados_med_ubs = []
    medicamento_encontrado = False

    arquivos = [arquivo for arquivo in os.listdir() if arquivo.endswith('.csv')]
    
    for arquivo in arquivos:
        df = pd.read_csv(arquivo).reset_index(drop=True)
        
        informacao_encontrada = df[df['Medicamento'] == informacao_desejada]
        
        informacao_encontrada = informacao_encontrada[['Nome', 'Endereco', 'CEP', 'Quantidade em Estoque']]
        
        if (informacao_encontrada['Quantidade em Estoque'] > 0).any():
            end_ubs.append(informacao_encontrada['CEP'].values.tolist())
            medicamento_encontrado = True
            dados_med = informacao_encontrada[['Nome','Quantidade em Estoque']]
            dados_med_ubs.append(dados_med)
        else:
            print("Medicamento não encontrado.")
    
    return end_ubs

# Função para criar mapa com marcadores
def criar_mapa(end_client, end_ubs, dados_med_ubs):
    mapa = folium.Map(location=end_client, zoom_start=15)

    folium.Marker(location=end_client, popup='Minha Localização').add_to(mapa)

    for i in range(0, len(end_ubs)):
        remedio = converter_cep(end_ubs[i][0])
        rotulo_ubs = f"{list(dados_med_ubs[i]['Nome'])}\nEstoque: {list(dados_med_ubs[i]['Quantidade em Estoque'])}"
        folium.Marker(location=remedio, popup=rotulo_ubs, icon=folium.Icon(color='purple')).add_to(mapa)

    return mapa

# Interface do Streamlit
st.title("Busca de Medicamentos e Farmácias Próximas")
cep_input = st.text_input('Insira o CEP:')
medicamento_input = st.text_input('Nome do Medicamento:')
st.button('Buscar')

# Processamento dos dados e exibição do mapa
if cep_input and medicamento_input:
    cep_input = cep_input.replace(" ", "").replace("-", "")
    medicamento_input = medicamento_input.upper()

    if len(cep_input) == 8 and cep_input.isdigit():
        end_client = converter_cep(cep_input)
        end_ubs = buscar_informacao_em_csv(medicamento_input, cep_input)
        
        if end_ubs:
            mapa = criar_mapa(end_client, end_ubs, dados_med_ubs)
            st.write(mapa._repr_html_(), unsafe_allow_html=True)
        else:
            st.warning("Medicamento não encontrado em nenhuma farmácia próxima.")
    else:
        st.error('CEP inválido. Insira exatamente 8 caracteres numéricos')
