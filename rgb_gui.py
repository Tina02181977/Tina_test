import tkinter as tk
from tkinter import messagebox

class RGBColorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RGB调色盘")
        self.root.geometry("500x700")
        self.root.config(bg="#f0f0f0")
        
        # 初始化RGB值
        self.red_var = tk.IntVar(value=128)
        self.green_var = tk.IntVar(value=128)
        self.blue_var = tk.IntVar(value=128)
        
        # 标题
        title_label = tk.Label(
            self.root,
            text="RGB调色盘",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0"
        )
        title_label.pack(pady=15)
        
        # 颜色预览框
        preview_label = tk.Label(self.root, text="预览颜色：", font=("Arial", 12, "bold"), bg="#f0f0f0")
        preview_label.pack(pady=5)
        
        self.preview_canvas = tk.Canvas(
            self.root,
            width=300,
            height=100,
            bg="#808080",
            border=2,
            relief=tk.SUNKEN
        )
        self.preview_canvas.pack(pady=10)
        
        # 颜色信息显示
        self.info_label = tk.Label(
            self.root,
            text="RGB: (128, 128, 128) | Hex: #808080",
            font=("Arial", 11),
            bg="#f0f0f0",
            fg="#333333"
        )
        self.info_label.pack(pady=5)
        
        # 滑块容器
        slider_container = tk.Frame(self.root, bg="#f0f0f0")
        slider_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 红色滑块
        self.create_slider(slider_container, "红色 (R)", self.red_var, "#FF6B6B")
        
        # 绿色滑块
        self.create_slider(slider_container, "绿色 (G)", self.green_var, "#6BFF6B")
        
        # 蓝色滑块
        self.create_slider(slider_container, "蓝色 (B)", self.blue_var, "#6B6BFF")
        
        # 按钮框架（放在最下面）
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=15)
        
        # 重置按钮
        reset_button = tk.Button(
            button_frame,
            text="重置为灰色",
            command=self.reset_colors,
            font=("Arial", 11),
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=8
        )
        reset_button.pack(side=tk.LEFT, padx=10)
        
        # 打印按钮
        print_button = tk.Button(
            button_frame,
            text="打印颜色信息",
            command=self.print_colors,
            font=("Arial", 11),
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=8
        )
        print_button.pack(side=tk.LEFT, padx=10)
        
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
        
        # 初始化颜色显示
        self.update_color()
    
    def create_slider(self, parent, name, var, color):
        """创建RGB滑块"""
        frame = tk.Frame(parent, bg="#f0f0f0")
        frame.pack(fill=tk.X, pady=10)
        
        # 标签
        label = tk.Label(
            frame,
            text=name,
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            width=12,
            anchor=tk.W
        )
        label.pack(side=tk.LEFT, padx=10)
        
        # 滑块
        slider = tk.Scale(
            frame,
            from_=0,
            to=255,
            orient=tk.HORIZONTAL,
            variable=var,
            command=lambda x: self.update_color(),
            bg=color,
            fg="white",
            troughcolor="#ddd",
            length=200
        )
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # 数值显示
        value_label = tk.Label(
            frame,
            font=("Arial", 11),
            bg="#f0f0f0",
            width=4,
            anchor=tk.E
        )
        value_label.pack(side=tk.LEFT, padx=10)
        
        # 更新数值显示
        var.trace("w", lambda *args: value_label.config(text=var.get()))
    
    def update_color(self):
        """更新颜色预览"""
        r = self.red_var.get()
        g = self.green_var.get()
        b = self.blue_var.get()
        
        # 转换为十六进制颜色
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        
        # 更新预览画布颜色
        self.preview_canvas.config(bg=hex_color)
        
        # 更新信息标签
        self.info_label.config(text=f"RGB: ({r}, {g}, {b}) | Hex: {hex_color}")
    
    def reset_colors(self):
        """重置为灰色"""
        self.red_var.set(128)
        self.green_var.set(128)
        self.blue_var.set(128)
        self.update_color()
    
    def print_colors(self):
        """打印当前颜色信息"""
        r = self.red_var.get()
        g = self.green_var.get()
        b = self.blue_var.get()
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        
        colors_info = f"""
当前调色盘颜色信息：

RGB值: ({r}, {g}, {b})
十六进制: {hex_color}
说明: 自由混合的RGB颜色

三原色份量：
  红色 (R): {r} (0-255)
  绿色 (G): {g} (0-255)
  蓝色 (B): {b} (0-255)
        """
        print(colors_info)
        messagebox.showinfo("当前颜色信息", colors_info)

if __name__ == "__main__":
    root = tk.Tk()
    app = RGBColorGUI(root)
    root.mainloop()
