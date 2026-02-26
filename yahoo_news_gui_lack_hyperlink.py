#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YAHOO新闻前十条GUI应用
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import webbrowser

class YahooNewsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TAIWAN YAHOO News - Top 10")
        self.root.geometry("900x700")
        self.root.config(bg="#f0f0f0")
        
        # 标题
        title_label = tk.Label(
            self.root,
            text="TAIWAN YAHOO News - Top 10",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        title_label.pack(pady=15)
        
        # 状态标签
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666666"
        )
        self.status_label.pack(pady=5)
        
        # 按钮框架
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=10)
        
        # 刷新按钮
        refresh_button = tk.Button(
            button_frame,
            text="Get Latest News",
            command=self.load_news_thread,
            font=("Arial", 11),
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=8
        )
        refresh_button.pack(side=tk.LEFT, padx=10)
        
        # 清空按钮
        clear_button = tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_news,
            font=("Arial", 11),
            bg="#FF9800",
            fg="white",
            padx=15,
            pady=8
        )
        clear_button.pack(side=tk.LEFT, padx=10)
        
        # 退出按钮
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
        
        # News display area
        news_label = tk.Label(
            self.root,
            text="News List:",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        news_label.pack(anchor=tk.W, padx=20, pady=(10, 5))
        
        # 使用Frame来放置Scrollbar和Text
        text_frame = tk.Frame(self.root, bg="#f0f0f0")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 20))
        
        # News content display box
        self.news_text = scrolledtext.ScrolledText(
            text_frame,
            font=("Arial", 10),
            bg="white",
            fg="#333333",
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief=tk.SUNKEN,
            border=1
        )
        self.news_text.pack(fill=tk.BOTH, expand=True)
        
        # Initialize news list
        self.news_list = []
    
    def load_news_thread(self):
        """Load news in a separate thread to avoid freezing the GUI"""
        self.status_label.config(text="Fetching news...", fg="#2196F3")
        self.root.update()
        
        thread = threading.Thread(target=self.load_news)
        thread.daemon = True
        thread.start()
    
    def load_news(self):
        """Fetch top 10 news from YAHOO News"""
        try:
            # Fetch YAHOO News page
            url = "https://tw.news.yahoo.com/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            self.status_label.config(text="Connecting...", fg="#2196F3")
            self.root.update()
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find news items
                news_items = []
                
                # Method 1: Find all links and filter for news
                all_links = soup.find_all('a', href=True)
                
                for link in all_links:
                    if len(news_items) >= 10:
                        break
                    try:
                        href = link.get('href', '')
                        
                        # Look for news article links (usually contain specific path patterns)
                        if any(pattern in href.lower() for pattern in ['article', '/news/', '/video/', '/captions/']):
                            # Get title
                            title = link.get_text(strip=True)
                            
                            # Title has reasonable length and is not empty
                            if title and 5 < len(title) < 300 and title not in [item['title'] for item in news_items]:
                                # Handle relative URLs
                                if href.startswith('/'):
                                    href = "https://tw.news.yahoo.com" + href
                                elif not href.startswith('http'):
                                    href = "https://tw.news.yahoo.com/" + href
                                
                                news_items.append({
                                    'title': title,
                                    'link': href
                                })
                    except Exception as e:
                        continue
                
                # Method 2: If found less than 10, try to find all longer text links
                if len(news_items) < 10:
                    for link in all_links:
                        if len(news_items) >= 10:
                            break
                        try:
                            title = link.get_text(strip=True)
                            href = link.get('href', '')
                            
                            # More relaxed filter conditions
                            if (title and 10 <= len(title) < 300 and 
                                href.startswith(('http', '/')) and
                                title not in [item['title'] for item in news_items]):
                                
                                if href.startswith('/'):
                                    href = "https://tw.news.yahoo.com" + href
                                
                                news_items.append({
                                    'title': title,
                                    'link': href
                                })
                        except Exception as e:
                            continue
                
                # Method 3: Find all h3/h2 tags (usually titles)
                if len(news_items) < 10:
                    for heading in soup.find_all(['h2', 'h3']):
                        if len(news_items) >= 10:
                            break
                        try:
                            title = heading.get_text(strip=True)
                            parent_link = heading.find_parent('a')
                            
                            if parent_link and title:
                                href = parent_link.get('href', '')
                                
                                if href and title not in [item['title'] for item in news_items]:
                                    if href.startswith('/'):
                                        href = "https://tw.news.yahoo.com" + href
                                    elif not href.startswith('http'):
                                        href = "https://tw.news.yahoo.com/" + href
                                    
                                    news_items.append({
                                        'title': title,
                                        'link': href
                                    })
                        except Exception as e:
                            continue
                
                self.news_list = news_items[:10]
                
                if self.news_list:
                    self.display_news()
                    self.status_label.config(text=f"Successfully retrieved {len(self.news_list)} news items", fg="#4CAF50")
                else:
                    self.show_error("Unable to find news. The website structure may have changed.\nPlease try again.")
                    self.status_label.config(text="No news found", fg="#ff9800")
            else:
                self.show_error(f"Failed to fetch, status code: {response.status_code}")
                self.status_label.config(text="Fetch failed", fg="#f44336")
        
        except requests.exceptions.Timeout:
            self.show_error("Connection timeout. Please check your network connection.")
            self.status_label.config(text="Connection timeout", fg="#f44336")
        except requests.exceptions.ConnectionError:
            self.show_error("Unable to connect to network. Please check your network connection.")
            self.status_label.config(text="Connection failed", fg="#f44336")
        except Exception as e:
            self.show_error(f"Error fetching news: {str(e)}")
            self.status_label.config(text="Error", fg="#f44336")
    
    def display_news(self):
        """Display news list"""
        self.news_text.config(state=tk.NORMAL)
        self.news_text.delete(1.0, tk.END)
        
        if not self.news_list:
            self.news_text.insert(tk.END, "No news data")
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.news_text.insert(tk.END, f"Fetch time: {timestamp}\n")
            self.news_text.insert(tk.END, "=" * 100 + "\n\n")
            
            for idx, news in enumerate(self.news_list, 1):
                # Get starting position
                pos_start = self.news_text.index(tk.END)
                
                # Insert title
                title_text = f"[{idx}] | {news['title']}"
                self.news_text.insert(tk.END, title_text)
                
                # Get ending position
                pos_end = self.news_text.index(tk.END)
                
                # Create unique tag for each link
                tag_name = f"hyperlink_{idx}"
                self.news_text.tag_config(tag_name, foreground="blue", underline=True)
                self.news_text.tag_add(tag_name, pos_start, pos_end)
                
                # Bind click event with proper closure
                self.news_text.tag_bind(tag_name, "<Button-1>", 
                                       lambda e, link=news['link']: self.open_link(link))
                
                # Bind hover for cursor change
                self.news_text.tag_bind(tag_name, "<Enter>", 
                                       lambda e: self.news_text.config(cursor="hand2"))
                self.news_text.tag_bind(tag_name, "<Leave>", 
                                       lambda e: self.news_text.config(cursor=""))
                
                # Add newline
                self.news_text.insert(tk.END, "\n")
        
        self.news_text.config(state=tk.DISABLED)
    
    def clear_news(self):
        """Clear news display"""
        self.news_text.config(state=tk.NORMAL)
        self.news_text.delete(1.0, tk.END)
        self.news_text.config(state=tk.DISABLED)
        self.news_list = []
        self.status_label.config(text="Cleared", fg="#666666")
    
    def show_error(self, message):
        """Display error message"""
        self.root.after(0, lambda: messagebox.showerror("错误", message))
    
    def open_link(self, url):
        """Open a news link directly"""
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open webpage: {str(e)}")


def main():
    root = tk.Tk()
    YahooNewsGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

