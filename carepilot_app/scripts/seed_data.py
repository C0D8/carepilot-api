from carepilot_app.extensions.db import db
import pandas as pd
from carepilot_app.models.cliente import Cliente
from carepilot_app.models.produto import Produto
from carepilot_app.models.movimento import Movimento
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from datetime import datetime
def seed_data(df, user_id):
    Session = sessionmaker(bind=db.engine)
    session = Session()

    try:
        # Deleting existing records for the user
        session.query(Movimento).filter_by(user_id=user_id).delete()
        session.query(Produto).filter_by(user_id=user_id).delete()
        session.query(Cliente).filter_by(user_id=user_id).delete()
        session.commit()  # Commit the deletions

        # Convert 'valor_total' to float and 'data' to proper date format
        df['valor_total'] = df['valor_total'].str.replace(',', '.').astype(float)
        df['data'] = pd.to_datetime(df['data']).dt.strftime('%Y-%m-%d')

        # Create clients
        clientes_unicos = df['cliente_id'].unique()
        dados_clientes = []

        for cliente in clientes_unicos:
            df_cliente = df[df['cliente_id'] == cliente]
            quantidade_datas = df_cliente['data'].nunique()
            valor_total = df_cliente['valor_total'].sum()
            nome_cliente = df_cliente['nome_cliente'].iloc[0] if 'nome_cliente' in df.columns else None
            dados_clientes.append({
                'id': cliente,
                'quantidade': quantidade_datas,
                'valor_total': valor_total,
                'user_id': user_id,
                'nome': nome_cliente
            })

        df_clientes = pd.DataFrame(dados_clientes)
        print(df_clientes)

        df_clientes.to_sql('cliente', con=db.engine, if_exists='append', index=False)

        # Create products
        produtos = df['produto_id'].unique()
        dados_produtos = []

        for produto in produtos:
            movimento_produto = df[df['produto_id'] == produto].iloc[0]
            valor_unitario = movimento_produto['valor_total'] / movimento_produto['quantidade']
            nome_produto = movimento_produto['descricao'] if 'descricao' in df.columns else 'Sem nome'
            tipo_produto = movimento_produto['tipo_produto'] if 'tipo_produto' in df.columns else 'Sem tipo'
            dados_produtos.append({
                'id': produto,
                'valor': valor_unitario,
                'user_id': user_id,
                'descricao': nome_produto,
                'tipo': tipo_produto,
                'data' : datetime.now().strftime('%Y-%m-%d')
            })

        
        print(dados_produtos)
        df_produtos = pd.DataFrame(dados_produtos)
        # df_produtos.rename(columns={'tipo_produto': 'tipo'}, inplace=True)
        df_produtos.to_sql('produto', con=db.engine, if_exists='append', index=False)

        # Create movements
        df.rename(columns={'valor_total': 'valor'}, inplace=True)
        df['user_id'] = user_id
        print(df)
        #colunas para o movimento = ['data', 'quantidade', 'valor', 'cliente_id', 'produto_id', 'user_id']
        df = df[['data', 'quantidade', 'valor', 'cliente_id', 'produto_id', 'user_id']]
        df.to_sql('movimento', con=db.engine, if_exists='append', index=False)

        session.commit()  # Commit all changes at the end

    except OperationalError as e:
        session.rollback()
        print(f"OperationalError: {e}")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()