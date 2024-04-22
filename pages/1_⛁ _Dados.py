import streamlit as st
import pandas as pd

st.set_page_config(page_title="Análise de Faturamento", page_icon="📈", layout="wide", initial_sidebar_state='collapsed')

st.markdown('# Tabela Cruzada')
df_origin = pd.read_csv('./VendaProduto.csv')


st.dataframe(df_origin, hide_index=True)
st.markdown(
                """
                <style>
                [data-testid="stElementToolbar"] {
                    display: none;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

st.write('A tabela possui', df_origin.shape[0], 'registros e ', df_origin.shape[1], 'colunas.')

with st.expander('Descrição:'):
    st.write('''

        A tabela acima foi cruzada no formato *SQL-join* a partir de outras duas (Vendas e Produtos), usando a coluna de *ID* como chave. \\
        Ambas as tabelas passaram por breves tratamentos (strings, números, dentre outros) antes do cruzamento. 

        - **ID_FERTILIZANTE**: código de identificação do produto fertilizante
        - **NOME**: nome do fertilizante
        - **PRECO_MEDIO_GALAO_2022**: preço médio de comercialização do galão de 50 litros do fertilizante para os distribuidores, em 2022
        - **PRECO_MEDIO_GALAO_2023**: preço médio de comercialização do galão de 50 litros do fertilizante para os distribuidores, em 2023
        - **TIPO**: tipo químico do fertilizante
        - **SOLO_RECOMENDADO**: tipo de solo mais adequado para utilização do fertilizante
        - **INDICACAO_USO**: recomendação de culturas mais adequadas para utilização do fertilizante
        - **CLASS_TOXICIDADE**: classificação do nível de toxicidade do fertilizante
        - **TEMPO_LIB_NUTRIENTES**: classificação do tempo necessário para liberação de nutrientes do fertilizante
        - **CLASS_SUSTENTAB**: classificação sobre o nível de sustentabilidade ambiental do fertilizante
        - **CLASS_SOLUBILIDADE**: classificação do grau de solubilidade em água do fertilizante
        - **METODO_IRRIGACAO_IDEAL**: indicação de se o fertilizante é mais indicado para irrigação por gotejamento ou aspersão
        - **STATUS_VENDA**: status atual de comercialização do fertilizante no mercado
        - **Mês**: mês de referência do faturamento
        - **Faturamento**: faturamento líquido mensal em vendas do fertilizante

    ''')

st.text('')
st.write('Escolha o melhor nome:')

col1, col2 = st.columns([1,4])

with col1:
    nome = st.text_input(label = '', 
                         label_visibility='collapsed', 
                         placeholder='dados',
                         value='')


csv = df_origin.to_csv(sep='\t', index=False)

if nome != '':
    nome = nome + '.txt'
else:
    nome = 'dados.txt'

with col2:
    st.download_button(label='Baixar dados', data=csv, file_name=nome)
