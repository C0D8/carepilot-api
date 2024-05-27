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

    # Create a new column to represent the month number in the overall dataset
    movimentos['month_num'] = ((movimentos['data'].dt.year - movimentos['data'].dt.year.min()) * 12 + 
                            movimentos['data'].dt.month)
    # print(movimentos['month_num'])
    # print('original df')
    # print(movimentos.info())
    movimentos = movimentos.sort_values('month_num')
    # Split the data based on the calculated month numbers
    # filter the first half of the dataframe by amount of rows
    df_first_half_months = movimentos[:len(movimentos)//4]
    df_last_half_months = movimentos[len(movimentos)//4:]
    # print('first half')
    # print(df_first_half_months.head(10))

    # print('second half')
    # print(df_last_half_months.head(10))

    print()
    # previous code
    # df_2023 = movimentos[movimentos['data'].dt.year == 2023]
    # print(df_2023.info())
    # df_first_half_months = df_2023[df_2023['data'].dt.month <= 8]
    # df_last_half_months = df_2023[(df_2023['data'].dt.month > 8)]
    ##


    last_purchase = df_last_half_months.groupby('cliente_id').data.max().reset_index()
    last_purchase.columns = ['cliente_id', 'max_date_first']
    first_purchase = df_first_half_months.groupby('cliente_id').data.min().reset_index()
    first_purchase.columns = ['cliente_id', 'min_date_last']
    
    print('first_purchase')
    print(first_purchase.head(10))
    print('last_purchase')
    print(last_purchase.head(10))
    print()
    # drop the clients on last purchase that do not appear on the first
    last_purchase = last_purchase[last_purchase['cliente_id'].isin(first_purchase['cliente_id'])]
    # create rows on last_purchase with valor = 0, data = now(), produto id = -1 quantidade = 0, month num = 0 and cliente_id equals to whatever is on the first but not on the second
    missing_clients = first_purchase[~first_purchase['cliente_id'].isin(last_purchase['cliente_id'])]
    missing_clients = missing_clients.drop('min_date_last', axis=1)
    missing_clients['max_date_first'] = first_purchase["min_date_last"]
    print('missing clients')
    print(missing_clients.head())
    last_purchase = pd.concat([last_purchase, missing_clients], ignore_index=True)

    print("first_purchase\n")
    print(first_purchase.head())
    print(first_purchase.info())
    
    print('last purchase\n')
    print(last_purchase.head())
    print(last_purchase.info())
    print()

    merged_df = pd.merge(first_purchase, last_purchase, on='cliente_id', how='left')
    print('merged df')
    print(merged_df.head())
    print(merged_df.info())
    print()
    merged_df['next_purchase'] = (merged_df['min_date_last'] - merged_df['max_date_first']).dt.days ## pau

    merged_df['recency'] = first_purchase['min_date_last'].max() - first_purchase['min_date_last']

    # Assuming the merged_df DataFrame contains the recency column
    X = merged_df[['recency']]

    # Create an instance of the KMeans algorithm with the desired number of clusters
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

        corr_metrics = mcopy[mcopy.columns].corr()
        corr_df = pd.DataFrame(corr_metrics.min())
        corr_df.columns = ['min_corr_coef']
        corr_df['max_corr_coef'] = corr_metrics[corr_metrics < 1].max()

        mcopy = mcopy.drop(columns=['min_date_last', 'max_date_first'])

        mcopy['recency'] = mcopy['recency'].dt.days.astype(int)

        mcopy = mcopy.drop(columns=['next_purchase'], axis = 1)

        X, y = mcopy.drop(columns=['next_purchase_day_range'], axis = 1), mcopy.next_purchase_day_range
        # X.to_csv('models/data/X.csv', sep=';', index=False)
        # y.to_csv('models/data/y.csv', sep=';', index=False)
        
        # Split feature data X and target data y into train and test data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=None, shuffle=True)
        # print(X.info())
        
        rfc = RandomForestClassifier(n_estimators=100, random_state=0)
        rfc.fit(X_train, y_train)
        predictions = rfc.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        print('resultadoooooo')
        print(accuracy)

        pred = rfc.predict(X)
        # merge pred with X again
        merged_df['predicted_range'] = pred
        merged_df = pd.concat([X, merged_df['predicted_range']], axis=1)
        merged_df.to_csv('predictions.csv', index = False)
        joblib.dump(rfc, 'rfc.joblib')