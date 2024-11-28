import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load and preprocess data
data = pd.read_csv('ecommerce_dataset_updated.csv')
data['Purchase_Date'] = pd.to_datetime(data['Purchase_Date'], format='%d-%m-%Y')
data['Month'] = data['Purchase_Date'].dt.to_period('M')

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the dashboard
app.layout = html.Div([
    html.H1("E-commerce Sales Dashboard", style={'textAlign': 'center'}),
    
    html.Div([
        dcc.DatePickerRange(
            id='date-range',
            start_date=data['Purchase_Date'].min(),
            end_date=data['Purchase_Date'].max(),
            display_format='YYYY-MM-DD',
            style={'padding': '10px'}
        ),
        dcc.Dropdown(
            id='category-filter',
            options=[{'label': category, 'value': category} for category in data['Category'].unique()],
            placeholder="Select Product Category",
            multi=True,
            style={'width': '300px', 'padding': '10px'}
        ),
    ], style={'display': 'flex', 'justify-content': 'center'}),

    html.Div([
        html.Div(id='kpi-total-sales', className='kpi-box'),
        html.Div(id='kpi-total-orders', className='kpi-box'),
        html.Div(id='kpi-avg-order-value', className='kpi-box')
    ], style={'display': 'flex', 'justify-content': 'space-around'}),

    dcc.Graph(id='bar-chart'),
    dcc.Graph(id='line-chart'),
    dcc.Graph(id='pie-chart'),

    html.H2("Detailed Purchase Data"),
    dcc.Graph(id='table-data')
])

# Callbacks for interactivity
@app.callback(
    [Output('bar-chart', 'figure'),
     Output('line-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('kpi-total-sales', 'children'),
     Output('kpi-total-orders', 'children'),
     Output('kpi-avg-order-value', 'children'),
     Output('table-data', 'figure')],
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('category-filter', 'value')]
)
def update_dashboard(start_date, end_date, selected_categories):
    filtered_data = data[(data['Purchase_Date'] >= start_date) & (data['Purchase_Date'] <= end_date)]
    if selected_categories:
        filtered_data = filtered_data[filtered_data['Category'].isin(selected_categories)]

    total_sales = filtered_data['Final_Price(Rs.)'].sum()
    total_orders = len(filtered_data)
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0

    bar_fig = px.bar(filtered_data.groupby('Category')['Final_Price(Rs.)'].sum().reset_index(),
                     x='Category', y='Final_Price(Rs.)', title='Total Sales by Category')

    line_fig = px.line(filtered_data.groupby('Month')['Final_Price(Rs.)'].sum().reset_index(),
                       x='Month', y='Final_Price(Rs.)', title='Sales Trend Over Time')

    pie_fig = px.pie(filtered_data.groupby('Category')['Final_Price(Rs.)'].sum().reset_index(),
                     names='Category', values='Final_Price(Rs.)', title='Sales Distribution by Category')

    table_fig = px.bar(filtered_data, x='Purchase_Date', y='Final_Price(Rs.)', color='Category',
                       title='Sales by Category and Date')

    return bar_fig, line_fig, pie_fig, f'Total Sales: Rs. {total_sales:.2f}', f'Total Orders: {total_orders}', f'Average Order Value: Rs. {avg_order_value:.2f}', table_fig

if __name__ == '__main__':
    app.run_server(debug=True)
