#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taiwan Stock Market Top 10 GUI Application
Display top 10 Taiwan stocks by trading volume
"""

import tkinter as tk
from tkinter import messagebox, ttk
import threading
import requests
from bs4 import BeautifulSoup
import webbrowser

class TaiwanStocksGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Taiwan Stock Market - Top 10 by Volume")
        self.root.geometry("1000x750")
        self.root.config(bg="#f0f0f0")
        
        # Title
        title_label = tk.Label(
            self.root,
            text="Taiwan Stock Market - Top 10 by Trading Volume",
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
        columns = ("No", "Symbol", "Name", "Price", "Change", "Volume", "Link")
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
        self.stocks_table.column("Link", width=150, anchor="w")
        
        self.stocks_table.heading("No", text="No")
        self.stocks_table.heading("Symbol", text="Symbol")
        self.stocks_table.heading("Name", text="Name")
        self.stocks_table.heading("Price", text="Price")
        self.stocks_table.heading("Change", text="Change")
        self.stocks_table.heading("Volume", text="Volume")
        self.stocks_table.heading("Link", text="Link")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.stocks_table.yview)
        self.stocks_table.configure(yscroll=scrollbar.set)
        
        # Pack table and scrollbar
        self.stocks_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind click event to table rows
        self.stocks_table.bind("<Button-1>", self.on_table_click)
        
        # Initialize stock list
        self.stocks_list = []
        self.selected_stock_idx = None
        self.selected_stock_symbol = None
    
    def load_stocks_thread(self):
        """Load stocks in a separate thread to avoid freezing the GUI"""
        self.status_label.config(text="Fetching stock data...", fg="#2196F3")
        self.root.update()
        
        thread = threading.Thread(target=self.load_stocks)
        thread.daemon = True
        thread.start()
    
    def load_stocks(self):
        """Fetch top 10 Taiwan stocks by trading volume"""
        try:
            self.status_label.config(text="Fetching stock data...", fg="#2196F3")
            self.root.update()
            
            # Fetch Taiwan stock market data from Yahoo Finance
            url = "https://tw.stock.yahoo.com/class"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                # Parse HTML to get stock data
                soup = BeautifulSoup(response.content, 'html.parser')
                
                stocks_items = []
                
                # Try multiple methods to find stock data
                # Method 1: Look for stock links and data in the page
                all_links = soup.find_all('a', href=True)
                
                for link in all_links:
                    if len(stocks_items) >= 10:
                        break
                    
                    try:
                        href = link.get('href', '')
                        
                        # Check if this is a stock quote link
                        if '/quote/' in href:
                            # Extract symbol from URL
                            symbol = href.split('/quote/')[-1].split('?')[0]
                            link_text = link.get_text(strip=True)
                            
                            if symbol and len(symbol) > 0:
                                # Find the parent container with stock data
                                parent = link.find_parent('tr') or link.find_parent('div')
                                
                                if parent:
                                    # Extract price and other data
                                    cells = parent.find_all('td') or parent.find_all('span')
                                    
                                    if cells and len(cells) >= 2:
                                        try:
                                            price = cells[-3].get_text(strip=True) if len(cells) >= 3 else "N/A"
                                            change = cells[-2].get_text(strip=True) if len(cells) >= 2 else "N/A"
                                            volume = cells[-1].get_text(strip=True) if len(cells) >= 1 else "N/A"
                                            
                                            # Clean up data
                                            if price and price != "N/A":
                                                stocks_items.append({
                                                    'symbol': symbol,
                                                    'name': link_text[:30] if link_text else symbol,
                                                    'price': price,
                                                    'change': change,
                                                    'volume': volume,
                                                    'url': f"https://tw.stock.yahoo.com/quote/{symbol}"
                                                })
                                        except:
                                            pass
                    except Exception as e:
                        continue
                
                # If we got enough data, use it
                if len(stocks_items) >= 10:
                    self.stocks_list = stocks_items[:10]
                    self.selected_stock_idx = None
                    self.selected_stock_symbol = None
                    self.display_stocks()
                    self.status_label.config(text=f"Successfully retrieved {len(self.stocks_list)} stocks", fg="#4CAF50")
                else:
                    # Fall back to sample data if we couldn't parse properly
                    self.show_error(f"Found only {len(stocks_items)} stocks. Showing sample data instead.")
                    self.load_sample_stocks()
            else:
                self.show_error(f"Failed to fetch, status code: {response.status_code}")
                self.status_label.config(text="Fetch failed", fg="#f44336")
        
        except requests.exceptions.Timeout:
            self.show_error("Connection timeout. Using sample data instead.")
            self.load_sample_stocks()
        except requests.exceptions.ConnectionError:
            self.show_error("Unable to connect. Using sample data instead.")
            self.load_sample_stocks()
        except Exception as e:
            self.show_error(f"Error fetching stock data: {str(e)}\nUsing sample data.")
            self.load_sample_stocks()
    
    def load_sample_stocks(self):
        """Load sample stock data when real data is unavailable"""
        self.stocks_list = [
            {'symbol': '2330', 'name': 'TSMC', 'price': '680.00', 'change': '+2.5%', 'volume': '35,520,000', 'url': 'https://tw.stock.yahoo.com/quote/2330'},
            {'symbol': '2454', 'name': 'MediaTek', 'price': '1,185.00', 'change': '+1.2%', 'volume': '8,420,000', 'url': 'https://tw.stock.yahoo.com/quote/2454'},
            {'symbol': '2317', 'name': 'Foxconn', 'price': '21.60', 'change': '+0.5%', 'volume': '35,680,000', 'url': 'https://tw.stock.yahoo.com/quote/2317'},
            {'symbol': '2308', 'name': 'Delta Electronics', 'price': '411.50', 'change': '+1.8%', 'volume': '3,250,000', 'url': 'https://tw.stock.yahoo.com/quote/2308'},
            {'symbol': '1303', 'name': 'Nanya Technology', 'price': '26.55', 'change': '-0.2%', 'volume': '28,450,000', 'url': 'https://tw.stock.yahoo.com/quote/1303'},
            {'symbol': '2412', 'name': 'MediaTek', 'price': '945.00', 'change': '+1.1%', 'volume': '12,350,000', 'url': 'https://tw.stock.yahoo.com/quote/2412'},
            {'symbol': '2303', 'name': 'Acer', 'price': '37.15', 'change': '+0.8%', 'volume': '18,920,000', 'url': 'https://tw.stock.yahoo.com/quote/2303'},
            {'symbol': '2409', 'name': 'Quanta Services', 'price': '150.00', 'change': '+2.1%', 'volume': '15,680,000', 'url': 'https://tw.stock.yahoo.com/quote/2409'},
            {'symbol': '2356', 'name': 'Micron Technology', 'price': '95.50', 'change': '-1.3%', 'volume': '22,150,000', 'url': 'https://tw.stock.yahoo.com/quote/2356'},
            {'symbol': '2338', 'name': 'NVIDIA', 'price': '1,280.00', 'change': '+3.2%', 'volume': '9,870,000', 'url': 'https://tw.stock.yahoo.com/quote/2338'},
        ]
        self.display_stocks()
        self.status_label.config(text="Showing sample data", fg="#ff9800")
    
    def display_stocks(self):
        """Display stock list in table"""
        # Clear existing items
        for item in self.stocks_table.get_children():
            self.stocks_table.delete(item)
        
        if not self.stocks_list:
            return
        
        # Insert stock data into table
        for idx, stock in enumerate(self.stocks_list, 1):
            values = (
                idx,
                stock['symbol'],
                stock['name'],
                stock['price'],
                stock['change'],
                stock['volume'],
                stock['url']
            )
            self.stocks_table.insert("", "end", values=values)
    
    def clear_stocks(self):
        """Clear stock display"""
        for item in self.stocks_table.get_children():
            self.stocks_table.delete(item)
        self.stocks_list = []
        self.selected_stock_idx = None
        self.selected_stock_symbol = None
        self.status_label.config(text="Cleared", fg="#666666")
        self.selected_stock_idx = None
        self.selected_stock_symbol = None
        self.status_label.config(text="Cleared", fg="#666666")
    
    def show_error(self, message):
        """Display error message"""
        self.root.after(0, lambda: messagebox.showerror("Error", message))
    
    def open_link(self, url):
        """Open a stock link in browser"""
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open webpage: {str(e)}")
    
    def select_and_open_stock(self, idx, symbol):
        """Select a stock and display its info"""
        self.selected_stock_idx = idx
        self.selected_stock_symbol = symbol
        self.select_var.set(str(idx))
        self.status_label.config(text=f"Selected: [{idx}] {symbol}", fg="#FF9800")
    
    def on_table_click(self, event):
        """Handle table row click event"""
        region = self.stocks_table.identify("region", event.x, event.y)
        if region != "body":
            return
        
        item = self.stocks_table.identify_row(event.y)
        if not item:
            return
        
        # Get the selected row data
        values = self.stocks_table.item(item)['values']
        if values:
            idx = values[0]
            symbol = values[1]
            url = values[6]  # Link is at index 6
            
            # Update selection
            self.selected_stock_idx = idx
            self.selected_stock_symbol = symbol
            self.select_var.set(str(idx))
            self.status_label.config(text=f"Selected: [{idx}] {symbol}", fg="#FF9800")
            
            # Open the link
            self.open_link(url)
    
    def open_selected_stock(self):
        """Open the stock by specified number"""
        try:
            index_str = self.select_var.get().strip()
            
            if not index_str:
                messagebox.showwarning("Warning", "Please enter stock number (1-10)")
                return
            
            index = int(index_str)
            
            if index < 1 or index > len(self.stocks_list):
                messagebox.showwarning("Warning", f"Invalid number. Please enter 1-{len(self.stocks_list)}")
                return
            
            url = self.stocks_list[index - 1]['url']
            symbol = self.stocks_list[index - 1]['symbol']
            self.selected_stock_idx = index
            self.selected_stock_symbol = symbol
            self.status_label.config(text=f"Selected: [{index}] {symbol}", fg="#FF9800")
            self.open_link(url)
        
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open stock page: {str(e)}")


def main():
    root = tk.Tk()
    TaiwanStocksGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
