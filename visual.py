import mysql.connector
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
 
# Connect to MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Harsh98321234@",
    database="xxx4"
)
 
# Read data from MySQL into DataFrames
df = pd.read_sql_query("SELECT * FROM transactions", con=conn)
df1 = pd.read_sql_query("SELECT * FROM users", con=conn)
 
# Data processing for banking management system dashboard
df['transaction_date'] = pd.to_datetime(df['transaction_date'])
df['hour'] = df['transaction_date'].dt.hour
hourly_transactions = df['hour'].value_counts().sort_index()
pivot = df.pivot_table(values='exchange_rate', index='hour', columns='transaction_date', aggfunc='mean')
 
# Data processing for user analytics dashboard
country_counts = df1['country_of_residence'].value_counts()
df1['email_provider'] = df1['email'].apply(lambda x: x.split('@')[1])
email_provider_counts = df1['email_provider'].value_counts()
 
# Function to categorize time of day
def categorize_time(hour):
    if 0 <= hour < 6:
        return 'Night'
    elif 6 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 18:
        return 'Afternoon'
    else:
        return 'Evening'
 
df['time_of_day'] = df['hour'].apply(categorize_time)
transaction_volume_by_time = df['time_of_day'].value_counts().sort_index()
 
# Dash app initialization
app = dash.Dash(__name__)
 
# Define layout
app.layout = html.Div([
    html.H1("Banking Management and User Analytics Dashboard"),
 
    # Banking Management System Dashboard Components
    html.Div([
        html.H2("Banking Management System Dashboard"),
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
        dcc.Graph(id='transaction-volume-over-time',
                  figure={
                      'data': [
                          {'x': transaction_volume_by_time.index, 'y': transaction_volume_by_time.values, 'type': 'line', 'name': 'Transaction Volume Over Time'},
                      ],
                      'layout': {
                          'title': 'Transaction Volume Over Time',
                          'xaxis': {'title': 'Time of Day'},
                          'yaxis': {'title': 'Number of Transactions'},
                      }
                  }),
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
 
    # User Analytics Dashboard Components
    html.Div([
        html.H2("User Analytics Dashboard"),
        dcc.Graph(id='country-bar',
                  figure={
                      'data': [
                          {'x': country_counts.index, 'y': country_counts.values, 'type': 'bar', 'name': 'Country of Residence'}
                      ],
                      'layout': {
                          'title': 'User Distribution by Country',
                          'xaxis': {'title': 'Country of Residence'},
                          'yaxis': {'title': 'Number of Users'}
                      }
                  }),
        dcc.Graph(id='country-pie',
                  figure={
                      'data': [
                          {'labels': country_counts.index, 'values': country_counts.values, 'type': 'pie', 'name': 'Country of Residence'}
                      ],
                      'layout': {
                          'title': 'User Distribution by Country',
                      }
                  }),
        dcc.Graph(id='email-provider-bar',
                  figure={
                      'data': [
                          {'x': email_provider_counts.index, 'y': email_provider_counts.values, 'type': 'bar', 'name': 'Email Provider'}
                      ],
                      'layout': {
                          'title': 'Email Providers Distribution',
                          'xaxis': {'title': 'Email Provider'},
                          'yaxis': {'title': 'Number of Users'}
                      }
                  }),
    ]),
])
 
if __name__ == '__main__':
    app.run_server(debug=True)