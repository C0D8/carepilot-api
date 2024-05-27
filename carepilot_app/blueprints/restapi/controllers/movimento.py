# flask imports
from flask_restx import Resource, Namespace
from carepilot_app.extensions.auth import auth
from carepilot_app.blueprints.restapi.services.movimento import get_movimentos, get_movimento, post_movimento, update_movimento, delete_movimento
from carepilot_app.blueprints.restapi.services.produto import get_all_produtos
from flask_restx import fields
from flask import request
import pandas as pd
import numpy as np
# ml imports
import pandas as pd
from sklearn.cluster import KMeans
import joblib
import time
import numpy as np
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

api = Namespace('movimentos', description='Movimentos operations')

def tratamento_de_dados(movimentos):
    movimentos['data'] = pd.to_datetime(movimentos["data"], format="%Y-%m-%d")
    movimentos['valor'] = movimentos['valor'].astype(float)
    movimentos['valor'] = movimentos['valor'].fillna(0)

    df_2023 = movimentos[movimentos['data'].dt.year == 2023]

    df_first_8_months = df_2023[df_2023['data'].dt.month <= 8]
    df_last_4_months = df_2023[(df_2023['data'].dt.month > 8)]
    # Create a dataframe with CustomerID and customers last purchase 
    # date in the dataset ctm_bhvr_dt
    last_purchase_8 = df_first_8_months.groupby('cliente_id').data.max().reset_index()
    last_purchase_8.columns = ['cliente_id', 'max_date_first']
    first_purchase_4 = df_last_4_months.groupby('cliente_id').data.min().reset_index()
    first_purchase_4.columns = ['cliente_id', 'min_date_last']

    merged_df = pd.merge(first_purchase_4, last_purchase_8, on='cliente_id', how='left')
    
    merged_df['next_purchase'] = (merged_df['min_date_last'] - merged_df['max_date_first']).dt.days

    merged_df['recency'] = first_purchase_4['min_date_last'].max() - first_purchase_4['min_date_last']

    # Assuming the merged_df DataFrame contains the recency column
    X = merged_df[['recency']]
    kmeans = KMeans(n_clusters=3)

    # Fit the data to the KMeans algorithm
    kmeans.fit(X)
    #save kmeans recency 
    joblib.dump(kmeans, 'kmeans_recency.joblib')

    # Add the cluster labels as a new column in the DataFrame
    merged_df['r_cluster'] = kmeans.labels_

    # Count the number of entries for each unique cliente_id
    count_df = movimentos['cliente_id'].value_counts().reset_index()

    # Rename the columns
    count_df.columns = ['cliente_id', 'count']

    # Display the count dataframe
    merged_df = merged_df.merge(count_df, on='cliente_id', how='left')
    merged_df.rename(columns={'count': 'frequency'}, inplace=True)

    # Assuming the merged_df DataFrame contains the recency column
    X = merged_df[['frequency']]

    # Create an instance of the KMeans algorithm with the desired number of clusters
    kmeans = KMeans(n_clusters=3)

    # Fit the data to the KMeans algorithm
    kmeans.fit(X)
    #save kmeans frequency
    joblib.dump(kmeans, 'kmeans_frequency.joblib')

    # Add the cluster labels as a new column in the DataFrame
    merged_df['f_cluster'] = kmeans.labels_

    revenues = movimentos.groupby('cliente_id').valor.sum().reset_index()
    merged_df = pd.merge(
        merged_df, revenues, on='cliente_id'
    )

    # Assuming the merged_df DataFrame contains the recency column
    
    X = merged_df[['valor']]

    # Create an instance of the KMeans algorithm with the desired number of clusters
    kmeans = KMeans(n_clusters=3)

    # Fit the data to the KMeans algorithm
    kmeans.fit(X)
    # Save the model to a file
    joblib.dump(kmeans, 'vt_kmeans.joblib')

    # Add the cluster labels as a new column in the DataFrame
    merged_df['vt_cluster'] = kmeans.labels_

    merged_df['overall_score'] = merged_df['f_cluster'] + merged_df['r_cluster'] + merged_df['vt_cluster']

    merged_df['segment'] = 'low'
    merged_df.loc[merged_df["overall_score"] >= 2, "segment"] = 'mid'
    merged_df.loc[merged_df["overall_score"] > 3, "segment"] = 'high'

    return merged_df


item = api.model('Movimento', {
    
    'valor': fields.Float(required=True, description='The value'),
    'data': fields.Date(required=True, description='The date'),
    'descricao': fields.String(required=True, description='The description'),
    'cliente_id': fields.Integer(required=True, description='The client id'),
    'produto_id': fields.Integer(required=True, description='The product id')

})

