# bibliotecas
import pandas as pd
import numpy as np
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_theme import st_theme
from millify import millify
import altair as alt

# configs da página principal
st.set_page_config(page_title="Análise de Faturamento", page_icon="📈", layout="wide", initial_sidebar_state='collapsed')

# estilização
def style_metric_cards(
    color:str = "#232323",
    background_color: str = "#FFF",
    border_size_px: int = 1,
    border_color: str = "#CCC",
    border_radius_px: int = 5,
    border_left_color: str = "#9AD8E1",
    box_shadow: bool = True,
):

    box_shadow_str = (
        "box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;"
        if box_shadow
        else "box-shadow: none !important;"
    )
    st.markdown(
        f"""
        <style>
            div[data-testid="stMetric"],
            div[data-testid="metric-container"] {{
                background-color: {background_color};
                border: {border_size_px}px solid {border_color};
                padding: 5% 5% 5% 10%;
                border-radius: {border_radius_px}px;
                border-left: 0.5rem solid {border_left_color} !important;
                color: {color};
                {box_shadow_str}
            }}
             div[data-testid="stMetric"] p,
             div[data-testid="metric-container"] p {{
              color: {color};
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 1rem;
                   
                }
        </style>
        """, unsafe_allow_html=True) 


# diferença percentual
def dif_percent(col, df, estat):
    agrupado = df.groupby('Mês')[col].agg([estat])[estat].pct_change() * 100
    agrupado.fillna(0, inplace=True)
    agrupado = agrupado.apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else 'NaN')

    return agrupado


# carregando dados e retornando diferenças
@st.cache_data(ttl=3600)
def load():
    df = pd.read_csv('VendaProduto.csv')

    # calculando diferenças e média
    agrupado_diff_faturado = dif_percent('Faturamento', df, 'sum')
    agrupado_media_faturado_mensal = df.groupby(['Mês'])['Faturamento'].mean()

    return df, agrupado_diff_faturado, agrupado_media_faturado_mensal


# definindo estrutura geral
sidebar = st.sidebar
dash_1 = st.container()
dash_2 = st.container()
dash_3 = st.container()
dash_4 = st.container()


# carregando dados e grupos
base, diff_faturado_agrupado, media_faturado_agrupado = load()


