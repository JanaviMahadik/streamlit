import dash
from dash import dcc 
from dash import html
from selenium import webdriver
from selenium.webdriver.edge.service import Service
import requests
import bs4
import time
import numpy as np

app = dash.Dash(__name__)

def setup_driver():
    path = "C:\\edgedriver_win64\\msedgedriver.exe"
    service = Service(executable_path=path)
    driver = webdriver.Edge(service=service)
    return driver

def scrape_screener_data(symbol, driver):
    url = f" https://www.screener.in/company/NESTLEIND/"
    driver.get(url)
    time.sleep(3)

    soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
    
    current_pe = fy23_pe = median_roce = sales_growth_ttm = sales_growth_3yr = sales_growth_5yr = sales_growth_10yr = 1
    
    current_pe_tag = soup.find('td', text='Current PE')
    if current_pe_tag:
        current_pe = current_pe_tag.find_next('td').text
    
    fy23_pe_tag = soup.find('td', text='FY23 PE')
    if fy23_pe_tag:
        fy23_pe = fy23_pe_tag.find_next('td').text
    
    median_roce_tag = soup.find('td', text='Median RoCE')
    if median_roce_tag:
        median_roce = median_roce_tag.find_next('td').text
    
    sales_growth_ttm_tag = soup.find('td', text='Sales Growth (TTM)')
    if sales_growth_ttm_tag:
        sales_growth_ttm = sales_growth_ttm_tag.find_next('td').text
    
    sales_growth_3yr_tag = soup.find('td', text='Sales Growth (3Yr)')
    if sales_growth_3yr_tag:
        sales_growth_3yr = sales_growth_3yr_tag.find_next('td').text
    
    sales_growth_5yr_tag = soup.find('td', text='Sales Growth (5Yr)')
    if sales_growth_5yr_tag:
        sales_growth_5yr = sales_growth_5yr_tag.find_next('td').text
    
    sales_growth_10yr_tag = soup.find('td', text='Sales Growth (10Yr)')
    if sales_growth_10yr_tag:
        sales_growth_10yr = sales_growth_10yr_tag.find_next('td').text
    
    return current_pe, fy23_pe, median_roce, sales_growth_ttm, sales_growth_3yr, sales_growth_5yr, sales_growth_10yr

def calculate_intrinsic_pe(current_pe, fy23_pe, cost_of_capital, roce, growth_high_period, high_growth_years, fade_years, terminal_growth_rate):
    
    if fy23_pe != "N/A":
        fy23_pe = float(fy23_pe)
    else:
        fy23_pe = 0.0  
    
    if current_pe != "N/A":
        current_pe = float(current_pe)
    else:
        current_pe = 0.0  
    
    if fy23_pe != "N/A":
        intrinsic_pe = (fy23_pe * (1 + terminal_growth_rate)) / (cost_of_capital - terminal_growth_rate)
    else:
        intrinsic_pe = 0.0  
    
    if intrinsic_pe != "N/A":
        degree_of_overvaluation = (current_pe - intrinsic_pe) / intrinsic_pe * 100
    else:
        degree_of_overvaluation = 0.0

    return intrinsic_pe, degree_of_overvaluation

app.layout = html.Div([
    dcc.Input(id='symbol', value='NESTLEIND', type='text', placeholder='Enter NSE/BSE symbol (e.g., NESTLEIND)'),
    dcc.Slider(
        id='cost_of_capital',
        min=8,
        max=16,
        value=8,
        marks={i: str(i) for i in range(8, 17, 2)}
    ),
    dcc.Slider(
        id='roce',
        min=10,
        max=100,
        value=10,
        step=10,
        marks={i: str(i) for i in range(10, 110, 10)}
    ),
    dcc.Slider(
        id='growth_high_period',
        min=8,
        max=20,
        value=8,
        step=2,
        marks={i: str(i) for i in range(8, 21, 2)}
    ),
    dcc.Slider(
        id='high_growth_years',
        min=8,
        max=25,
        value=8,
        step=2,
        marks={i: str(i) for i in range(8, 26, 2)}
    ),
    dcc.Slider(
        id='fade_years',
        min=5,
        max=20,
        value=5,
        step=5,
        marks={i: str(i) for i in range(5, 21, 5)}
    ),
    dcc.Slider(
        id='terminal_growth_rate',
        min=1,
        max=7,
        value=1,
        step=1,
        marks={i: str(i) for i in range(1, 8)}
    ),
    html.Div(id='output')
])

@app.callback(
    dash.dependencies.Output('output', 'children'),
    [
        dash.dependencies.Input('symbol', 'value'),
        dash.dependencies.Input('cost_of_capital', 'value'),
        dash.dependencies.Input('roce', 'value'),
        dash.dependencies.Input('growth_high_period', 'value'),
        dash.dependencies.Input('high_growth_years', 'value'),
        dash.dependencies.Input('fade_years', 'value'),
        dash.dependencies.Input('terminal_growth_rate', 'value')
    ]
)
def update_output(symbol, cost_of_capital, roce, growth_high_period, high_growth_years, fade_years, terminal_growth_rate):
    driver = setup_driver()
    current_pe, fy23_pe, median_roce, sales_growth_ttm, sales_growth_3yr, sales_growth_5yr, sales_growth_10yr = scrape_screener_data(symbol, driver)
    intrinsic_pe, degree_of_overvaluation = calculate_intrinsic_pe(current_pe, fy23_pe, cost_of_capital, roce, growth_high_period, high_growth_years, fade_years, terminal_growth_rate)
    return [
        html.H6('Current PE: {}'.format(current_pe)),
        html.H6('FY23 PE: {}'.format(fy23_pe)),
        html.H6('5-yr Median RoCE: {}'.format(median_roce)),
        html.H6('Compounded Sales Growth (TTM): {}'.format(sales_growth_ttm)),
        html.H6('Compounded Sales Growth (3yr): {}'.format(sales_growth_3yr)),
        html.H6('Compounded Sales Growth (5yr): {}'.format(sales_growth_5yr)),
        html.H6('Compounded Sales Growth (10yr): {}'.format(sales_growth_10yr)),
        html.H6('Intrinsic PE: {}'.format(intrinsic_pe)),
        html.H6('Degree of Overvaluation: {}%'.format(degree_of_overvaluation))
    ]

if __name__ == '__main__':
    app.run_server(port=8054, debug=True)
