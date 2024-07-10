import mysql.connector
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
 
# Connect to the MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Harsh98321234@",
    database="xxx4"
)
 
# Read data from the MySQL database into a DataFrame
df = pd.read_sql_query("SELECT * FROM transactions", con=conn)
 
# Convert transaction_date to datetime
df['transaction_date'] = pd.to_datetime(df['transaction_date'])
df['hour'] = df['transaction_date'].dt.hour
 
# Generate hourly transactions data
hourly_transactions = df['hour'].value_counts().sort_index()
 
# Create pivot table for heatmap
pivot = df.pivot_table(values='exchange_rate', index='hour', columns='transaction_date', aggfunc='mean')
 
# Dash app initialization
app = dash.Dash(__name__)
 
# Define layout of the dashboard
app.layout = html.Div([
    html.H1("Banking Management System Dashboard"),
   
    html.Div([
        dcc.Graph(id='hourly-transactions',
                  figure={
                      'data': [
                          {'x': hourly_transactions.index, 'y': hourly_transactions.values, 'type': 'bar', 'name': 'Hourly Transactions'},
                      ],
                      'layout': {
                          'title': 'Number of Transactions Per Hour',
                          'xaxis': {'title': 'Hour of the Day'},
                          'yaxis': {'title': 'Number of Transactions'},
                      }
                  }),
    ]),
   
    html.Div([
        dcc.Graph(id='transaction-volume-over-time',
                  figure={
                      'data': [
                          {'x': df['transaction_date'], 'y': df['transaction_date'].value_counts().sort_index(), 'type': 'line', 'name': 'Transaction Volume Over Time'},
                      ],
                      'layout': {
                          'title': 'Transaction Volume Over Time',
                          'xaxis': {'title': 'Transaction Date'},
                          'yaxis': {'title': 'Number of Transactions'},
                      }
                  }),
    ]),
   
    html.Div([
        dcc.Graph(id='sender-vs-receiver-transactions',
                  figure={
                      'data': [
                          {'x': df['sender_id'], 'y': df['receiver_id'], 'mode': 'markers', 'marker': {'size': df['amount']/100, 'opacity': 0.5}, 'type': 'scatter', 'name': 'Sender vs Receiver Transactions'},
                      ],
                      'layout': {
                          'title': 'Sender vs Receiver Transactions',
                          'xaxis': {'title': 'Sender ID'},
                          'yaxis': {'title': 'Receiver ID'},
                      }
                  }),
    ]),
   
    html.Div([
        dcc.Graph(id='histogram-converted-amounts',
                  figure={
                      'data': [
                          {'x': df['converted_amount'], 'type': 'histogram', 'name': 'Histogram of Converted Amounts'},
                      ],
                      'layout': {
                          'title': 'Histogram of Converted Amounts',
                          'xaxis': {'title': 'Converted Amount'},
                          'yaxis': {'title': 'Frequency'},
                      }
                  }),
    ]),
   
    html.Div([
        dcc.Graph(id='exchange-rate-heatmap',
                  figure={
                      'data': [
                          {'z': pivot.values, 'x': pivot.columns, 'y': pivot.index, 'type': 'heatmap', 'colorscale': 'Viridis', 'name': 'Exchange Rate Heatmap'},
                      ],
                      'layout': {
                          'title': 'Exchange Rate Heatmap by Hour and Date',
                          'xaxis': {'title': 'Transaction Date'},
                          'yaxis': {'title': 'Hour of Day'},
                      }
                  }),
    ]),
])
 
if __name__ == '__main__':
    app.run_server(debug=True)
 