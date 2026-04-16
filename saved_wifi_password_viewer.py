import subprocess, re, sys, tkinter as tk
from tkinter import ttk, messagebox, filedialog

class WiFiPasswordViewer:
    def __init__(self, master):
        self.master = master
        master.title("已保存的WiFi密码查看器")
        master.geometry("500x600")

        tool = ttk.Frame(master)
        tool.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(tool, text="刷新列表", command=self.load).pack(side=tk.LEFT, padx=2)
        ttk.Button(tool, text="导出全部", command=lambda: self.export(True)).pack(side=tk.LEFT, padx=2)

        self.search = tk.StringVar()
        ttk.Entry(tool, textvariable=self.search, width=25).pack(side=tk.RIGHT, padx=5)
        self.search.trace('w', lambda *_: self.filter())
        ttk.Label(tool, text="搜索:").pack(side=tk.RIGHT)

        self.tree = ttk.Treeview(master, columns=('name','pwd'), show='headings')
        self.tree.heading('name', text='WiFi名称')
        self.tree.heading('pwd', text='WiFi密码')
        self.tree.column('name', width=250, anchor='center')
        self.tree.column('pwd', width=250, anchor='center')
        vsb = ttk.Scrollbar(master, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.status = ttk.Label(master, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        menu = tk.Menu(master, tearoff=0)
        menu.add_command(label="复制密码", command=self.copy)
        menu.add_separator()
        menu.add_command(label="导出选中", command=lambda: self.export(False))
        self.tree.bind("<Button-3>", lambda e: self.tree.selection_set(self.tree.identify_row(e.y)) or menu.post(e.x_root, e.y_root))

        try:
            subprocess.check_output(['netsh','wlan','show','profiles'], stderr=subprocess.STDOUT)
        except:
            messagebox.showerror("权限错误", "请以管理员身份运行")
            sys.exit(1)

        self.load()

    def get(self):
        try:
            out = subprocess.check_output(['netsh','wlan','show','profiles'], encoding='gbk')
            return re.findall(r'(?:所有用户配置文件|All User Profile)\s*:\s*(.*)', out)
        except:
            return []

    def pwd(self, name):
        try:
            out = subprocess.check_output(['netsh','wlan','show','profile',name,'key=clear'], encoding='gbk')
            m = re.search(r'(?:关键内容|Key Content)\s*:\s*(.*)', out)
            return m.group(1).strip() if m else "无密码"
        except:
            return "获取失败"

    def load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.status.config(text="扫描中...")
        profiles = self.get()
        if not profiles:
            self.status.config(text="未找到WiFi")
            return
        for i, name in enumerate(profiles, 1):
            self.tree.insert('', 'end', values=(name, self.pwd(name)))
            self.status.config(text=f"{name} ({i}/{len(profiles)})")
        self.status.config(text=f"完成，共 {len(profiles)} 个")

    def filter(self):
        kw = self.search.get().lower()
        for child in self.tree.get_children():
            if kw in self.tree.item(child)['values'][0].lower():
                self.tree.reattach(child, '', 'end')
            else:
                self.tree.detach(child)

    def export(self, all_=True):
        items = self.tree.get_children() if all_ else self.tree.selection()
        if not items:
            messagebox.showwarning("提示", "没有数据可导出")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("文本文件","*.txt"),("CSV文件","*.csv")])
        if not path:
            return
        sep = ',' if path.endswith('.csv') else '\t'
        with open(path, 'w', encoding='utf-8-sig') as f:
            f.write(f"WiFi名称{sep}WiFi密码\n")
            for item in items:
                n, p = self.tree.item(item)['values']
                f.write(f"{n}{sep}{p}\n")
        self.status.config(text=f"已导出 {path}")
        messagebox.showinfo("成功", "导出完成")

    def copy(self):
        sel = self.tree.selection()
        if sel:
            self.master.clipboard_clear()
            self.master.clipboard_append(self.tree.item(sel[0])['values'][1])
            self.status.config(text="密码已复制")

if __name__ == "__main__":
    root = tk.Tk()
    app = WiFiPasswordViewer(root)
    root.mainloop()
