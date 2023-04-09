import os
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import pandas_ta as ta
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

class StockPriceTracker(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Stock Price Tracker")
        self.geometry("450x300")

        self.create_welcome_page()
        self.create_main_page()
        self.show_welcome_page()

    def create_welcome_page(self):
        self.welcome_page = tk.Frame(self, bg='#800080')
        self.welcome_label = ttk.Label(self.welcome_page, text="Welcome to Stock Price Tracker", font=("Arial", 16))
        self.start_button = ttk.Button(self.welcome_page, text="Start", command=self.show_main_page)
        self.exit_button = ttk.Button(self.welcome_page, text="Exit", command=self.quit)

        self.welcome_label.pack(pady=(50, 0))
        self.start_button.pack(pady=(20, 0))
        self.exit_button.pack(pady=(10, 0))

    def show_welcome_page(self):
        self.main_page.pack_forget()
        self.welcome_page.pack(fill=tk.BOTH, expand=True)

    def create_main_page(self):
        self.main_page = tk.Frame(self, bg='green')
        self.stock_symbols_label = ttk.Label(self.main_page, text="Stock symbols (comma-separated):")
        self.stock_symbols_entry = ttk.Entry(self.main_page, width=40)

        self.start_date_label = ttk.Label(self.main_page, text="Start date (YYYY-MM-DD):")
        self.start_date_entry = ttk.Entry(self.main_page, width=20)

        self.end_date_label = ttk.Label(self.main_page, text="End date (YYYY-MM-DD):")
        self.end_date_entry = ttk.Entry(self.main_page, width=20)

        self.output_folder_label = ttk.Label(self.main_page, text="Output folder:")
        self.output_folder_entry = ttk.Entry(self.main_page, width=40)

        self.browse_button = ttk.Button(self.main_page, text="Browse", command=self.browse_output_folder)
        self.run_button = ttk.Button(self.main_page, text="Run", command=self.run)

        self.progress_label = ttk.Label(self.main_page, text="")
        self.message_label = ttk.Label(self.main_page, text="")

        self.layout_widgets()

    def show_main_page(self):
        self.welcome_page.pack_forget()
        self.main_page.pack(fill=tk.BOTH, expand=True)

    def layout_widgets(self):
        self.stock_symbols_label.grid(column=0, row=0, padx=10, pady=10, sticky="W")
        self.stock_symbols_entry.grid(column=1, row=0, padx=10, pady=10, columnspan=2)

        self.start_date_label.grid(column=0, row=1, padx=10, pady=10, sticky="W")
        self.start_date_entry.grid(column=1, row=1, padx=10, pady=10)

        self.end_date_label.grid(column=0, row=2, padx=10, pady=10, sticky="W")
        self.end_date_entry.grid(column=1, row=2, padx=10, pady=10)

        self.output_folder_label.grid(column=0, row=3, padx=10, pady=10, sticky="W")
        self.output_folder_entry.grid(column=1, row=3, padx=10, pady=10)
        self.browse_button.grid(column=2, row=3, padx=10, pady=10)

        self.run_button.grid(column=1, row=4, padx=10, pady=20)
        self.progress_label.grid(column=0, row=5, padx=10, pady=10, columnspan=3, sticky="W")
        self.message_label.grid(column=0, row=6, padx=10, pady=10, columnspan=3, sticky="W")

    def browse_output_folder(self):
        output_folder = filedialog.askdirectory()
        self.output_folder_entry.delete(0, tk.END)
        self.output_folder_entry.insert(0, output_folder)

    def display_stock_info(self, stock_symbols):
        for symbol in stock_symbols:
            stock = yf.Ticker(symbol)
            info = stock.info

            if 'shortName' not in info:
                print(f"Invalid or delisted stock symbol: {symbol}")
                print("")
                continue

            print(f"Stock: {info['shortName']} ({info['symbol']})")
        
            try:
                print(f"Industry: {info['industry']}")
            except KeyError:
                print("Industry: Not available")

        print("")

    def run(self):
        stock_symbols = self.stock_symbols_entry.get().split(',')
        stock_symbols = [symbol.strip() for symbol in stock_symbols]
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        output_folder = self.output_folder_entry.get()

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        self.progress_label['text'] = "Fetching stock data..."
        self.update_idletasks()

        stock_data = self.get_stock_data(stock_symbols, start_date, end_date)
        self.display_stock_info(stock_symbols)
        self.save_stock_data(stock_data, stock_symbols, output_folder)

        self.progress_label['text'] = "Plotting stock data and saving to output folder..."
        self.update_idletasks()

        for stock_symbol in stock_symbols:
            self.plot_stock_data(stock_data, stock_symbol, output_folder)

        self.progress_label['text'] = ""
        self.message_label['text'] = "Stock data and interactive plots saved to the output folder."

    def get_stock_data(self, stock_symbols, start_date, end_date):
        stock_data = {}
        for symbol in stock_symbols:
            stock_data[symbol] = yf.download(symbol, start=start_date, end=end_date)
        return stock_data

    def save_stock_data(self, stock_data, stock_symbols, output_folder):
        for symbol in stock_symbols:
            data = stock_data[symbol]
            data.to_csv(os.path.join(output_folder, f'{symbol}_stock_data.csv'))

    def plot_stock_data(self, stock_data, stock_symbol, output_folder):
        data = stock_data[stock_symbol]
        data['SMA'] = ta.sma(data['Close'], length=20)
        data['RSI'] = ta.rsi(data['Close'], length=14)

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close'))
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA'], mode='lines', name='SMA (20)'))

        fig.update_layout(
            title=f'{stock_symbol} Stock Price',
            xaxis_title='Date',
            yaxis_title='Price (USD)',
                        yaxis=dict(domain=[0.3, 1]),
            legend=dict(orientation='h', yanchor='bottom', xanchor='right', y=1.02, x=1)
        )

        fig2 = go.Figure()

        fig2.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI (14)'))
        fig2.update_layout(
            title=f'{stock_symbol} RSI',
            xaxis_title='Date',
            yaxis_title='RSI',
            yaxis=dict(domain=[0, 0.3]),
            legend=dict(orientation='h', yanchor='bottom', xanchor='right', y=0.5, x=1)
        )

        fig.add_trace(fig2.data[0])

        fig.write_html(os.path.join(output_folder, f'{stock_symbol}_stock_data.html'))

if __name__ == "__main__":
    app = StockPriceTracker()
    app.mainloop()
