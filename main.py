from flask import Flask, render_template, request

import requests
from bs4 import BeautifulSoup

# BASE DE DADOS
lista_de_produtos_atual = []

# CONSTANTES
ACRESCIMO = 48
INDICE = 49

# FUNÇÕES
def retornar_media_aritmetica(lista):
    try:
        return sum(lista) / len(lista)
    except:
        print('Não foi possível calcular a média')
        return 0
def retornar_apenas_os_precos(produto):
    return produto['preco']

# def perguntar_o_produto_desejado():
#     return input('Informe o produto sobre o qual deseja obter informações: ').split()

def adequar_para_formato_da_url(separador, nome_do_produto):
    produto_com_split = nome_do_produto.split()
    return f'{separador}'.join(produto_com_split)

def retornar_url_inicial(produto_desejado):

  primeira_parte_da_url = adequar_para_formato_da_url('-', produto_desejado)
  segunda_parte_da_url = adequar_para_formato_da_url('%20', produto_desejado)

  url_da_primeira_pagina = f'https://lista.mercadolivre.com.br/{primeira_parte_da_url}#D[A:{segunda_parte_da_url}]'
  return url_da_primeira_pagina

def inserir_dados(lista, descricao, preco):
    lista.append({'descricao':descricao, 'preco':preco})

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('homepage.html', titulo='Produtos', result=lista_de_produtos_atual, media_precos = 0)

@app.route('/pesquisa', methods=['POST',])
def pesquisa():
    lista_de_produtos_atual.clear()
    produto_desejado = request.form['produto_descricao']
    url_primeira_pagina = retornar_url_inicial(produto_desejado)
    resposta = requests.get(url_primeira_pagina)
    soup = BeautifulSoup(resposta.text, 'html.parser')

    # Não estamos incluindo a foto do produto, somente a parte de texto de cada item
    tag_da_sessao_de_todos_os_produtos = soup.find('section', class_="ui-search-results ui-search-results--without-disclaimer") 
    descricao_completa_do_produto = tag_da_sessao_de_todos_os_produtos.find_all('div', class_="ui-search-result__content-wrapper") 

    for produto in descricao_completa_do_produto:
        descricao = produto.find('a', class_="ui-search-item__group__element ui-search-link")
        preco = produto.find('span', class_="andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript")

        inserir_dados(lista_de_produtos_atual, descricao.text, float(preco.text.replace('R$', '').replace('.', '').replace(',', '.')))

    # Fazendo a média dos preços de venda dos itens mais relevantes
    lista_de_preco_dos_produtos_buscados = list(map(retornar_apenas_os_precos, lista_de_produtos_atual))
    media_preco_produtos = retornar_media_aritmetica(lista_de_preco_dos_produtos_buscados)
    
    return render_template('homepage.html', titulo='Produtos', produtos=lista_de_produtos_atual, media_precos = f'{media_preco_produtos:.2f}')

if __name__ == "__main__":
    app.run()