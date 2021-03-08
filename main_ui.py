from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash
import plotly.express as px
import pandas as pd
from csv_imports import get_final_stock_df
import sys
sys.path.append(
    '/Users/raul/anaconda3/envs/pyfinance/lib/python3.9/site-packages')
sys.path.append('/Users/raul/Downloads')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# ----------------------------------------------------------------------
# Import and clean data
df_income = pd.read_csv(
    '/Users/raul/Downloads/aapl_income_statement_annual.csv', error_bad_lines=False, index_col='Unnamed: 1')
df_balance = pd.read_csv(
    '/Users/raul/Downloads/aapl_balance_sheet_statement_full_annual.csv', index_col='date')

# stock_df = get_final_stock_df(df_income, df_balance)


# ----------------------------------------------------------------------
# app.layout

# app.layout = html.Div([
#     html.H1("Raul's Financial Findings - Python Financial Statement Analyzer",
#             style={'text-align': 'center'}),

#     dcc.Dropdown(id="slct_year",
#                  options=[
#                     {"label": 'Revenue', 'value': 'revenue'},
#                     {"label": 'EPS', 'value': 'EPS'},
#                     {"label": 'Book Value Per Share', 'value': "BVPS"},
#                     {"label": 'Debt to Equity', 'value': "Debt to Equity"}
#                  ],
#                  multi=False,
#                  value='revenue',
#                  style={
#                      'width': '40%'
#                  }

#                  ),

#     html.Div(id='output_container', children=[]),
#     html.Br(),

#     dcc.Graph(id='my_bee_map', figure={})
# ])

app.layout = html.Div([
    html.Div([
        dcc.Input(id='ticker_symbol', type='text'),
        html.Button('Submit', id='submit', n_clicks=0),
    ]),
    html.Br(),

    html.Div(id='output_container'),
    html.Br(),

    html.H1(
        "Revenue Graph",
        style={'text-align': 'center'}
    ),
    dcc.Graph(id='revenue_plot'),
    html.Br(),

    html.H1(
        "EPS Graph",
        style={'text-align': 'center'}
    ),
    dcc.Graph(id='EPS_plot'),
    html.Br(),

    html.H1(
        "BVPS Graph",
        style={'text-align': 'center'}
    ),
    dcc.Graph(id='bvps_plot'),
    html.Br(),

    html.H1(
        "Debt to Equity Graph",
        style={'text-align': 'center'}
    ),
    dcc.Graph(id='de_plot'),
    html.Br()


])


# ----------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components

@app.callback(
    [
        Output(component_id='output_container', component_property='children'),
        Output(component_id='revenue_plot', component_property='figure'),
        Output(component_id='EPS_plot', component_property='figure'),
        Output(component_id='bvps_plot', component_property='figure'),
        Output(component_id='de_plot', component_property='figure')
    ],
    [
        Input(component_id='submit', component_property='n_clicks')
    ],
    [
        dash.dependencies.State('ticker_symbol', 'value')
    ]
)
def update_graph(option_slctd, value):
    # print(option_slctd)
    # print(type(option_slctd))

    container = f"The stock chosen by user was : {value}"

    stock_income_statement = pd.read_csv(
        f'https://fmpcloud.io/api/v3/income-statement/{value}?datatype=csv&apikey={apikey}', error_bad_lines=False, index_col='Unnamed: 1')
    stock_balance_sheet = pd.read_csv(
        f'https://fmpcloud.io/api/v3/balance-sheet-statement-shorten/{value}?datatype=csv&apikey={apikey}', index_col='date')

    stock_df = get_final_stock_df(stock_income_statement, stock_balance_sheet)

    # Plotly Express
    fig = px.line(
        data_frame=stock_df,
        y=stock_df['revenue']
    )

    fig2 = px.line(
        data_frame=stock_df,
        y=stock_df['EPS']
    )

    fig3 = px.line(
        data_frame=stock_df,
        y=stock_df['BVPS']
    )

    fig4 = px.line(
        data_frame=stock_df,
        y=stock_df['Debt to Equity']
    )

    return container, fig, fig2, fig3, fig4


if __name__ == '__main__':
    app.run_server(debug=False, host='192.168.1.2', port='5000')
