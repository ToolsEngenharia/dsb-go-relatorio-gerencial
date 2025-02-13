import streamlit as st
import pandas as pd
from getDados import get_dataModay, getDados, getDadosPBI
from utildia import quantidade_dias_uteis, dataEhUtil
# Configuração da página
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

# Cabeçalho
col1, col2, col3 = st.columns([2, 4, 1])
with col1:
	st.image('./images/Logo Verde.png', width=200)
with col2:
	st.header('GERENCIAMENTO DE OBRAS - RESIDENCIAL')
with col3:
	if st.button('Atualizar Dados'):
		st.cache_data.clear()
		st.rerun()
			
st.write('# ')

dfMonday = pd.DataFrame(get_dataModay(926240878))
dfMonday['SIGLA'] = dfMonday['SIGLA'].str.strip()
dfMonday['INICIO'] = pd.to_datetime(dfMonday['INICIO'], format='%Y-%m-%d')
dfMonday['TERMINO'] = pd.to_datetime(dfMonday['TERMINO'], format='%Y-%m-%d')

dfPBIs = pd.DataFrame(getDadosPBI())
dfPBIs['MES'] = pd.to_datetime(dfPBIs['DATA'], format='%Y-%m-%d').dt.tz_localize(None).dt.to_period('M')
dfPBIs = pd.merge(dfPBIs, dfMonday[['SIGLA', 'RCR']], left_on='SIGLA', right_on='SIGLA', how='left')
dfPBIs['SIGLA'] = dfPBIs['SIGLA'].str.strip()
dfPBIs['DATA'] = pd.to_datetime(dfPBIs['DATA'], format='%Y-%m-%d')
dfPBIs = dfPBIs.drop_duplicates(subset=['SIGLA', 'MES'])
dfPBIs = dfPBIs.drop(columns=['DATA'])

dfActivities = pd.DataFrame(getDados())
dfActivities = dfActivities.iloc[1:]
dfActivities = dfActivities.drop(columns=['ID'])
dfActivities = dfActivities.drop_duplicates(subset=['OBRA', 'DATA'])
dfActivities['DATA'] = pd.to_datetime(dfActivities['DATA'], format='%Y-%m-%d')
dfActivities['DIA_UTIL'] = dfActivities.apply(lambda x: dataEhUtil(x['DATA'].year, x['DATA'].month, x['DATA'].day), axis=1)
dfActivities['MES'] = pd.to_datetime(dfActivities['DATA'], format='%Y-%m-%d').dt.tz_localize(None).dt.to_period('M')
dfActivities = dfActivities.groupby(['OBRA', 'MES', 'DIA_UTIL']).size().unstack(fill_value=0).reset_index()
dfActivities.columns = ['OBRA', 'MES', 'NÃO ÚTIL', 'ÚTIL']
dfActivities['QUANTIDADE DE DIAS ÚTEIS'] = dfActivities.apply(lambda x: quantidade_dias_uteis(x['MES'].year, x['MES'].month), axis=1)
dfActivities = pd.merge(dfActivities, dfMonday[['SIGLA', 'RCR']], left_on='OBRA', right_on='SIGLA', how='left')
dfActivities = dfActivities.drop(columns=['SIGLA'])
dfActivities = dfActivities.dropna(subset=['RCR'])

ano_min = dfMonday['INICIO'].dt.year.min()
ano_max = dfMonday['TERMINO'].dt.year.max()
intervaloAnos = range(ano_min, ano_max+1)
intervaloAnos = list(filter(lambda x: x >= 2024, intervaloAnos))

with st.container( border=True ):
	col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

	with col2:
		listRCR = dfActivities['RCR'].unique()
		listRCR = listRCR[listRCR != 'MARCIO TEIXEIRA']
		listRCR = ['TODOS'] + listRCR.tolist()
		st_rcr = st.selectbox('RCR', listRCR)

	with col1:
		if st_rcr != 'TODOS':
			listProdutos = dfMonday[dfMonday['RCR'] == st_rcr]['PRODUTO'].unique()
		else:
			listProdutos = dfMonday['PRODUTO'].unique()
		st_produto = st.pills('PRODUTO', listProdutos, selection_mode="multi", default=listProdutos)

	with col3:
		sln_ano = st.selectbox('ANO', intervaloAnos, index= intervaloAnos.index(2024))
		dfMonday = dfMonday[(dfMonday['INICIO'].dt.year <= sln_ano) & (dfMonday['TERMINO'].dt.year >= sln_ano)]

	# with col4:
	# 	listFases = dfMonday['FASE'].unique()
	# 	st_fase = st.pills('FASE', listFases, selection_mode="multi", default=listFases)

	with col4:
		listObras = dfMonday['SIGLA'].unique()

		listObras = ['TODAS'] + listObras.tolist()
		st_obras = st.selectbox('OBRAS', listObras)
		st.write('')

