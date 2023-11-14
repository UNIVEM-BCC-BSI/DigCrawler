from flask import Flask, render_template

import requests
from bs4 import BeautifulSoup
import sqlite3

# CONSTANTES
ACRESCIMO = 48
INDICE = 49

# FUNÇÕES
def retornar_media_aritmetica(lista):
    return sum(lista) / len(lista)

def retornar_apenas_os_precos(produto):
    return produto[2]

def perguntar_o_produto_desejado():
    return input('Informe o produto sobre o qual deseja obter informações: ').split()

def adequar_para_formato_da_url(separador, nome_do_produto):
    return f'{separador}'.join(nome_do_produto)

def pegar_numero_paginas():
    tag_paginas = soup.find('li', class_="andes-pagination__page-count")
    numero_paginas = int(tag_paginas.text.split()[1])
    return numero_paginas

def retornar_url_inicial():
  produto_desejado = perguntar_o_produto_desejado()

  primeira_parte_da_url = adequar_para_formato_da_url('-', produto_desejado)
  segunda_parte_da_url = adequar_para_formato_da_url('%20', produto_desejado)

  url_da_primeira_pagina = f'https://lista.mercadolivre.com.br/{primeira_parte_da_url}#D[A:{segunda_parte_da_url}]'

  return url_da_primeira_pagina

def inserir_dados(descricao, preco):
    cursor.execute("INSERT INTO products (descricao, price) VALUES (?, ?);", (descricao, preco))


# CRIAÇÃO DO BANCO DE DADOS LOCAL
connection = sqlite3.connect(':memory:')  # You can replace ':memory:' with your actual database file path
cursor = connection.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        descricao TEXT NOT NULL,
        price REAL NOT NULL
    );
''')

url_primeira_pagina = retornar_url_inicial()
resposta = requests.get(url_primeira_pagina)
soup = BeautifulSoup(resposta.text, 'html.parser')

# Não estamos incluindo a foto do produto, somente a parte de texto de cada item
tag_da_sessao_de_todos_os_produtos = soup.find('section', class_="ui-search-results ui-search-results--without-disclaimer") 
descricao_completa_do_produto = tag_da_sessao_de_todos_os_produtos.find_all('div', class_="ui-search-result__content-wrapper") 

for produto in descricao_completa_do_produto:
    descricao = produto.find('a', class_="ui-search-item__group__element ui-search-link")
    preco = produto.find('span', class_="andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript")
    # Insert data into the 'products' table
    try: 
        inserir_dados(descricao.text, float(preco.text.replace('R$', '').replace('.', '').replace(',', '.')))
    except:
        print('Produto não pôde ser adicionado.')

# Requerendo os dados do banco 
cursor.execute("SELECT * FROM products;")
result = cursor.fetchall()

# Commit changes and close connection
connection.commit()
connection.close()

# Fazendo a média dos preços de venda dos itens mais relevantes
lista_de_preco_dos_produtos_buscados = list(map(retornar_apenas_os_precos, result))
media_preco_produtos = retornar_media_aritmetica(lista_de_preco_dos_produtos_buscados)

app = Flask(__name__)

@app.route('/inicio')
def ola():
    return render_template('lista.html', titulo='Produtos', result=result)

app.run()