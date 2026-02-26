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
        """Fetch top 10 Taiwan stocks by trading volume - Optimized Version"""
        try:
            self.status_label.config(text="Fetching real-time data from Yahoo...", fg="#2196F3")
            
            # 這是 Yahoo 股市「成交量排行」的正確網址
            #url = "https://tw.stock.yahoo.com/rank/volume"
            #url = "https://tw.stock.yahoo.com/rank/volume?exchange=TAI"  
            url = "https://tw.stock.yahoo.com/quote/2454"            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            """print(f"tinatest {response.status_code}")"""
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                """print(f"tinatest {soup}")"""
                stocks_items = []
                
                # Yahoo 股市的清單通常放在每一個 'li' 或 'div' 的結構中
                # 我們直接抓取包含股票代號連結的區塊
                rows = soup.select('div.table-row') # 這是 Yahoo 目前常用的類別
                
                # 如果 table-row 抓不到，嘗試抓取所有清單項目
                if not rows:
                    rows = soup.select('li.List\(n\)') 

                for row in rows:
                    if len(stocks_items) >= 20: break
                    
                    try:
                        # 1. 抓取名稱與代號
                        name_tag = row.select_one('div.Lh\(20px\)')
                        symbol_tag = row.select_one('span.Fz\(12px\)')
                        
                        if not name_tag or not symbol_tag: continue
                        
                        name = name_tag.get_text(strip=True)
                        symbol = symbol_tag.get_text(strip=True)
                        
                        # 2. 抓取數值 (價格、漲跌、成交量)
                        # 在 Yahoo 排行榜中，這些數值通常是特定類別的選取器
                        cells = row.select('div.Fxg\(1\)')
                        
                        if len(cells) >= 4:
                            price = cells[0].get_text(strip=True)
                            change = cells[1].get_text(strip=True)
                            volume = cells[4].get_text(strip=True) if len(cells) > 4 else "N/A"
                            
                            print(f"tinatest : test1 , test2 , test3")
                            stocks_items.append({
                                'symbol': symbol,
                                'name': name,
                                'price': price,
                                'change': change,
                                'volume': volume,
                                'url': f"https://tw.stock.yahoo.com/quote/{symbol}"
                            })
                    except:
                        continue
                
                # 更新 UI
                if len(stocks_items) > 0:
                    self.stocks_list = stocks_items
                    self.root.after(0, self.display_stocks)
                    self.status_label.config(text=f"Successfully updated {len(self.stocks_list)} stocks", fg="#4CAF50")
                else:
                    raise Exception("Could not parse data rows")
            else:
                raise Exception(f"HTTP Error {response.status_code}")
        
        except Exception as e:
            self.show_error(f"Live data error: {str(e)}")
            self.load_sample_stocks()
    
    def load_sample_stocks(self):
        """Load sample stock data when real data is unavailable
        """
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
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            if response.status_code == 200 :
                soup = BeautifulSoup(response.content, 'html.parser')
                header = soup.select_one('h1.C\(\$c-link-text\)')  # Yahoo h1 標籤       
                #volume_label = soup.find('span' , string='成交量')
                #all_links = soup.find_all('a',href=True)
                if header:
                    #symbol_tag = soup.find('h1').find_next_sibling('span') or soup.find('h1').select_one('span')
                    #symbol = symbol_tag.get_text(strip=True).replace('(','').replace(')','')
                    full_text =header.get_text(strip=True)
                    print(f"tinatest : full_text {full_text}")
                    #print(f"tinatest : symbol {symbol}")

                    price_tag = soup.select_one('span.Fz\(32px\).Fw\(b\)')
                    if price_tag:
                        price = price_tag.get_text(strip=True)
                    
                    volume_tag = soup.select_one('span.Fz\(16px\).Fw\(b\).Lh\(23px\)')
                    volume_a = "N/A"
                    if volume_tag:
                        volume_a = volume_tag.get_text()
                    """
                    all_spans =soup.find_all('span' , class_='Fz(16px)')
                    for i,span in enumerate(all_spans):
                        print(f"tinatest : span {span.get_text(strip=True)}")

                        if span.get_text() == "成交量":
                            volume_tag = span.find_next_sibling('span')
                            if volume_tag:
                                volume = volume_tag.get_text(strip=True)
                                break
                    """
                    print(f"Stock symbol : {url.split('/')[-1]}")
                    print(f"Price : {price}")
                    #volume_value = volume_label.find_next_sibling('span')
                    print(f"Volume : {volume_a}")     
                
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