# barra lateral
with sidebar:
    # guardando os meses
    meses = base['Mês'].unique().tolist() 
    meses.insert(0, "Todos")
    map_mes = {k:v for (k,v) in zip(meses, ['2023', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'])}

    # lista de meses para seleção
    mes_selec = st.selectbox("Selecione um mês", meses)

    if mes_selec == "Todos":
        df_selec = base
    else:
        df_selec = base[base['Mês'] == int(mes_selec)]


# Título
with dash_1:
    st.markdown("<h2 style='text-align: center;'>Desempenho de Fertilizantes em 2023</h2>", unsafe_allow_html=True)
    st.write("")


# Cards 
with dash_2:
    # calcular valores
    total_faturado = df_selec['Faturamento'].sum()
    media_faturado = media_faturado_agrupado[mes_selec] if mes_selec != 'Todos' else df_selec.groupby(['Mês'])['Faturamento'].sum().sum()/12

    # mudança com o filtro
    if mes_selec == "Todos":
        faturado_diff = round((df_selec.groupby('Mês')['Faturamento'].sum()[[1,12]].pct_change()*100)[12], 2).astype('str')+'%'
        produto_maior_faturamento = df_selec.groupby('NOME')['Faturamento'].sum().idxmax()
        valor_maior_fat = df_selec.groupby('NOME')['Faturamento'].sum().sort_values(ascending=False).max()
    else:
        faturado_diff = diff_faturado_agrupado[mes_selec]
        produto_maior_faturamento = df_selec.sort_values('Faturamento', ascending=False).iloc[0,1]
        valor_maior_fat = df_selec.groupby('NOME')['Faturamento'].sum().sort_values(ascending=False).max()


    # definindo colunas dos Cards
    col1, col2, col3 = st.columns(3)

    # Faturamento
    col1.metric(label="**Total Faturado - " + str(2023 if mes_selec=='Todos' else map_mes[mes_selec]) + '**' , value = "R$"+millify(total_faturado, precision=2), delta = faturado_diff, help='Diferença percentual é *MoM*, sendo comparado janeiro e dezembro no agregado')

    # Média
    col2.metric(label="**Faturamento Médio - " + str(2023 if mes_selec=='Todos' else map_mes[mes_selec]) + '**', value = "R$"+millify(media_faturado, precision=2), delta = faturado_diff)
    
    # Maior Faturamento
    st.markdown(
    """
    <style>
    [data-testid="stMetricDelta"] svg {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
    )
    col3.metric(label="**Maior Faturamento - " + str(2023 if mes_selec=='Todos' else map_mes[mes_selec]) + '**', value = produto_maior_faturamento, delta = 'R$' + millify(valor_maior_fat, precision=2))
    
    style_metric_cards(border_left_color="#DBF227")



# Gráficos centrais
with dash_3:
    # colunas dos gráficos
    col1, col2 = st.columns(2)

    def soma_fat_agrupado(col):
        return df_selec.groupby(col)['Faturamento'].sum().reset_index()


    produto_faturamento = soma_fat_agrupado('NOME') # df_selec.groupby('NOME')['Faturamento'].sum().reset_index()
    composicao_uso = soma_fat_agrupado('INDICACAO_USO') # df_selec.groupby('INDICACAO_USO')['Faturamento'].sum().reset_index()
    composicao_sust = soma_fat_agrupado('CLASS_SUSTENTAB') # df_selec.groupby('CLASS_SUSTENTAB')['Faturamento'].sum().reset_index()
    composicao_solo = soma_fat_agrupado(['Mês', 'SOLO_RECOMENDADO']) # df_selec.groupby(['Mês', 'SOLO_RECOMENDADO'])['Faturamento'].sum().reset_index()
    composicao_tipo = soma_fat_agrupado('TIPO') # df_selec.groupby(['TIPO'])['Faturamento'].sum().reset_index()
    composicao_solub = soma_fat_agrupado('CLASS_SOLUBILIDADE') # df_selec.groupby(['CLASS_SOLUBILIDADE'])['Faturamento'].sum().reset_index()
    composicao_toxi_irrig = soma_fat_agrupado(['METODO_IRRIGACAO_IDEAL', 'CLASS_TOXICIDADE']) # df_selec.groupby(['METODO_IRRIGACAO_IDEAL', 'CLASS_TOXICIDADE'])['Faturamento'].sum().reset_index()

    # gráfico 1
    with col1:

        plot = alt.Chart(produto_faturamento, title = alt.Title('Faturamento por produto', anchor='middle', orient='top')).mark_bar(opacity = 0.9, color="#9FC131",orient='horizontal').encode(
                x = alt.X('sum(Faturamento):Q'),
                y = alt.Y('NOME:N', sort='-x', title='Fertilizante'),
                color = alt.condition(
                    alt.datum.NOME == produto_faturamento.sort_values('Faturamento', ascending=False).iloc[0]['NOME'],
                    alt.value('#007F7F'),
                    alt.value('#9FC131')
                ),
                tooltip = [alt.Tooltip('sum(Faturamento):Q', title = 'Total Faturado', format='~s'), alt.Tooltip('NOME:N', title = 'Fertilizante')]
            )
        
        plot = plot.configure_axisX(grid = False, labels=False, title='')
        st.altair_chart(plot, use_container_width=True)


    # gráficos 
    with col2:
        
        # gráficos para categorias
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['Por uso', 'Por tipo', 'Por solo', 'Por toxicidade e irrigação', 'Por sustentabilidade', 'Por solubilidade'])

        with tab1:
            plot = alt.Chart(composicao_uso).mark_bar(opacity=0.9, color="#9FC131").encode(
                x = alt.X('sum(Faturamento):Q'),
                y = alt.Y('INDICACAO_USO:N', sort='-x', title='Tipo de uso'),
                tooltip = [alt.Tooltip('sum(Faturamento):Q', title='Total Faturado', format='~s'), alt.Tooltip('INDICACAO_USO:N', title='Tipo de uso')]
            )

            text = alt.Chart(composicao_uso).mark_text(color='white', dx=-40, fontWeight='bold').encode(
                x = alt.X('sum(Faturamento):Q'),
                y = alt.Y('INDICACAO_USO:N', stack = 'zero', sort='-x'),
                text = alt.Text('sum(Faturamento):Q', format='~s'),
                tooltip = [alt.Tooltip('sum(Faturamento):Q', format='~s', title='Total Faturado'), alt.Tooltip('INDICACAO_USO:N', title='Tipo de uso')]
            )


            plot = plot + text
            plot = plot.configure_axisX(grid=False, labels=False, title='')
            plot = plot.properties(height=300)
            st.altair_chart(plot, use_container_width=True)


        with tab2:
            plot = alt.Chart(composicao_tipo).mark_bar(opacity=0.9, color="#9FC131").encode(
                x = alt.X('sum(Faturamento):Q'),
                y = alt.Y('TIPO:N', sort='-x', title='Tipo de Fertilizante'),
                tooltip = [alt.Tooltip('sum(Faturamento):Q', format='~s', title='Total Faturado'), alt.Tooltip('TIPO:N', title='Tipo de fertilizante')]
            )

            text = alt.Chart(composicao_tipo).mark_text(color='white', dx=-40, fontWeight='bold').encode(
                x = alt.X('sum(Faturamento):Q'),
                y = alt.Y('TIPO:N', stack = 'zero', sort='-x'),
                text = alt.Text('sum(Faturamento):Q', format='~s'),
                tooltip = [alt.Tooltip('sum(Faturamento):Q', format='~s', title='Total Faturado'), alt.Tooltip('TIPO:N', title='Tipo de fertilizante')]
            )

            plot = plot + text
            plot = plot.configure_axisX(grid=False, labels=False, title='')
            plot = plot.properties(height=300)
            st.altair_chart(plot, use_container_width=True)

        
        with tab3:
            cores = {'Arenoso':'#9FC131', 'Humoso':'#007F7F', 'Argiloso':'#2F4858'}

            plot = alt.Chart(composicao_solo).mark_bar().encode(
                x = alt.X('Mês:O'),
                y = alt.Y('sum(Faturamento):Q', stack='zero'),
                color = alt.Color('SOLO_RECOMENDADO:N', scale = alt.Scale(domain = list(cores.keys()), range = list(cores.values()))).title('Solo Recomendado'),
                tooltip = [alt.Tooltip('sum(Faturamento):Q', format='~s', title='Total Faturado'), alt.Tooltip('SOLO_RECOMENDADO:N', title='Solo Recomendado')]
            )

            text = alt.Chart(composicao_solo).mark_text(align='center', baseline='top', dy=10, color='white', fontWeight='bold').encode(
                y = alt.Y('sum(Faturamento):Q', stack='zero', axis=alt.Axis(format='~s')),
                x = alt.X('Mês:O', axis=alt.Axis(labelAngle=0)),
                detail = alt.Detail('SOLO_RECOMENDADO:N').title('Solo Recomendado'),
                text = alt.Text('sum(Faturamento):Q', format='~s'),
                tooltip = [alt.Tooltip('sum(Faturamento):Q', format='~s', title='Total Faturado'), alt.Tooltip('SOLO_RECOMENDADO:N', title='Solo Recomendado')]
            )

            plot = plot + text
            plot = plot.configure_axisY(grid = False, labels=False, title='')
            plot = plot.properties(height=300)

            st.altair_chart(plot, use_container_width=True)

        
        with tab4:
            cores = {'Baixa':'#9FC131', 'Média':'#007F7F', 'Alta':'#2F4858'}

            plot = alt.Chart(composicao_toxi_irrig).mark_bar().encode(
                y = alt.Y('METODO_IRRIGACAO_IDEAL:N').axis().title('Método de Irrigação'),
                x = alt.X('sum(Faturamento):Q', stack='zero'),
                color = alt.Color('CLASS_TOXICIDADE:O', scale = alt.Scale(domain = list(cores.keys()), range = list(cores.values()))).title('Toxicidade'),
                tooltip = [alt.Tooltip('sum(Faturamento):Q', format='~s', title='Total Faturado'), 
                           alt.Tooltip('METODO_IRRIGACAO_IDEAL:N', title='Método de irrigação'), 
                           alt.Tooltip('CLASS_TOXICIDADE:O', title='Toxicidade')]
            )

            text = alt.Chart(composicao_toxi_irrig).mark_text(color='white', dx=-20, fontWeight='bold').encode(
                y = alt.Y('METODO_IRRIGACAO_IDEAL:N'),
                x = alt.X('sum(Faturamento):Q', stack = 'zero'),
                detail = alt.Detail('CLASS_TOXICIDADE:O'),
                text = alt.Text('sum(Faturamento):Q', format='~s'),
                tooltip = [alt.Tooltip('sum(Faturamento):Q', format='~s', title='Total Faturado'), 
                           alt.Tooltip('METODO_IRRIGACAO_IDEAL:N', title='Método de irrigação'), 
                           alt.Tooltip('CLASS_TOXICIDADE:O', title='Toxicidade')]
            )

            plot = plot + text
            plot = plot.configure_axisX(grid = False, labels=False, title='')
            plot = plot.properties(height=300)

            st.altair_chart(plot, use_container_width=True)

        
        with tab5:
            composicao_sust['Porcentagem'] = composicao_sust['Faturamento']/composicao_sust['Faturamento'].sum()*100

            plot = alt.Chart(composicao_sust).mark_arc(innerRadius=80).encode(
                x = alt.value(250),
                y = alt.value(100),
                theta = alt.Theta('Faturamento:Q').stack(True),
                color = alt.Color('CLASS_SUSTENTAB:O').title('Sustentabilidade').scale(domain=['Alta', 'Média', 'Baixa'], range=['#9FC131', '#007F7F', '#2F4858']).legend(orient='left')
            )

            plot = plot.properties(height=310).transform_joinaggregate(
                Total='sum(Faturamento)',
                ).transform_calculate(
                    Porcentagem='datum.Faturamento/datum.Total'
                )

            text = plot.mark_text(
                align='center',
                radius=160,
                size=20
            ).encode(
                text=alt.Text('Porcentagem:Q', format='.2%')
            )

            plot = plot + text
            st.altair_chart(plot, use_container_width=True)


        with tab6:
            composicao_solub['Porcentagem'] = composicao_solub['Faturamento']/composicao_solub['Faturamento'].sum()*100

            plot = alt.Chart(composicao_solub).mark_arc(innerRadius=80).encode(
                x = alt.value(276),
                y = alt.value(100),
                theta = alt.Theta('Faturamento:Q').stack(True),
                color = alt.Color('CLASS_SOLUBILIDADE:O').title('Solubilidade').scale(domain=['Alta', 'Média', 'Baixa'], range=['#9FC131', '#007F7F', '#2F4858']).legend(orient='left')
            )

            plot = plot.properties(height=310).transform_joinaggregate(
                Total='sum(Faturamento)',
                ).transform_calculate(
                    Porcentagem='datum.Faturamento/datum.Total'
                )

            text = plot.mark_text(
                align='center',
                radius=160,
                size=20
            ).encode(
                text=alt.Text('Porcentagem:Q', format='.2%')
            )

            plot = plot + text
            
            st.altair_chart(plot, use_container_width=True)

        

# tabela e gráfico de linhas
with dash_4:

    col1, col2 = st.columns(2)

    with col1:
        fat_linha = base.groupby('Mês')['Faturamento'].sum().reset_index()
        del map_mes['Todos']
        fat_linha['label_mes'] = list(map_mes.values())

        plot = alt.Chart(fat_linha, title = alt.Title('Faturamento mensal', anchor='middle', orient='top')).mark_line(point=True).encode(
            x = alt.X('Mês:O'),
            y = alt.Y('Faturamento:Q'),
            color = alt.value('#9FC131'),
            tooltip = [alt.Tooltip('Faturamento:Q', title='Total Faturado', format='~s'), alt.Tooltip('label_mes', title='Mês')]
        )

        tema = st_theme()['backgroundColor']

        text = plot.mark_text(align ='center', baseline = 'bottom', dy = 30).encode(
            x = 'Mês:O',
            y = 'Faturamento:Q',
            text = 'label_mes',
            color = alt.value('white') if tema == '#0e1117' else alt.value('#0E1117'),
            angle = alt.value(0)
        )

        legend = plot.mark_text(
            align = 'center',
            baseline = 'bottom',
            dy= -15,
            strokeWidth=0.5,  
            fontWeight='bold', 
        ).encode(
            text=alt.Text('Faturamento:Q', format='~s')
        )

        plot = plot + legend + text
        plot = plot.configure_axisY(grid = False, labels=False, title='')
        plot = plot.configure_axisX(grid = False, labels=False, title='')

        st.altair_chart(plot, use_container_width=True)


    with col2:
        galoes = base[['NOME','PRECO_MEDIO_GALAO_2022', 'PRECO_MEDIO_GALAO_2023', 'STATUS_VENDA']].groupby('NOME')[['PRECO_MEDIO_GALAO_2022', 'PRECO_MEDIO_GALAO_2023', 'STATUS_VENDA']].min().reset_index()

        galoes['Diferença'] = (galoes['PRECO_MEDIO_GALAO_2023'] - galoes['PRECO_MEDIO_GALAO_2022'])/galoes['PRECO_MEDIO_GALAO_2023']*100
        galoes = galoes[['NOME', 'PRECO_MEDIO_GALAO_2022', 'PRECO_MEDIO_GALAO_2023', 'Diferença', 'STATUS_VENDA']]

        st.dataframe(galoes, hide_index=True, height=300, use_container_width=True, column_config={
            'NOME': 'Produto',
            'PRECO_MEDIO_GALAO_2023': st.column_config.NumberColumn('Preço Médio Galão 2023', format='R$%.2f'),
            'PRECO_MEDIO_GALAO_2022': st.column_config.NumberColumn('Preço Médio Galão 2022', format='R$%.2f'),
            'Diferença': st.column_config.NumberColumn(format='%.2f%%'),
            'STATUS_VENDA': 'Status Venda'
        })