update_item = api.model('Movimento', {
    'valor': fields.Float(required=False, description='The value'),
    'data': fields.Date(required=False, description='The date'),
    'descricao': fields.String(required=False, description='The description'),
    'cliente_id': fields.Integer(required=False, description='The client id'),
    'produto_id': fields.Integer(required=False, description='The product id')
})

@api.route('')
class Movimentos(Resource):

    @auth.login_required(role='admin')
    def get(self):
        return get_movimentos()
    
    @auth.login_required(role='admin')
    @api.expect(item)
    def post(self):
        movimento_json = request.get_json()
        print(movimento_json)
        return post_movimento(movimento_json)


@api.route('/<int:movimento_id>')
class Movimento(Resource):

    @auth.login_required(role='admin')
    def get(self, movimento_id): 
        return get_movimento(movimento_id)
    
    @auth.login_required(role='admin')
    def delete(self, movimento_id):
        return delete_movimento(movimento_id)
    
    @auth.login_required(role='admin')
    @api.expect(update_item)
    def put(self, movimento_id):
        movimento_json = request.get_json()
        return update_movimento(movimento_id, movimento_json)
    
   
@api.route('/intervalo')
class MovimentoIntervalo(Resource):

    @auth.login_required(role='admin')
    def get(self):
        movimentos = get_movimentos()
        df = pd.DataFrame(movimentos)
        print(df.head())
        # Drop rows where cliente_id is equal to 1
        df = df[df['cliente_id'] != 1]
        # Convertendo a data de documento para datetime
        df['data'] = pd.to_datetime(df['data'], format="%Y-%m-%d")

        # Count the number of unique dates for each client
        date_counts = df.groupby('cliente_id')['data'].nunique()
        valid_clients = date_counts[date_counts >= 1].index

        # Filter the dataframe to keep only the valid clients
        df = df[df['cliente_id'].isin(valid_clients)]

        # Calculate the maximum time difference between data dates for each group
        df['time_diff'] = df.groupby('cliente_id')['data'].diff().dt.days
        df['max_time_diff'] = df.groupby('cliente_id')['time_diff'].transform('max')
        print(df.head())
        # Get the maximum time difference for each client
        max_time_diff = df.groupby('cliente_id')['max_time_diff'].first()

        return max_time_diff.tolist()

@api.route('/train')
class MovimentoTrain(Resource):
    @auth.login_required(role='admin')
    def get(self):
        movimentos = get_movimentos()
        movimentos = pd.DataFrame(movimentos)
        movimentos = movimentos[['cliente_id', 'valor', 'produto_id', 'data', 'quantidade']]
        merged_df = tratamento_de_dados(movimentos)
        mcopy = merged_df.copy(deep=True)
        mcopy = pd.get_dummies(mcopy)

        mcopy = mcopy.dropna(subset=['next_purchase'])

        mcopy['next_purchase_day_range'] = 1  # Inicialize com um valor padrão

        # Ajuste os intervalos de forma ordenada e sem sobreposição
        mcopy.loc[mcopy.next_purchase > 90, "next_purchase_day_range"] = 0
        mcopy.loc[(mcopy.next_purchase > 60) & (mcopy.next_purchase <= 90), "next_purchase_day_range"] = 4
        mcopy.loc[(mcopy.next_purchase > 30) & (mcopy.next_purchase <= 60), "next_purchase_day_range"] = 3
        mcopy.loc[(mcopy.next_purchase > 15) & (mcopy.next_purchase <= 30), "next_purchase_day_range"] = 2
        mcopy.loc[(mcopy.next_purchase > 10) & (mcopy.next_purchase <= 15), "next_purchase_day_range"] = 1

        mcopy = mcopy.drop(columns=['min_date_last', 'max_date_first'])

        mcopy['recency'] = mcopy['recency'].dt.days.astype(int)

        mcopy = mcopy.drop(columns=['next_purchase'], axis = 1)

        X, y = mcopy.drop(columns=['next_purchase_day_range'], axis = 1), mcopy.next_purchase_day_range
        
        # Split feature data X and target data y into train and test data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=None, shuffle=True)
        # print(X.info())
        
        rfc = RandomForestClassifier(n_estimators=100, random_state=0)
        rfc.fit(X_train, y_train)
        predictions = rfc.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        print('resultadoooooo')
        print(accuracy)
        print(X.head(), y.head())

        # Convertendo as predições para um DataFrame
        predictions_df = pd.DataFrame(predictions, columns=['predictions'], index=X_test.index)

        # Concatenando X_test e as predições
        merged_df = pd.concat([X_test, predictions_df], axis=1)

        # Exibindo as primeiras linhas do DataFrame resultante
        print(merged_df.head())

        merged_df.to_csv('predictions.csv' , sep=',')
        # Save the trained RandomForestClassifier model to a file
        joblib.dump(rfc, 'rfc_model.joblib')