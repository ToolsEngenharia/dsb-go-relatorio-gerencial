import requests as req
import streamlit as st

@st.cache_data()
def getDados():
	url = 'https://script.google.com/macros/s/AKfycbxaeIfGD1Tc8BfGKnyjC1Clzd7aRrbKhTSYDiYUoBMXjVtD1PMmS1YBPG0UNJtedNhB/exec'
	response = req.get(url)
	data = response.json()
	return data['itens']

@st.cache_data()
def getDadosPBI():
	url = 'https://script.google.com/macros/s/AKfycbwqui34_1ypLekQlnO-P_6z_00dlZNrejda1AqThNj8IIta9j11JJ072bxfQJRLRoA/exec'
	response = req.get(url)
	data = response.json()
	return data['itens']

@st.cache_data
def get_dataModay(board):
	api = 'eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjI2Njg4NzkwNiwiYWFpIjoxMSwidWlkIjoyMzA5NjM0MiwiaWFkIjoiMjAyMy0wNy0wNVQxNDoyNTo1NS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6NDkwNjU3MCwicmduIjoidXNlMSJ9.tRWcVx3Q9oUEPKRMdaEiFzqCf1n0F7NelbjY09jQix4'
	url = 'https://api.monday.com/v2'
	query = 'query { boards(ids: '+str(board)+') { items_page (limit:500) { cursor items { id name column_values(ids: [\"status6\", \"dup__of_equipe\", \"produto\", , \"timeline\",\"location\", \"dup__of_produto\"]) { id text  } } } } }'

	headers = {
		'Authorization': api
	}
	response = req.post(url, json={'query': query}, headers=headers)
	return transformar_dados(response.json())

def transformar_dados(input_data):
    try:
        items = input_data['data']['boards'][0]['items_page']['items']
    except (KeyError, IndexError):
        raise ValueError("Formato de dados de entrada inválido.")

    resultado = []

    for item in items:
        novo_item = {
			"SIGLA": item.get('name', '').split('-')[0],
            "OBRA": item.get('name', ''),
            "INICIO": next(
                (c['text'].split(' - ')[0] for c in item.get('column_values', []) 
                if c['id'] == 'timeline' and 'text' in c and ' - ' in c['text']), 
                None
            ),
            "TERMINO": next(
                (c['text'].split(' - ')[1] for c in item.get('column_values', []) 
                if c['id'] == 'timeline' and 'text' in c and ' - ' in c['text']), 
                None
            ),
            "FASE": next((c['text'] for c in item.get('column_values', []) if c['id'] == 'status6'), ''),
            "RCR": next((c['text'].split('@')[0].replace('.',' ').upper() for c in item.get('column_values', []) if c['id'] == 'dup__of_equipe'), ''),
            "PRODUTO": next((c['text'] for c in item.get('column_values', []) if c['id'] == 'produto'), ''),
            "LOCAL": next((c['text'] for c in item.get('column_values', []) if c['id'] == 'location'), ''),
            "CLIENTE": next((c['text'] for c in item.get('column_values', []) if c['id'] == 'dup__of_produto'), ''),
        }
        resultado.append(novo_item)

    #selecionar apenas os itens que possuem o produto GERENCIAMENTO RESIDENCIAL e que esta na fase de Fase Obra
    # resultado = [item for item in resultado if item['PRODUTO'] == 'GERENCIAMENTO DE OBRA RESIDENCIAL' and item['FASE'] == 'Fase Obra']
    resultado = [item for item in resultado if item['PRODUTO'] == 'GERENCIAMENTO DE OBRA RESIDENCIAL' and item ['INICIO'] is not None and item['RCR'] != '']
    return resultado