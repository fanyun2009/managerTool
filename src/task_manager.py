import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# 配置常量
TASK_FILE = "tasks.json"
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400


class TaskManagerApp:
    def __init__(self, root):
        # 主窗口配置
        self.root = root
        self.root.title("简易任务管理工具")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)

        # 任务数据存储
        self.tasks = []
        self.load_tasks()  # 加载本地任务

        # 创建UI组件
        self.create_widgets()

    def create_widgets(self):
        # 1. 顶部输入区域
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text="新增任务：").pack(side=tk.LEFT, padx=5)
        self.task_entry = ttk.Entry(input_frame, width=40)
        self.task_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        add_btn = ttk.Button(input_frame, text="添加", command=self.add_task)
        add_btn.pack(side=tk.LEFT, padx=5)

        # 2. 任务列表区域
        list_frame = ttk.Frame(self.root, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 列表表头
        columns = ("#1", "#2", "#3")
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        self.task_tree.heading("#1", text="序号")
        self.task_tree.heading("#2", text="任务内容")
        self.task_tree.heading("#3", text="状态")

        # 设置列宽
        self.task_tree.column("#1", width=80, anchor=tk.CENTER)
        self.task_tree.column("#2", width=350, anchor=tk.W)
        self.task_tree.column("#3", width=80, anchor=tk.CENTER)

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)

        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 3. 底部操作区域
        btn_frame = ttk.Frame(self.root, padding="10")
        btn_frame.pack(fill=tk.X)

        complete_btn = ttk.Button(btn_frame, text="标记完成", command=self.mark_complete)
        complete_btn.pack(side=tk.LEFT, padx=5)

        delete_btn = ttk.Button(btn_frame, text="删除选中", command=self.delete_task)
        delete_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(btn_frame, text="清空所有", command=self.clear_tasks)
        clear_btn.pack(side=tk.LEFT, padx=5)

        # 初始化列表显示
        self.refresh_task_list()

    def load_tasks(self):
        """从本地文件加载任务"""
        if os.path.exists(TASK_FILE):
            try:
                with open(TASK_FILE, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
            except Exception as e:
                messagebox.showerror("错误", f"加载任务失败：{str(e)}")
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self):
        """保存任务到本地文件"""
        try:
            with open(TASK_FILE, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存任务失败：{str(e)}")

    def refresh_task_list(self):
        """刷新任务列表显示"""
        # 清空现有内容
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        # 重新添加任务
        for idx, task in enumerate(self.tasks, 1):
            status = "已完成" if task["completed"] else "未完成"
            self.task_tree.insert("", tk.END, values=(idx, task["content"], status))

    def add_task(self):
        """添加新任务"""
        content = self.task_entry.get().strip()
        if not content:
            messagebox.showwarning("提示", "任务内容不能为空！")
            return
        # 添加任务到列表
        self.tasks.append({"content": content, "completed": False})
        # 保存并刷新
        self.save_tasks()
        self.refresh_task_list()
        # 清空输入框
        self.task_entry.delete(0, tk.END)

    def mark_complete(self):
        """标记选中任务为完成"""
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请选中要标记的任务！")
            return
        # 获取选中任务的索引
        idx = int(self.task_tree.item(selected[0], "values")[0]) - 1
        self.tasks[idx]["completed"] = True
        self.save_tasks()
        self.refresh_task_list()

    def delete_task(self):
        """删除选中的任务"""
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请选中要删除的任务！")
            return
        # 确认删除
        if not messagebox.askyesno("确认", "确定要删除选中的任务吗？"):
            return
        # 获取索引并删除
        idx = int(self.task_tree.item(selected[0], "values")[0]) - 1
        del self.tasks[idx]
        self.save_tasks()
        self.refresh_task_list()

    def clear_tasks(self):
        """清空所有任务"""
        if not self.tasks:
            messagebox.showinfo("提示", "暂无任务可清空！")
            return
        if messagebox.askyesno("确认", "确定要清空所有任务吗？"):
            self.tasks = []
            self.save_tasks()
            self.refresh_task_list()


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()