if st_rcr != 'TODOS':
	dfMonday = dfMonday[dfMonday['RCR'] == st_rcr]

if st_produto != []:
	dfMonday = dfMonday[dfMonday['PRODUTO'].isin(st_produto)]

# if st_fase != []:
# 	dfMonday = dfMonday[dfMonday['FASE'].isin(st_fase)]

if st_obras != 'TODAS':
	dfMonday = dfMonday[dfMonday['SIGLA'] == st_obras]

# FILTRANDO AS ATIVIDADES por ano conforme a seleção
dfActivities = dfActivities[dfActivities['MES'].dt.year == sln_ano]
dfPBIs = dfPBIs[dfPBIs['MES'].dt.year == sln_ano]

for rdc in dfActivities['RCR'].unique():
	if (st_rcr == 'TODOS'or st_rcr == rdc) :
		with st.expander(f'{rdc}', expanded=True):
			obras = dfMonday[dfMonday['RCR'] == rdc]['SIGLA'].unique()

			dfActivities1 = dfActivities[dfActivities['OBRA'].isin(obras)][['OBRA', 'MES', 'ÚTIL', 'QUANTIDADE DE DIAS ÚTEIS']]
			dfPBIs1 = dfPBIs[dfPBIs['SIGLA'].isin(obras)]
			dfPBIs1['ÚTIL'] = 'ok'

			col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
			with col1:
				st.metric('OBRAS', len(obras), border=True)

			with col2:
				st.metric('OBRAS STATUS', dfActivities1['OBRA'].nunique(), border=True)

			with col3:
				st.metric('PBIs', dfPBIs1['SIGLA'].nunique(), border=True)

			with col4:
				st.metric('% ATIVIDADES', round(dfActivities1['ÚTIL'].sum() / dfActivities1['QUANTIDADE DE DIAS ÚTEIS'].sum() * 100, 2), border=True)
			# with col4:
			# 	st.metric('% PBIs', round(dfPBIs1['ÚTIL'].count() / dfPBIs1['SIGLA'].count() * 100, 2), border=True)

			df_temp = dfActivities1.copy()
			dfActivities1 = df_temp.pivot(index='OBRA', columns='MES', values='ÚTIL')
			dfActivities1 = dfActivities1.fillna(0).astype(int)
			dfActivities1 = dfActivities1.where(pd.notnull(dfActivities1), '')

			# pivot table colunas meses e linhas obras para o dataframe de PBIs
			dfPBIs1 = dfPBIs1.pivot(index='SIGLA', columns='MES', values='ÚTIL')

			# adiciona a coluna 'TOTAL' no dataframe
			dfActivities1['TOTAL'] = dfActivities1.sum(axis=1)

			# calcula os dias úteis únicos para cada mês usando o dataframe original
			dias_uteis = df_temp.groupby('MES')['QUANTIDADE DE DIAS ÚTEIS'].first()

			# cria uma nova linha com os dias úteis para cada mês
			row_dias = {}
			for col in dfActivities1.columns:
				if col == 'TOTAL':
					row_dias[col] = sum(dias_uteis)
				else:
					row_dias[col] = dias_uteis.get(col, '')
					
			# adiciona a nova linha ao final do dataframe
			dfActivities1.loc['DIAS ÚTEIS'] = row_dias

			# move a linha 'DIAS ÚTEIS' para a primeira linha do dataframe
			dfActivities1 = dfActivities1.reindex(['DIAS ÚTEIS'] + dfActivities1.index[:-1].tolist())

			# indiferente de da coluna ser o valor for None, substitui por ''
			dfPBIs1 = dfPBIs1.where(pd.notnull(dfPBIs1), '')
			
			with st.container(border=True):
				st.write('STATUS DAS ATIVIDADES')
				st.dataframe(dfActivities1, use_container_width=True)

			with st.container(border=True):
				st.write('RELATÓRIO DE GERENCIAL DE OBRAS')
				st.dataframe(dfPBIs1, use_container_width=True)
