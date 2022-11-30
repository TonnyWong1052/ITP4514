import imp
from flask import Flask,request,jsonify
from flask_cors import CORS
import numpy as np 
import pandas as pd 
pd.set_option('display.float_format', '{:.2f}'.format)
pd.set_option('display.max_rows', 100)
import matplotlib.pyplot as plt
# get_ipython().run_line_magic('matplotlib', 'inline')
import seaborn as sns
sns.set_style('darkgrid')
import warnings
warnings.filterwarnings("ignore")
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsRegressor

app = Flask(__name__)
CORS(app)

def remove_outliers(column):
    Q1 = column.quantile(.25)
    Q3 = column.quantile(.75)
    IQR = Q3 - Q1
    column = column[((Q1 - 1.5 * IQR) <= column) & (column  <= (Q3 + 1.5 * IQR))]
    return column

@app.route("/api/AIWeatherPred/<amount>",methods=['GET'])
def GetNewAmount(amount):
    train = pd.read_csv('data/dataset.csv')
    test = pd.read_csv('data/dataset_test.csv')
    test = test.iloc[1:,:]
    full_data = pd.concat((test, train), ignore_index=True) # merging the data.
    full_data['Date'] = pd.to_datetime(full_data['Date']) # making the data in datetime format.
    full_data = full_data.sort_values(by=['Date']) # sorting by date.
    fig = make_subplots(rows=8, cols=1,
                    vertical_spacing=0.1,
                    subplot_titles=('MeanPressure', 'MaxDeg', 'MeanDeg', 'MinDeg', 'Mean Dew Point', 'Mean Relative Humidity',
                                    'Mean Amount of Cloud', 'Total Rainfall'))
    fig.append_trace(go.Scatter(x=full_data['Date'], y=full_data['MeanPressure']),
                row=1, col=1)

    fig.append_trace(go.Scatter(x=full_data['Date'], y=full_data['MaxDeg']),
                row=2, col=1)

    fig.append_trace(go.Scatter(x=full_data['Date'], y=full_data['MeanDeg']),
                row=3, col=1)

    fig.append_trace(go.Scatter(x=full_data['Date'], y=full_data['MinDeg']),
                row=4, col=1)

    fig.append_trace(go.Scatter(x=full_data['Date'], y=full_data['MeanDewPoint']),
                row=5, col=1)

    fig.add_trace(go.Scatter(x=full_data['Date'], y=full_data['MeanRelativeHumidity']),
                row=6, col=1)

    fig.add_trace(go.Scatter(x=full_data['Date'], y=full_data['MeanAmountofCloud']),
                row=7, col=1)

    fig.add_trace(go.Scatter(x=full_data['Date'], y=full_data['TotalRainfall']),
                row=8, col=1)

    full_data['year'] = full_data.Date.dt.year # making year column.
    full_data['month'] = full_data.Date.dt.month # making month column.
    full_data['monthday'] = full_data.Date.dt.day # making day of month column.
    full_data['yearday'] = full_data.Date.dt.dayofyear # making day of year column.
    full_data.rename(columns={'Date':'ds'},inplace=True) # changing the date column name to "ds" for NeuralProphet model.
    for col in ["MeanRelativeHumidity" ,'TotalRainfall']:  
        full_data[col] = remove_outliers(full_data[col]) # removing the column's outliers
    full_data.dropna(inplace=True)
    # spliting the data back to train and test data.
    train = full_data.iloc[:len(train),:]
    test = full_data.iloc[len(train):,:] 

    fig = make_subplots(rows=3, cols=1,
                    vertical_spacing=0.1,
                    subplot_titles=("MeanDewPoint" ,'TotalRainfall', 'MeanPressure'))

    fig.add_trace(go.Scatter(x=full_data['ds'], y=full_data['MeanDewPoint']),
                row=1, col=1)

    fig.add_trace(go.Scatter(x=full_data['ds'], y=full_data['TotalRainfall']),
                row=2, col=1)

    fig.add_trace(go.Scatter(x=full_data['ds'], y=full_data['MeanPressure']),
                row=3, col=1)

    KNNforecasts = dict()

    for column in ['MeanPressure', 'MaxDeg', 'MeanDeg', 'MinDeg', 'MeanDewPoint','MeanRelativeHumidity','MeanAmountofCloud','TotalRainfall']:
        m = KNeighborsRegressor(n_neighbors=27)
        X = train.drop(['ds',column],axis = 1)
        y = train[column]
        model = m.fit(X,y)
        X_test = test.drop(['ds',column],axis = 1)
        forecast = m.predict(X_test)
        KNNforecasts[column] = forecast
        print(f'r2 score for {column} : {r2_score(test[column],forecast)}')

    fig = make_subplots(rows=8, cols=1, vertical_spacing=0.04,subplot_titles=('MeanPressure', 'MaxDeg', 'MeanDeg', 'MinDeg', 'MeanDewPoint', 'MeanRelativeHumidity',
                                    "MeanAmountofCloud" ,'TotalRainfall'))

    row = 1
    for col,fcst in KNNforecasts.items():
        
        fig.append_trace(go.Scatter(x=test['ds'], y=test[col],name=col),
                row=row, col=1)
        fig.append_trace(go.Scatter(x=test['ds'], y=fcst, name = col+' forecast'),
                row=row, col=1)
        row +=1
    fig.update_layout(height=3000)
    fig.show()

    amount = 1
    return jsonify({"test": "123"})

if __name__ == "__main__":
    app.run(debug=True,
            port=8000)