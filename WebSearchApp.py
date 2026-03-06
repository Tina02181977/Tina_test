import tkinter as tk
from tkinter import messagebox
import threading
import urllib.request
import urllib.parse
import re
import html
import webbrowser
import os
import json

GEMINI_AVAILABLE = True

class WebSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("城市/國家 網路探索工具 (雙擊開啟網頁)")
        self.root.geometry("750x500")

        # 用來儲存搜尋結果的 List，方便雙擊時取得對應的 URL
        self.search_results = []

        # --- 頂部：輸入與按鈕區 ---
        self.frame_top = tk.Frame(root)
        self.frame_top.pack(pady=15)

        self.lbl_query = tk.Label(self.frame_top, text="請輸入城市或國家名：", font=("微軟正黑體", 12))
        self.lbl_query.pack(side=tk.LEFT, padx=5)

        self.entry_query = tk.Entry(self.frame_top, font=("微軟正黑體", 12), width=20)
        self.entry_query.pack(side=tk.LEFT, padx=5)
        # 綁定 Enter 鍵也可以觸發搜尋
        self.entry_query.bind("<Return>", lambda event: self.start_search())

        self.btn_search = tk.Button(self.frame_top, text="開始搜尋", font=("微軟正黑體", 12), 
                                    bg="#4CAF50", fg="white", command=self.start_search)
        self.btn_search.pack(side=tk.LEFT, padx=5)

        self.btn_summary = tk.Button(self.frame_top, text="生成旅遊總結 (AI)", font=("微軟正黑體", 12),
                                     bg="#2196F3", fg="white", command=self.start_generate_summary, state=tk.DISABLED)
        self.btn_summary.pack(side=tk.LEFT, padx=5)
        
        # Gemini API Key 設定
        self.gemini_api_key = ""  # 使用者可以在這裡設定 API Key

        # --- 中間：提示訊息區 ---
        self.lbl_status = tk.Label(root, text="準備就緒。輸入後按下搜尋，並「雙擊」結果來開啟網頁。", font=("微軟正黑體", 10), fg="gray")
        self.lbl_status.pack(pady=5)

        # --- 底部：清單顯示區 ---
        self.frame_list = tk.Frame(root)
        self.frame_list.pack(pady=5, padx=15, fill=tk.BOTH, expand=True)

        # 捲動條
        self.scrollbar = tk.Scrollbar(self.frame_list)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox 列表
        self.listbox = tk.Listbox(self.frame_list, font=("微軟正黑體", 12), yscrollcommand=self.scrollbar.set, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.listbox.yview)

        # 綁定雙擊事件：當在 Listbox 項目上點擊兩下時觸發
        self.listbox.bind("<Double-1>", self.on_double_click)

    def start_search(self):
        query = self.entry_query.get().strip()
        if not query:
            messagebox.showwarning("警告", "請輸入您想查詢的名稱！")
            return
            
        # UI 狀態更新
        self.btn_search.config(state=tk.DISABLED)
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "正在網路上為您抓取前 5 項結果，請稍候...")
        self.lbl_status.config(text="搜尋中...", fg="blue")
        
        # 使用執行緒以防 GUI 卡頓
        threading.Thread(target=self.perform_search, args=(query,), daemon=True).start()

    def perform_search(self, query):
        try:
            # 加上「旅遊」關鍵字確保找到的是旅遊相關的網站
            search_query = f"{query} 旅遊"
            
            # 使用 urllib.parse.quote 對中文字進行 URL 編碼
            encoded_query = urllib.parse.quote(search_query)
            
            # 使用 DuckDuckGo HTML 介面 (穩定且可靠的替代方案)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            print(f"Fetching: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req, timeout=10)
            html_content = response.read().decode('utf-8', errors='ignore')
            
            # 針對 DuckDuckGo 的結果結構進行擷取
            pattern = r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>'
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            
            results = []
            seen_urls = set()
            
            for link_raw, title_raw in matches:
                # 處理 DuckDuckGo 轉址還原真實 URL
                if "uddg=" in link_raw:
                    clean_url = urllib.parse.unquote(link_raw.split('uddg=')[1].split('&')[0])
                else:
                    clean_url = link_raw
                
                # 確保 URL 不重複
                if clean_url in seen_urls:
                    continue
                seen_urls.add(clean_url)
                    
                # 清理標題上的 HTML 標籤與特殊字元
                clean_title = re.sub(r'<[^>]+>', '', title_raw).strip()
                clean_title = html.unescape(clean_title) 
                
                if clean_title and clean_url:
                    results.append({"title": clean_title, "url": clean_url})
                
                # 只要前 5 項
                if len(results) >= 5:
                    break
            
            # 將結果送回主執行緒更新 UI
            self.root.after(0, self.update_listbox, results, query)
            
        except Exception as e:
            error_msg = f"搜尋失敗：{str(e)}"
            self.root.after(0, self.show_error, error_msg)

    def update_listbox(self, results, query):
        self.listbox.delete(0, tk.END)
        self.search_results = results # 存入 Class 變數供雙擊事件使用
        
        if not results:
            self.listbox.insert(tk.END, "找不到相關結果，請嘗試其他關鍵字。")
            self.lbl_status.config(text="搜尋完畢，無結果。", fg="red")
            self.btn_summary.config(state=tk.DISABLED)
        else:
            for idx, item in enumerate(results, start=1):
                display_text = f"{idx}. {item['title']}"
                self.listbox.insert(tk.END, display_text)
            self.lbl_status.config(text=f"成功為您找到【{query}】的 {len(results)} 個網頁！(雙擊清單以開啟瀏覽器)", fg="green")
            self.btn_summary.config(state=tk.NORMAL)
            
        self.btn_search.config(state=tk.NORMAL)

    def show_error(self, message):
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, message)
        self.lbl_status.config(text="發生錯誤", fg="red")
        self.btn_search.config(state=tk.NORMAL)
        self.btn_summary.config(state=tk.DISABLED)

    def on_double_click(self, event):
        # 取得目前被選中的索引
        selection = self.listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        
        # 確認清單內有儲存的 URL 資料 (防止點到錯誤訊息文字)
        if index < len(self.search_results):
            target_url = self.search_results[index]['url']
            
            # 使用 Python 內建的 webbrowser 模組，透過電腦預設瀏覽器開啟網頁
            try:
                webbrowser.open(target_url)
                self.lbl_status.config(text=f"已開啟網頁：{target_url[:50]}...", fg="#FF9800")
            except Exception as e:
                messagebox.showerror("錯誤", f"無法開啟網頁：{str(e)}")

    def start_generate_summary(self):
        if not self.search_results:
            messagebox.showwarning("警告", "請先搜尋後再生成總結！")
            return
        
        # 檢查 API Key
        if not self.gemini_api_key:
            api_key = self._prompt_api_key()
            if not api_key:
                return
            self.gemini_api_key = api_key
        
        self.btn_summary.config(state=tk.DISABLED)
        self.lbl_status.config(text="正在使用 Gemini AI 生成旅遊總結，請稍候...", fg="blue")
        threading.Thread(target=self.generate_summary, daemon=True).start()
    
    def _prompt_api_key(self):
        """彈出視窗讓用戶輸入 API Key"""
        dialog = tk.Toplevel(self.root)
        dialog.title("設定 Gemini API Key")
        dialog.geometry("500x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="請輸入您的 Google Gemini API Key：", 
                font=("微軟正黑體", 11)).pack(pady=10)
        
        tk.Label(dialog, text="(可至 https://aistudio.google.com/apikey 免費取得)",
                font=("微軟正黑體", 9), fg="gray").pack()
        
        api_key_var = tk.StringVar()
        entry = tk.Entry(dialog, textvariable=api_key_var, font=("微軟正黑體", 10), width=50)
        entry.pack(pady=10, padx=20)
        entry.focus()
        
        result = {'key': None}
        
        def on_ok():
            result['key'] = api_key_var.get().strip()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="確定", command=on_ok, bg="#4CAF50", fg="white",
                 font=("微軟正黑體", 10), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="取消", command=on_cancel, bg="#f44336", fg="white",
                 font=("微軟正黑體", 10), width=10).pack(side=tk.LEFT, padx=5)
        
        dialog.wait_window()
        return result['key']

    def generate_summary(self):
        try:
            # 收集所有網頁的文字內容
            all_content = []
            query_location = self.entry_query.get().strip()
            web_summaries = []
            
            for idx, result in enumerate(self.search_results, start=1):
                url = result['url']
                title = result['title']
                
                try:
                    # 抓取網頁內容
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    req = urllib.request.Request(url, headers=headers)
                    response = urllib.request.urlopen(req, timeout=8)
                    page_html = response.read().decode('utf-8', errors='ignore')
                    
                    # 移除所有 HTML 標籤，保留純文字
                    text_only = re.sub(r'<script[^>]*>.*?</script>', '', page_html, flags=re.DOTALL)
                    text_only = re.sub(r'<style[^>]*>.*?</style>', '', text_only, flags=re.DOTALL)
                    text_only = re.sub(r'<[^>]+>', ' ', text_only)
                    text_only = html.unescape(text_only)
                    
                    # 清理空白與換行
                    lines = [line.strip() for line in text_only.split('\n') if line.strip()]
                    # 取前1000字作為摘要
                    content_preview = ' '.join(lines)[:1000]
                    web_summaries.append(f"來源{idx} - {title}:\n{content_preview}\n")
                    
                except Exception as e:
                    web_summaries.append(f"來源{idx} - {title}: 無法擷取內容\n")
            
            # 使用 Gemini AI 生成總結 - 直接使用 REST API
            try:
                # 構建 API 請求 URL 與參數
                api_endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
                
                prompt = f"""你是一位專業的旅遊規劃師。請根據以下網頁資訊，為【{query_location}】生成一份詳細的旅遊導覽。

參考資料：
{chr(10).join(web_summaries)}

請以繁體中文生成以下內容：

1. **旅遊簡介**（100字內）：簡述這個地點的特色與魅力

2. **熱門景點推薦**（列出5-8個具體景點，每個景點包含名稱和一句話介紹）
   格式範例：
   📍 台北101 - 台灣最高地標建築，可登頂欣賞360度城市美景

3. **在地美食**（列出4-6項特色美食或餐廳）
   格式範例：
   🍜 鼎泰豐小籠包 - 米其林推薦的台灣必吃美食

4. **交通資訊**（說明如何抵達及市區交通方式）

5. **住宿建議**（推薦2-3個住宿區域及特色）

6. **三天兩夜自由行程規劃**（詳細列出每天的行程安排，包含上午、下午、晚上的活動）
   格式範例：
   【第一天】主題
   ⏰ 上午 09:00 - 具體活動內容
   ⏰ 下午 14:00 - 具體活動內容
   ⏰ 晚上 18:00 - 具體活動內容

請確保內容具體、實用，避免空泛的描述。"""
                
                # 準備請求參數
                request_body = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 2048
                    }
                }
                
                # 構建完整的 URL
                url = f"{api_endpoint}?key={self.gemini_api_key}"
                
                # 發送請求
                headers = {
                    'Content-Type': 'application/json'
                }
                body_json = json.dumps(request_body).encode('utf-8')
                
                req = urllib.request.Request(url, data=body_json, headers=headers, method='POST')
                response = urllib.request.urlopen(req, timeout=30)
                response_data = response.read().decode('utf-8')
                
                # 解析回應
                result = json.loads(response_data)
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    ai_content = result['candidates'][0]['content']['parts'][0]['text']
                    summary_text = "\n" + "="*50 + "\n"
                    summary_text += f"  【{query_location}】AI 智能旅遊導覽\n"
                    summary_text += "="*50 + "\n\n"
                    summary_text += ai_content
                    summary_text += "\n\n" + "="*50 + "\n"
                    summary_text += "📚 本導覽由 Google Gemini AI 根據以下資料生成：\n"
                    for idx, result_item in enumerate(self.search_results, start=1):
                        summary_text += f"{idx}. {result_item['title']}\n"
                else:
                    summary_text = f"API 回應異常\n\n錯誤詳情：{json.dumps(result, indent=2, ensure_ascii=False)}"
                
            except urllib.error.HTTPError as e:
                error_content = e.read().decode('utf-8')
                if "API key not valid" in error_content or "Invalid API Key" in error_content or "403" in str(e.code):
                    summary_text = f"❌ API Key 無效或已過期\n\n請檢查：\n1. API Key 是否正確複製\n2. API Key 是否仍然有效\n3. 前往 https://aistudio.google.com/apikey 檢查\n\n發生在：{str(e)}"
                elif "429" in str(e.code):
                    summary_text = f"⚠️ API 配額已用完\n\nGoogle Gemini 免費版每天有配額限制\n請明天再試，或升級為付費版本\n\n錯誤代碼：{e.code}"
                else:
                    summary_text = f"🌐 API 請求失敗\n\n狀態代碼：{e.code}\n錯誤信息：{error_content[:200]}"
            except json.JSONDecodeError as e:
                summary_text = f"❌ 回應數據解析失敗\n\n請確認：\n1. API Key 是否正確\n2. 網路連線是否正常\n3. 可嘗試稍後重試\n\n錯誤詳情：{str(e)}"
            except Exception as e:
                summary_text = f"❌ 生成失敗：{str(e)}\n\n請檢查：\n1. API Key 是否正確\n2. 網路連線是否正常\n3. Gemini API 是否有效\n4. 配額是否足夠"
            
            # 在主執行緒中顯示結果
            self.root.after(0, self.show_summary_window, summary_text)
            
        except Exception as e:
            error_msg = f"生成總結失敗：{str(e)}"
            self.root.after(0, lambda: messagebox.showerror("錯誤", error_msg))
        finally:
            self.root.after(0, lambda: self.btn_summary.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.lbl_status.config(text="AI 總結生成完畢", fg="green"))

    def show_summary_window(self, summary_text):
        # 創建新視窗顯示總結
        summary_window = tk.Toplevel(self.root)
        summary_window.title("旅遊導覽總結")
        summary_window.geometry("700x500")
        
        # 文字框與捲動條
        frame = tk.Frame(summary_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(frame, font=("微軟正黑體", 11), wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        text_widget.insert(tk.END, summary_text)
        text_widget.config(state=tk.DISABLED)  # 設為唯讀
        
        # 關閉按鈕
        btn_close = tk.Button(summary_window, text="關閉", font=("微軟正黑體", 12),
                             bg="#f44336", fg="white", command=summary_window.destroy)
        btn_close.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = WebSearchApp(root)
    root.mainloop()