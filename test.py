import streamlit as st
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.edge.service import Service

def setup_driver():
    # Replace the path with the path to your web driver
    path = "C:\\edgedriver_win64\\msedgedriver.exe"
    # Choose the appropriate web driver for your browser
    service = Service(executable_path=path)
    driver = webdriver.Edge(service=service)
    return driver

def scrape_screener_data(symbol, driver):
    url = f"https://www.screener.in/company/{symbol}/consolidated/"
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
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
    
    if fy23_pe != 'N/A':
        fy23_pe = float(fy23_pe)
    else:
        fy23_pe = 0.0  
    
    if current_pe != 'N/A':
        current_pe = float(current_pe)
    else:
        current_pe = 0.0  
    
    if fy23_pe != 0:
        intrinsic_pe = (fy23_pe * (1 + terminal_growth_rate)) / (cost_of_capital - terminal_growth_rate)
    else:
        intrinsic_pe = 0.0  
    
    if intrinsic_pe != 0:
        degree_of_overvaluation = (current_pe - intrinsic_pe) / intrinsic_pe * 100
    else:
        degree_of_overvaluation = 0.0 
    
    return intrinsic_pe, degree_of_overvaluation

st.title('Reverse DCF Analysis')
symbol = st.text_input('Enter NSE/BSE symbol (e.g., NESTLEIND):', 'NESTLEIND')

driver = setup_driver()
current_pe, fy23_pe, median_roce, sales_growth_ttm, sales_growth_3yr, sales_growth_5yr, sales_growth_10yr = scrape_screener_data(symbol, driver)

cost_of_capital = st.number_input('Cost of Capital:', min_value=8, max_value=16, value=8, step=1)
roce = st.number_input('Return on Capital Employed (RoCE):', min_value=10, value=10, step=10, max_value=100)
growth_high_period = st.number_input('Growth during High Growth Period:', min_value=8, value=8, step=2, max_value=20)
high_growth_years = st.number_input('High Growth Period (years):', min_value=8, value=8, max_value=25, step=2)
fade_years = st.number_input('Fade Period (years):', min_value=5, value=5, max_value=20, step=5)
terminal_growth_rate = st.number_input('Terminal Growth Rate:', min_value=1, value=1, step=1, max_value=7)

driver.quit()

intrinsic_pe, degree_of_overvaluation = calculate_intrinsic_pe(current_pe, fy23_pe, cost_of_capital, roce, growth_high_period, high_growth_years, fade_years, terminal_growth_rate)

st.write(f'Current PE: {current_pe}')
st.write(f'FY23 PE: {fy23_pe}')
st.write(f'5-yr Median RoCE: {median_roce}')
st.write(f'Compounded Sales Growth (TTM): {sales_growth_ttm}')
st.write(f'Compounded Sales Growth (3yr): {sales_growth_3yr}')
st.write(f'Compounded Sales Growth (5yr): {sales_growth_5yr}')
st.write(f'Compounded Sales Growth (10yr): {sales_growth_10yr}')
st.write(f'Intrinsic PE: {intrinsic_pe}')
st.write(f'Degree of Overvaluation: {degree_of_overvaluation}')
