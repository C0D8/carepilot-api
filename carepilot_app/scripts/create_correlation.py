from carepilot_app.extensions.db import db
from carepilot_app.models.movimento import Movimento
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os

def create_correlation():

    
    movimentos = Movimento.query.all()
    df = pd.DataFrame([m.json() for m in movimentos])

    # colunas cliente_id;produto_id;quantidade;valor_total;data
    costumer_item_matrix = df.pivot_table(index='cliente_id', columns='produto_id', values='quantidade', aggfunc='sum', fill_value=0)
    
    # Create a mapping of original customer ID to a continuous customer ID
    original_to_continuous_id = {original_id: i + 1 for i, original_id in enumerate(costumer_item_matrix.index)}
    # Create a reverse mapping of continuous customer ID to the original customer ID
    continuous_to_original_id = {v: k for k, v in original_to_continuous_id.items()}
    
    # Replace the customer_id in the dataframe with the continuous ID
    costumer_item_matrix = costumer_item_matrix.rename(index=original_to_continuous_id)
    print(continuous_to_original_id[2])
    
    user_user_sim_matrix = pd.DataFrame(cosine_similarity(costumer_item_matrix))
    print(user_user_sim_matrix)
    
    # Save the similarity matrix and the two dictionaries
    user_user_sim_matrix.to_csv('./carepilot_app/data/user_user_sim_matrix.csv')
    pd.DataFrame.from_dict(original_to_continuous_id, orient='index').to_csv('./carepilot_app/data/original_to_continuous_id.csv', header=False)
    pd.DataFrame.from_dict(continuous_to_original_id, orient='index').to_csv('./carepilot_app/data/continuous_to_original_id.csv', header=False)


def get_similar_users(user_id):

    #verificar se os arquivos existem

    if not os.path.exists('./carepilot_app/data/user_user_sim_matrix.csv'):
        create_correlation()


    user_user_sim_matrix = pd.read_csv('./carepilot_app/data/user_user_sim_matrix.csv', index_col=0)
    original_to_continuous_id = pd.read_csv('./carepilot_app/data/original_to_continuous_id.csv', header=None, index_col=0).squeeze("columns").to_dict()
    continuous_to_original_id = pd.read_csv('./carepilot_app/data/continuous_to_original_id.csv', header=None, index_col=0).squeeze("columns").to_dict()
    
    similar_users = user_user_sim_matrix.iloc[original_to_continuous_id[user_id]].sort_values(ascending=False).head(10)
    # print(continuous_to_original_id.keys())
    similar_users.index = similar_users.index.map(lambda x: continuous_to_original_id[float(x)])
    
    dict_users = similar_users.to_dict()
    print(dict_users)
    return dict_users
