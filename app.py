import requests
import json
import yfinance as yf
from datetime import datetime
import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# This Function Is Use to download financial data
def download_financial_data(companies):
    # Connection  to SQLite database
    conn = sqlite3.connect('financial_data.db')
    cursor = conn.cursor()

    # Here Table Is Created If Table Not Exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS financial_data
                (Ticker text, Date text, Open real, Close real, Volume integer)''')


    # iterate through the companies and download financial data
    for company in companies:
        # Here We Get data from yfinance
        data = yf.download(company, start="2020-01-01", end="2023-04-01")

        # Here We Insert data into database
        for date in data.index:
            open_price = data.loc[date]['Open']
            close_price = data.loc[date]['Close']
            volume = data.loc[date]['Volume']
            cursor.execute("INSERT INTO financial_data (Ticker, Date, Open, Close, Volume) VALUES (?, ?, ?, ?, ?)", (company, date.strftime('%Y-%m-%d'), open_price, close_price, volume))

    # commit changes and close connection
    conn.commit()
    conn.close()

    print('Financial data download complete!')


# Endpoint for the root URL
@app.route('/')
def home():
    return 'Hello Welcome To The API You Can View The Data By Changing Route'


# Here API First Task Get All Stock Data for Perticular Day
@app.route('/stock-data-by-date', methods=['GET'])
def get_stock_data_by_date():
    date = request.args.get('date')
    conn = sqlite3.connect('financial_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM financial_data WHERE Date=?", (date,))
    data = cursor.fetchall()
    conn.close()
    return render_template('company_data.html', data=data, title='Stock Data of {}'.format(date))


# Here API Second Task Get all stock data for a particular company for a particular day 
@app.route('/stock-data-by-company-and-date', methods=['GET'])
def get_stock_data_by_company_and_date():
    symbol = request.args.get('symbol')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    conn = sqlite3.connect('financial_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM financial_data WHERE Ticker=? AND Date BETWEEN ? AND ?", (symbol, start_date, end_date))
    data = cursor.fetchall()
    conn.close()
    return render_template('company_data.html', data=data, title='Stock Data Of {} for {}'.format(symbol, start_date))

# Here API Third For Getting All Stock Data For A Perticular Company 
@app.route('/stock-data-by-company', methods=['GET'])
def get_stock_data_by_company():
    symbol = request.args.get('symbol')
    conn = sqlite3.connect('financial_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM financial_data WHERE Ticker=?", (symbol,))
    data = cursor.fetchall()
    conn.close()
    return render_template('company_data.html', data=data, title='Stock Data Of {}'.format(symbol))


# Here API Fourth For Update Stock Data For A Company
@app.route('/update-stock-data', methods=['POST', 'PATCH'])
def update_stock_data():
    company = request.json['company']
    date = request.json['date']
    open_price = request.json['open_price']
    close_price = request.json['close_price']
    volume = request.json['volume']
    conn = sqlite3.connect('financial_data.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE financial_data SET Open=?, Close=?, Volume=? WHERE Ticker=? AND Date=?", (open_price, close_price, volume, company, date))
    conn.commit()
    conn.close()
    return 'Stock data updated successfully'


if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)
    companies = config['companies']
    download_financial_data(companies)
    app.run(debug=True)
