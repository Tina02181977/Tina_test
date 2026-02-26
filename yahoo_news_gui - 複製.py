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

class YahooNewsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YAHOO新闻 - 前十条")
        self.root.geometry("900x700")
        self.root.config(bg="#f0f0f0")
        
        # 标题
        title_label = tk.Label(
            self.root,
            text="YAHOO新闻 - 前十条新闻",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        title_label.pack(pady=15)
        
        # 状态标签
        self.status_label = tk.Label(
            self.root,
            text="准备就绪",
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
            text="获取最新新闻",
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
            text="清空",
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
            text="退出",
            command=self.root.quit,
            font=("Arial", 11),
            bg="#f44336",
            fg="white",
            padx=15,
            pady=8
        )
        exit_button.pack(side=tk.LEFT, padx=10)
        
        # 新闻显示区域
        news_label = tk.Label(
            self.root,
            text="新闻列表：",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        news_label.pack(anchor=tk.W, padx=20, pady=(10, 5))
        
        # 使用Frame来放置Scrollbar和Text
        text_frame = tk.Frame(self.root, bg="#f0f0f0")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 20))
        
        # 新闻内容显示框
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
        
        # 初始化新闻列表
        self.news_list = []
    
    def load_news_thread(self):
        """在独立线程中加载新闻，避免GUI冻结"""
        self.status_label.config(text="正在获取新闻...", fg="#2196F3")
        self.root.update()
        
        thread = threading.Thread(target=self.load_news)
        thread.daemon = True
        thread.start()
    
    def load_news(self):
        """从YAHOO新闻获取前十条新闻"""
        try:
            # 获取YAHOO新闻页面
            url = "https://news.yahoo.com"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            self.status_label.config(text="连接中...", fg="#2196F3")
            self.root.update()
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 寻找新闻条目
                news_items = []
                
                # 方法1: 查找所有链接，过滤新闻相关的
                all_links = soup.find_all('a', href=True)
                
                for link in all_links:
                    if len(news_items) >= 10:
                        break
                    try:
                        href = link.get('href', '')
                        
                        # 寻找新闻文章链接（通常包含特定路径模式）
                        if any(pattern in href.lower() for pattern in ['article', '/news/', '/video/', '/captions/']):
                            # 获取标题
                            title = link.get_text(strip=True)
                            
                            # 标题长度合理且不为空
                            if title and 5 < len(title) < 300 and title not in [item['title'] for item in news_items]:
                                # 处理相对URL
                                if href.startswith('/'):
                                    href = "https://news.yahoo.com" + href
                                elif not href.startswith('http'):
                                    href = "https://news.yahoo.com/" + href
                                
                                news_items.append({
                                    'title': title,
                                    'link': href
                                })
                    except Exception as e:
                        continue
                
                # 方法2: 如果找到不足10条，尝试查找所有文本较长的链接
                if len(news_items) < 10:
                    for link in all_links:
                        if len(news_items) >= 10:
                            break
                        try:
                            title = link.get_text(strip=True)
                            href = link.get('href', '')
                            
                            # 更宽松的过滤条件
                            if (title and 10 <= len(title) < 300 and 
                                href.startswith(('http', '/')) and
                                title not in [item['title'] for item in news_items]):
                                
                                if href.startswith('/'):
                                    href = "https://news.yahoo.com" + href
                                
                                news_items.append({
                                    'title': title,
                                    'link': href
                                })
                        except Exception as e:
                            continue
                
                # 方法3: 查找所有h3/h2标签（通常是标题）
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
                                        href = "https://news.yahoo.com" + href
                                    elif not href.startswith('http'):
                                        href = "https://news.yahoo.com/" + href
                                    
                                    news_items.append({
                                        'title': title,
                                        'link': href
                                    })
                        except Exception as e:
                            continue
                
                self.news_list = news_items[:10]
                
                if self.news_list:
                    self.display_news()
                    self.status_label.config(text=f"成功获取 {len(self.news_list)} 条新闻", fg="#4CAF50")
                else:
                    self.show_error("未能找到新闻。网站结构可能已更改，请尝试重新加载。")
                    self.status_label.config(text="未找到新闻", fg="#ff9800")
            else:
                self.show_error(f"获取失败，状态码: {response.status_code}")
                self.status_label.config(text="获取失败", fg="#f44336")
        
        except requests.exceptions.Timeout:
            self.show_error("连接超时，请检查网络连接")
            self.status_label.config(text="连接超时", fg="#f44336")
        except requests.exceptions.ConnectionError:
            self.show_error("无法连接到网络，请检查网络连接")
            self.status_label.config(text="连接失败", fg="#f44336")
        except Exception as e:
            self.show_error(f"获取新闻出错: {str(e)}")
            self.status_label.config(text="出错", fg="#f44336")
    
    def display_news(self):
        """显示新闻列表"""
        self.news_text.config(state=tk.NORMAL)
        self.news_text.delete(1.0, tk.END)
        
        if not self.news_list:
            self.news_text.insert(tk.END, "没有新闻数据")
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.news_text.insert(tk.END, f"获取时间: {timestamp}\n")
            self.news_text.insert(tk.END, "=" * 100 + "\n\n")
            
            for idx, news in enumerate(self.news_list, 1):
                self.news_text.insert(tk.END, f"【{idx}】 {news['title']}\n")
                self.news_text.insert(tk.END, f"链接: {news['link']}\n")
                self.news_text.insert(tk.END, "-" * 100 + "\n\n")
        
        self.news_text.config(state=tk.DISABLED)
    
    def clear_news(self):
        """清空新闻显示"""
        self.news_text.config(state=tk.NORMAL)
        self.news_text.delete(1.0, tk.END)
        self.news_text.config(state=tk.DISABLED)
        self.news_list = []
        self.status_label.config(text="已清空", fg="#666666")
    
    def show_error(self, message):
        """显示错误消息"""
        self.root.after(0, lambda: messagebox.showerror("错误", message))


def main():
    root = tk.Tk()
    app = YahooNewsGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
