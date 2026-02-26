import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import os

class FileSearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("文件内容搜索")
        self.root.geometry("700x800")
        self.root.config(bg="#f0f0f0")
        
        self.file_path = ""
        self.search_results = []  # 存储搜索结果
        self.current_page = 1
        self.results_per_page = 10  # 每页显示的行数
        
        # 标题
        title_label = tk.Label(
            self.root,
            text="文件内容搜索工具",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0"
        )
        title_label.pack(pady=15)
        
        # 文件选择框架
        file_frame = tk.Frame(self.root, bg="#f0f0f0")
        file_frame.pack(fill=tk.X, padx=20, pady=10)
        
        file_label = tk.Label(file_frame, text="选择文件：", font=("Arial", 11, "bold"), bg="#f0f0f0")
        file_label.pack(side=tk.LEFT, padx=10)
        
        self.file_entry = tk.Entry(file_frame, font=("Arial", 10), width=50)
        self.file_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        browse_button = tk.Button(
            file_frame,
            text="浏览",
            command=self.browse_file,
            font=("Arial", 10),
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=5
        )
        browse_button.pack(side=tk.LEFT, padx=10)
        
        # 搜索关键词框架
        search_frame = tk.Frame(self.root, bg="#f0f0f0")
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        search_label = tk.Label(search_frame, text="搜索关键词：", font=("Arial", 11, "bold"), bg="#f0f0f0")
        search_label.pack(side=tk.LEFT, padx=10)
        
        self.search_entry = tk.Entry(search_frame, font=("Arial", 10), width=50)
        self.search_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.search_entry.bind("<Return>", lambda e: self.search_file())
        
        search_button = tk.Button(
            search_frame,
            text="搜索",
            command=self.search_file,
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=5
        )
        search_button.pack(side=tk.LEFT, padx=10)
        
        # 搜索选项框架
        options_frame = tk.Frame(self.root, bg="#f0f0f0")
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.case_sensitive = tk.BooleanVar(value=False)
        case_check = tk.Checkbutton(
            options_frame,
            text="区分大小写",
            variable=self.case_sensitive,
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        case_check.pack(side=tk.LEFT, padx=10)
        
        self.show_line_num = tk.BooleanVar(value=True)
        line_check = tk.Checkbutton(
            options_frame,
            text="显示行号",
            variable=self.show_line_num,
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        line_check.pack(side=tk.LEFT, padx=10)
        
        # 每页行数设置
        page_label = tk.Label(options_frame, text="每页显示：", font=("Arial", 10), bg="#f0f0f0")
        page_label.pack(side=tk.LEFT, padx=10)
        
        self.page_var = tk.StringVar(value="10")
        page_spin = tk.Spinbox(
            options_frame,
            from_=5,
            to=50,
            textvariable=self.page_var,
            font=("Arial", 10),
            width=5
        )
        page_spin.pack(side=tk.LEFT, padx=5)
        
        page_unit = tk.Label(options_frame, text="行", font=("Arial", 10), bg="#f0f0f0")
        page_unit.pack(side=tk.LEFT, padx=0)
        
        # 搜索结果标签
        result_label = tk.Label(
            self.root,
            text="搜索结果：",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            anchor=tk.W
        )
        result_label.pack(fill=tk.X, padx=20, pady=(10, 5))
        
        # 分页导航框架
        page_nav_frame = tk.Frame(self.root, bg="#f0f0f0")
        page_nav_frame.pack(fill=tk.X, padx=20, pady=5)
        
        prev_button = tk.Button(
            page_nav_frame,
            text="< 上一页",
            command=self.prev_page,
            font=("Arial", 10),
            bg="#FF9800",
            fg="white",
            padx=10,
            pady=5,
            width=10
        )
        prev_button.pack(side=tk.LEFT, padx=5)
        
        self.page_info_label = tk.Label(
            page_nav_frame,
            text="第 1 页 / 共 1 页",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0",
            width=20
        )
        self.page_info_label.pack(side=tk.LEFT, padx=20)
        
        next_button = tk.Button(
            page_nav_frame,
            text="下一页 >",
            command=self.next_page,
            font=("Arial", 10),
            bg="#FF9800",
            fg="white",
            padx=10,
            pady=5,
            width=10
        )
        next_button.pack(side=tk.LEFT, padx=5)
        
        # 搜索结果显示框
        self.result_text = scrolledtext.ScrolledText(
            self.root,
            font=("Courier", 10),
            height=20,
            width=80,
            bg="white",
            fg="#333333",
            relief=tk.SUNKEN,
            border=2
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 配置文本标签颜色
        self.result_text.tag_config("keyword", foreground="red", font=("Courier", 10, "bold"))
        self.result_text.tag_config("line_num", foreground="blue", font=("Courier", 10, "bold"))
        
        # 统计信息标签
        self.info_label = tk.Label(
            self.root,
            text="就绪",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666666"
        )
        self.info_label.pack(fill=tk.X, padx=20, pady=5)
        
        # 按钮框架
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=15)
        
        clear_button = tk.Button(
            button_frame,
            text="清空结果",
            command=self.clear_results,
            font=("Arial", 10),
            bg="#FF9800",
            fg="white",
            padx=15,
            pady=8
        )
        clear_button.pack(side=tk.LEFT, padx=10)
        
        copy_button = tk.Button(
            button_frame,
            text="复制结果",
            command=self.copy_results,
            font=("Arial", 10),
            bg="#9C27B0",
            fg="white",
            padx=15,
            pady=8
        )
        copy_button.pack(side=tk.LEFT, padx=10)
        
        exit_button = tk.Button(
            button_frame,
            text="退出",
            command=self.root.quit,
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            padx=15,
            pady=8
        )
        exit_button.pack(side=tk.LEFT, padx=10)
    
    def browse_file(self):
        """浏览选择文件"""
        filetypes = (
            ("所有文件", "*.*"),
            ("文本文件", "*.txt"),
            ("Python文件", "*.py"),
            ("日志文件", "*.log"),
        )
        file_path = filedialog.askopenfilename(
            title="选择要搜索的文件",
            filetypes=filetypes
        )
        if file_path:
            self.file_path = file_path
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.info_label.config(text=f"已选择: {os.path.basename(file_path)}")
    
    def search_file(self):
        """搜索文件内容"""
        file_path = self.file_entry.get()
        keyword = self.search_entry.get()
        
        if not file_path:
            messagebox.showwarning("警告", "请先选择文件！")
            return
        
        if not keyword:
            messagebox.showwarning("警告", "请输入搜索关键词！")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("错误", "文件不存在！")
            return
        
        try:
            self.search_results = []
            self.results_per_page = int(self.page_var.get())
            self.current_page = 1
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                for line_num, line in enumerate(file, 1):
                    if self.case_sensitive.get():
                        is_match = keyword in line
                    else:
                        is_match = keyword.lower() in line.lower()
                    
                    if is_match:
                        self.search_results.append({
                            'line_num': line_num,
                            'content': line.rstrip('\n'),
                            'keyword': keyword
                        })
            
            if self.search_results:
                self.display_page()
                self.info_label.config(
                    text=f"搜索完成 - 共找到 {len(self.search_results)} 个匹配行",
                    fg="#4CAF50"
                )
                print(f"搜索完成：共找到 {len(self.search_results)} 个匹配行")
            else:
                self.result_text.config(state=tk.NORMAL)
                self.result_text.delete(1.0, tk.END)
                self.result_text.config(state=tk.DISABLED)
                self.info_label.config(
                    text=f"搜索完成 - 未找到匹配项",
                    fg="#f44336"
                )
                messagebox.showinfo("搜索结果", "未找到匹配的内容！")
                self.update_page_label()
            
        except Exception as e:
            messagebox.showerror("错误", f"读取文件出错：{str(e)}")
    
    def display_page(self):
        """显示当前页的搜索结果"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        if not self.search_results:
            self.result_text.config(state=tk.DISABLED)
            return
        
        start_idx = (self.current_page - 1) * self.results_per_page
        end_idx = min(start_idx + self.results_per_page, len(self.search_results))
        
        for i, result in enumerate(self.search_results[start_idx:end_idx], 1):
            line_num = result['line_num']
            content = result['content']
            keyword = result['keyword']
            result_num = start_idx + i  # 结果序号
            page_num = self.current_page
            
            # 显示页号、序号和行号
            header = f"[第 {page_num} 页] [结果 #{result_num}] [第 {line_num} 行] "
            self.result_text.insert(tk.END, header, "line_num")
            
            # 显示内容，高亮关键词
            if self.case_sensitive.get():
                parts = content.split(keyword)
                for j, part in enumerate(parts):
                    self.result_text.insert(tk.END, part)
                    if j < len(parts) - 1:
                        self.result_text.insert(tk.END, keyword, "keyword")
            else:
                # 不区分大小写的高亮
                remaining = content
                while True:
                    lower_pos = remaining.lower().find(keyword.lower())
                    if lower_pos == -1:
                        self.result_text.insert(tk.END, remaining)
                        break
                    self.result_text.insert(tk.END, remaining[:lower_pos])
                    self.result_text.insert(tk.END, remaining[lower_pos:lower_pos+len(keyword)], "keyword")
                    remaining = remaining[lower_pos+len(keyword):]
            
            self.result_text.insert(tk.END, "\n")
        
        self.result_text.config(state=tk.DISABLED)
        self.update_page_label()
    
    def update_page_label(self):
        """更新页码标签"""
        total_pages = (len(self.search_results) + self.results_per_page - 1) // self.results_per_page
        if total_pages == 0:
            total_pages = 1
        self.page_info_label.config(text=f"第 {self.current_page} 页 / 共 {total_pages} 页")
    
    def prev_page(self):
        """显示上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.display_page()
        else:
            messagebox.showinfo("提示", "已经是第一页了！")
    
    def next_page(self):
        """显示下一页"""
        total_pages = (len(self.search_results) + self.results_per_page - 1) // self.results_per_page
        if total_pages == 0:
            total_pages = 1
        if self.current_page < total_pages:
            self.current_page += 1
            self.display_page()
        else:
            messagebox.showinfo("提示", "已经是最后一页了！")
    
    def clear_results(self):
        """清空搜索结果"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.search_results = []
        self.current_page = 1
        self.info_label.config(text="结果已清空", fg="#666666")
        self.update_page_label()
    
    def copy_results(self):
        """复制搜索结果到剪贴板"""
        try:
            content = self.result_text.get(1.0, tk.END)
            if content.strip():
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                self.root.update()
                messagebox.showinfo("成功", "搜索结果已复制到剪贴板！")
            else:
                messagebox.showwarning("提示", "没有结果可复制！")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败：{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSearchGUI(root)
    root.mainloop()
