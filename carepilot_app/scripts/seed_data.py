from carepilot_app.extensions.db import db
import pandas as pd
from carepilot_app.models.cliente import Cliente
from carepilot_app.models.produto import Produto
from carepilot_app.models.movimento import Movimento

def seed_data(df):

    Movimento.delete_all()
    Cliente.delete_all()
    Produto.delete_all()
    

    df['valor_total'] = df['valor_total'].str.replace(',', '.').astype(float)

    #converter data para o formato do banco

    df['data'] = pd.to_datetime(df['data']).dt.strftime('%Y-%m-%d')


    #criar clientes
    clientes_unicos = df['cliente_id'].unique()
    #quantidade de movimentos
    quantidade = df['cliente_id'].value_counts()
    #valor total
    valor_total = df.groupby('cliente_id')['valor_total'].sum()

    # Crie um DataFrame com os códigos dos clientes únicos
    df_clientes = pd.DataFrame(clientes_unicos, columns=['id'])
    df_clientes['quantidade'] = quantidade.values
    df_clientes['valor_total'] = valor_total.values
    

    print("CLIENTESSSSS")
    print(df_clientes)

    df_clientes.to_sql('cliente', con=db.engine, if_exists='append', index=False)

    # criar produtos
    produtos = df['produto_id'].unique()



    # # Crie uma lista ou dicionário para armazenar os dados
    dados = []

    # Iterar através dos produtos para calcular o valor unitário
    for produto in produtos:
        movimento_produto = df[df['produto_id'] == produto].iloc[0]
        # Calcular o valor unitário
        valor_unitario = movimento_produto['valor_total'] / movimento_produto['quantidade']
        
        # Adicione o código do produto e o valor unitário à lista
        dados.append({'id': produto, 'valor': valor_unitario})

    # Converta a lista de dicionários em um DataFrame
    df_valores_unitarios = pd.DataFrame(dados)

    df_valores_unitarios.to_sql('produto', con=db.engine, if_exists='append', index=False)

    #criar movimentos
    #trocar nome da coluna valor_total para valor
    df.rename(columns={'valor_total': 'valor'}, inplace=True)

    df.to_sql('movimento', con=db.engine, if_exists='append', index=False)





    

    # #inserir movimentos

