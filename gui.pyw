import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, font
import os

class LightweightTextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("轻量级文本编辑器")
        self.root.geometry("800x600")
        self.root.minsize(400, 300)
        
        # 初始化变量
        self.current_file = None
        self.font_size = 12
        self.font_family = "Consolas"
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建状态栏
        self.create_statusbar()
        
        # 创建文本区域
        self.create_text_area()
        
        # 绑定快捷键
        self.bind_shortcuts()
        
        # 更新状态栏
        self.update_statusbar()
    
    def create_menu(self):
        # 创建主菜单
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="打开", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="保存", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="另存为", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.exit_app, accelerator="Ctrl+Q")
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="撤销", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="重做", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="剪切", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="复制", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="粘贴", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="全选", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="查找", command=self.find_text, accelerator="Ctrl+F")
        menubar.add_cascade(label="编辑", menu=edit_menu)
        
        # 格式菜单
        format_menu = tk.Menu(menubar, tearoff=0)
        format_menu.add_command(label="字体", command=self.change_font)
        format_menu.add_command(label="增大字体", command=lambda: self.change_font_size(1))
        format_menu.add_command(label="减小字体", command=lambda: self.change_font_size(-1))
        menubar.add_cascade(label="格式", menu=format_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_toolbar(self):
        # 创建工具栏
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        
        # 添加工具栏按钮
        buttons = [
            ("新建", self.new_file, "icons/new.png"),
            ("打开", self.open_file, "icons/open.png"),
            ("保存", self.save_file, "icons/save.png"),
            ("剪切", self.cut, "icons/cut.png"),
            ("复制", self.copy, "icons/copy.png"),
            ("粘贴", self.paste, "icons/paste.png"),
            ("查找", self.find_text, "icons/find.png")
        ]
        
        # 创建按钮（使用文本代替图标）
        for text, command, _ in buttons:
            btn = tk.Button(toolbar, text=text, command=command, relief=tk.FLAT, padx=2, pady=2)
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        toolbar.pack(side=tk.TOP, fill=tk.X)
    
    def create_text_area(self):
        # 创建文本区域和滚动条
        frame = tk.Frame(self.root)
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建文本编辑器
        self.text_area = tk.Text(
            frame, 
            wrap=tk.WORD, 
            yscrollcommand=scrollbar.set,
            undo=True,
            autoseparators=True,
            maxundo=-1,
            font=(self.font_family, self.font_size)
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.text_area.yview)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 绑定文本修改事件
        self.text_area.bind("<<Modified>>", self.on_text_modified)
        self.text_area.bind("<KeyRelease>", self.update_statusbar)
    
    def create_statusbar(self):
        # 创建状态栏
        self.status_bar = tk.Label(
            self.root, 
            text="就绪 | 行: 1, 列: 1 | 字数: 0", 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def bind_shortcuts(self):
        # 绑定快捷键
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-q>", lambda e: self.exit_app())
        self.root.bind("<Control-f>", lambda e: self.find_text())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-x>", lambda e: self.cut())
        self.root.bind("<Control-c>", lambda e: self.copy())
        self.root.bind("<Control-v>", lambda e: self.paste())
        self.root.bind("<Control-a>", lambda e: self.select_all())
    
    def on_text_modified(self, event=None):
        # 当文本修改时更新状态
        if self.text_area.edit_modified():
            title = self.root.title()
            if not title.startswith("*"):
                self.root.title("*" + title)
            self.text_area.edit_modified(False)
    
    def update_statusbar(self, event=None):
        # 更新状态栏信息
        text = self.text_area.get("1.0", tk.END)
        lines = text.split("\n")
        line_count = len(lines)
        
        # 获取当前光标位置
        cursor_pos = self.text_area.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        
        # 计算字数（非空白字符）
        word_count = len(text.replace('\n', ' ').split())
        
        # 更新状态栏
        self.status_bar.config(text=f"就绪 | 行: {line}, 列: {col} | 行数: {line_count-1} | 字数: {word_count}")
    
    def new_file(self):
        # 新建文件
        if self.text_area.edit_modified():
            if not self.prompt_save():
                return
        
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.root.title("轻量级文本编辑器 - 无标题")
        self.text_area.edit_modified(False)
    
    def open_file(self):
        # 打开文件
        if self.text_area.edit_modified():
            if not self.prompt_save():
                return
        
        file_path = filedialog.askopenfilename(
            filetypes=[("文本文档", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, content)
                    self.text_area.edit_modified(False)
                    self.current_file = file_path
                    self.root.title(f"轻量级文本编辑器 - {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件:\n{str(e)}")
    
    def save_file(self):
        # 保存文件
        if self.current_file:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(self.current_file, "w", encoding="utf-8") as file:
                    file.write(content)
                self.text_area.edit_modified(False)
                self.root.title(f"轻量级文本编辑器 - {os.path.basename(self.current_file)}")
                messagebox.showinfo("保存成功", "文件已成功保存！")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存文件:\n{str(e)}")
        else:
            self.save_as()
    
    def save_as(self):
        # 另存为文件
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文档", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                self.text_area.edit_modified(False)
                self.current_file = file_path
                self.root.title(f"轻量级文本编辑器 - {os.path.basename(file_path)}")
                messagebox.showinfo("保存成功", "文件已成功保存！")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存文件:\n{str(e)}")
    
    def prompt_save(self):
        # 提示保存更改
        response = messagebox.askyesnocancel(
            "保存更改",
            "是否保存对文件的更改?"
        )
        
        if response is None:  # 取消
            return False
        elif response:  # 是
            self.save_file()
        return True
    
    def exit_app(self):
        # 退出应用
        if self.text_area.edit_modified():
            if not self.prompt_save():
                return
        
        self.root.destroy()
    
    def undo(self):
        # 撤销操作
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass
    
    def redo(self):
        # 重做操作
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            pass
    
    def cut(self):
        # 剪切文本
        self.text_area.event_generate("<<Cut>>")
    
    def copy(self):
        # 复制文本
        self.text_area.event_generate("<<Copy>>")
    
    def paste(self):
        # 粘贴文本
        self.text_area.event_generate("<<Paste>>")
    
    def select_all(self):
        # 全选文本
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
    
    def find_text(self):
        # 查找文本
        find_str = simpledialog.askstring("查找", "输入要查找的文本:")
        if find_str:
            content = self.text_area.get(1.0, tk.END)
            start_pos = self.text_area.search(
                find_str, 
                tk.INSERT, 
                nocase=1, 
                stopindex=tk.END
            )
            
            if start_pos:
                end_pos = f"{start_pos}+{len(find_str)}c"
                self.text_area.tag_remove(tk.SEL, 1.0, tk.END)
                self.text_area.tag_add(tk.SEL, start_pos, end_pos)
                self.text_area.mark_set(tk.INSERT, end_pos)
                self.text_area.see(tk.INSERT)
            else:
                messagebox.showinfo("查找", "未找到匹配的文本")
    
    def change_font(self):
        # 更改字体
        font_window = tk.Toplevel(self.root)
        font_window.title("选择字体")
        font_window.geometry("300x200")
        font_window.transient(self.root)
        font_window.grab_set()
        
        # 获取可用字体
        available_fonts = list(font.families())
        available_fonts.sort()
        
        # 创建字体选择列表
        tk.Label(font_window, text="字体:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        font_listbox = tk.Listbox(font_window, width=30, height=10)
        font_listbox.grid(row=1, column=0, padx=10, pady=5, columnspan=2)
        
        # 添加字体到列表
        for f in available_fonts:
            font_listbox.insert(tk.END, f)
        
        # 设置当前选中字体
        try:
            index = available_fonts.index(self.font_family)
            font_listbox.selection_set(index)
            font_listbox.see(index)
        except ValueError:
            pass
        
        # 字体大小选择
        tk.Label(font_window, text="大小:").grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
        size_var = tk.StringVar(value=str(self.font_size))
        size_spinbox = tk.Spinbox(
            font_window, 
            from_=8, 
            to=72, 
            textvariable=size_var, 
            width=5
        )
        size_spinbox.grid(row=0, column=3, padx=10, pady=5)
        
        # 确定按钮
        def apply_font():
            selected = font_listbox.curselection()
            if selected:
                self.font_family = font_listbox.get(selected[0])
                self.font_size = int(size_var.get())
                self.text_area.config(font=(self.font_family, self.font_size))
                font_window.destroy()
        
        tk.Button(
            font_window, 
            text="确定", 
            command=apply_font,
            width=10
        ).grid(row=2, column=0, columnspan=4, pady=10)
    
    def change_font_size(self, delta):
        # 更改字体大小
        self.font_size += delta
        if self.font_size < 8:
            self.font_size = 8
        elif self.font_size > 72:
            self.font_size = 72
        
        self.text_area.config(font=(self.font_family, self.font_size))
    
    def show_about(self):
        # 显示关于信息
        about_text = (
            "轻量级文本编辑器\n\n"
            "版本: 1.0\n"
            "作者: Python Tkinter\n\n"
            "一个简单、快速的文本编辑器，支持基本的文本编辑功能。"
        )
        messagebox.showinfo("关于", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    editor = LightweightTextEditor(root)
    root.mainloop()