#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taiwan Stock Market Top 10 GUI Application
Display top 10 Taiwan stocks by price
"""

import tkinter as tk
from tkinter import messagebox, ttk
import threading
import requests
from bs4 import BeautifulSoup
import webbrowser

class TaiwanTopPriceStocksGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Taiwan Stock Market - Top 10 by Price")
        self.root.geometry("1000x750")
        self.root.config(bg="#f0f0f0")
        
        # Title
        title_label = tk.Label(
            self.root,
            text="Taiwan Stock Market - Top 10 by Price",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        title_label.pack(pady=15)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666666"
        )
        self.status_label.pack(pady=5)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=10)
        
        # Refresh button
        refresh_button = tk.Button(
            button_frame,
            text="Get Latest Data",
            command=self.load_stocks_thread,
            font=("Arial", 11),
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=8
        )
        refresh_button.pack(side=tk.LEFT, padx=10)
        
        # Clear button
        clear_button = tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_stocks,
            font=("Arial", 11),
            bg="#FF9800",
            fg="white",
            padx=15,
            pady=8
        )
        clear_button.pack(side=tk.LEFT, padx=10)
        
        # Exit button
        exit_button = tk.Button(
            button_frame,
            text="Exit",
            command=self.root.quit,
            font=("Arial", 11),
            bg="#f44336",
            fg="white",
            padx=15,
            pady=8
        )
        exit_button.pack(side=tk.LEFT, padx=10)
        
        # Selection frame for specifying stock number
        select_frame = tk.Frame(self.root, bg="#f0f0f0")
        select_frame.pack(pady=10)
        
        tk.Label(
            select_frame,
            text="Select stock (enter number 1-10):",
            font=("Arial", 10),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=5)
        
        # Input field for stock number
        self.select_var = tk.StringVar()
        select_entry = tk.Entry(
            select_frame,
            textvariable=self.select_var,
            width=5,
            font=("Arial", 10)
        )
        select_entry.pack(side=tk.LEFT, padx=5)
        
        # Open selected button
        open_selected_button = tk.Button(
            select_frame,
            text="View Details",
            command=self.open_selected_stock,
            font=("Arial", 11),
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=5
        )
        open_selected_button.pack(side=tk.LEFT, padx=5)
        
        # Stock display area
        stocks_label = tk.Label(
            self.root,
            text="Stock List:",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        stocks_label.pack(anchor=tk.W, padx=20, pady=(10, 5))
        
        # Table frame
        table_frame = tk.Frame(self.root, bg="#f0f0f0")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 20))
        
        # Create Treeview for stock table
        columns = ("No", "Symbol", "Name", "Price", "Change", "Volume")
        self.stocks_table = ttk.Treeview(
            table_frame,
            columns=columns,
            height=12,
            show="headings"
        )
        
        # Define column headings and widths
        self.stocks_table.column("No", width=40, anchor="center")
        self.stocks_table.column("Symbol", width=80, anchor="center")
        self.stocks_table.column("Name", width=120, anchor="center")
        self.stocks_table.column("Price", width=100, anchor="e")
        self.stocks_table.column("Change", width=80, anchor="e")
        self.stocks_table.column("Volume", width=100, anchor="e")
        
        self.stocks_table.heading("No", text="No")
        self.stocks_table.heading("Symbol", text="Symbol")
        self.stocks_table.heading("Name", text="Name")
        self.stocks_table.heading("Price", text="Price")
        self.stocks_table.heading("Change", text="Change")
        self.stocks_table.heading("Volume", text="Volume")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.stocks_table.yview)
        self.stocks_table.configure(yscroll=scrollbar.set)
        
        # Pack table and scrollbar
        self.stocks_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind click event to table rows
        self.stocks_table.bind("<Double-1>", self.on_table_double_click)
        
        # Initialize stock list
        self.stocks_list = []
    
    def load_stocks_thread(self):
        """Load stocks in a separate thread to avoid freezing the GUI"""
        self.status_label.config(text="Fetching stock data...", fg="#2196F3")
        self.root.update()
        
        thread = threading.Thread(target=self.load_stocks)
        thread.daemon = True
        thread.start()
    
    def load_stocks(self):
        """Fetch top 10 Taiwan stocks by price"""
        try:
            url = "https://tw.stock.yahoo.com/rank/price"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            stocks_items = []
            list_items = soup.select('li.List\(n\)')

            for item in list_items:
                if len(stocks_items) >= 10:
                    break
                try:
                    row_divs = item.select_one('div.D\(f\).Ai\(c\)').find_all('div', recursive=False)
                    if len(row_divs) < 5: continue

                    name_div = row_divs[0]
                    name = name_div.select_one('div.Lh\(20px\)').get_text(strip=True)
                    symbol = name_div.select_one('span').get_text(strip=True)
                    price = row_divs[1].get_text(strip=True)
                    change = row_divs[2].get_text(strip=True)
                    volume = row_divs[4].get_text(strip=True)

                    if price and price != "-":
                        stocks_items.append({
                            'symbol': symbol, 'name': name, 'price': price,
                            'change': change, 'volume': volume,
                            'url': f"https://tw.stock.yahoo.com/quote/{symbol}"
                        })
                except (AttributeError, IndexError):
                    continue

            if stocks_items:
                self.stocks_list = stocks_items[:10]
                self.root.after(0, self.display_stocks)
                self.root.after(0, lambda: self.status_label.config(text=f"Successfully retrieved {len(self.stocks_list)} stocks", fg="#4CAF50"))
            else:
                raise Exception("Could not parse stock data from website.")

        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda: self.show_error(f"Failed to fetch data: {e}. Using sample data instead."))
            self.root.after(0, self.load_sample_stocks)
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"An error occurred: {e}. Using sample data."))
            self.root.after(0, self.load_sample_stocks)

    def load_sample_stocks(self):
        """Load sample stock data when real data is unavailable"""
        self.stocks_list = [
            {'symbol': '3008', 'name': '大立光', 'price': '2,250.00', 'change': '-10.0', 'volume': '500', 'url': 'https://tw.stock.yahoo.com/quote/3008'},
            {'symbol': '5274', 'name': '信驊', 'price': '2,100.00', 'change': '+25.0', 'volume': '300', 'url': 'https://tw.stock.yahoo.com/quote/5274'},
            {'symbol': '5269', 'name': '祥碩', 'price': '1,500.00', 'change': '+5.0', 'volume': '800', 'url': 'https://tw.stock.yahoo.com/quote/5269'},
            {'symbol': '6669', 'name': '緯穎', 'price': '1,300.00', 'change': '-15.0', 'volume': '1,200', 'url': 'https://tw.stock.yahoo.com/quote/6669'},
            {'symbol': '2330', 'name': '台積電', 'price': '580.00', 'change': '+2.0', 'volume': '35,000', 'url': 'https://tw.stock.yahoo.com/quote/2330'},
        ]
        self.display_stocks()
        self.status_label.config(text="Showing sample data", fg="#ff9800")
    
    def display_stocks(self):
        """Display stock list in table"""
        for item in self.stocks_table.get_children():
            self.stocks_table.delete(item)
        
        for idx, stock in enumerate(self.stocks_list, 1):
            values = (idx, stock['symbol'], stock['name'], stock['price'], stock['change'], stock['volume'])
            self.stocks_table.insert("", "end", values=values)
    
    def clear_stocks(self):
        """Clear stock display"""
        for item in self.stocks_table.get_children():
            self.stocks_table.delete(item)
        self.stocks_list = []
        self.status_label.config(text="Cleared", fg="#666666")
    
    def show_error(self, message):
        """Display error message in a thread-safe way"""
        messagebox.showerror("Error", message)
    
    def open_link(self, url):
        """Open a stock link in browser"""
        try:
            webbrowser.open(url)
        except Exception as e:
            self.show_error(f"Failed to open webpage: {str(e)}")
    
    def on_table_double_click(self, event):
        """Handle table row double-click event"""
        item = self.stocks_table.identify_row(event.y)
        if not item: return
        
        values = self.stocks_table.item(item)['values']
        if values:
            index = values[0]
            url = self.stocks_list[index - 1]['url']
            self.open_link(url)
    
    def open_selected_stock(self):
        """Open the stock by specified number"""
        try:
            index_str = self.select_var.get().strip()
            if not index_str:
                messagebox.showwarning("Warning", "Please enter stock number (1-10)")
                return
            
            index = int(index_str)
            if not (1 <= index <= len(self.stocks_list)):
                messagebox.showwarning("Warning", f"Invalid number. Please enter 1-{len(self.stocks_list)}")
                return
            
            url = self.stocks_list[index - 1]['url']
            self.open_link(url)
        
        except ValueError:
            self.show_error("Please enter a valid number")
        except Exception as e:
            self.show_error(f"Failed to open stock page: {str(e)}")

def main():
    root = tk.Tk()
    app = TaiwanTopPriceStocksGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
