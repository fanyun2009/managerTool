import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random
from datetime import datetime

# 配置常量
TASK_FILE = "tasks.json"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CATEGORIES = ["工作", "学习", "生活"]
PRIORITIES = ["高", "中", "低"]


class TaskManagerApp:
    def __init__(self, root):
        # 主窗口配置
        self.root = root
        self.root.title("简易任务管理工具")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(True, True)

        # 任务数据存储
        self.tasks = []
        self.load_tasks()  # 加载本地任务

        # 创建UI组件
        self.create_widgets()

    def create_widgets(self):
        # 搜索区域
        search_frame = ttk.Frame(self.root, padding="10")
        search_frame.pack(fill=tk.X)
        ttk.Label(search_frame, text="搜索：").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_tasks)

        # 1. 顶部输入区域
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text="新增任务：").pack(side=tk.LEFT, padx=5)
        self.task_entry = ttk.Entry(input_frame, width=30)
        self.task_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        ttk.Label(input_frame, text="分类：").pack(side=tk.LEFT, padx=5)
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(input_frame, textvariable=self.category_var, values=CATEGORIES, width=8)
        self.category_combobox.current(0)
        self.category_combobox.pack(side=tk.LEFT, padx=5)

        ttk.Label(input_frame, text="优先级：").pack(side=tk.LEFT, padx=5)
        self.priority_var = tk.StringVar()
        self.priority_combobox = ttk.Combobox(input_frame, textvariable=self.priority_var, values=PRIORITIES, width=8)
        self.priority_combobox.current(1)
        self.priority_combobox.pack(side=tk.LEFT, padx=5)

        add_btn = ttk.Button(input_frame, text="添加", command=self.add_task)
        add_btn.pack(side=tk.LEFT, padx=5)

        # 2. 任务列表区域
        list_frame = ttk.Frame(self.root, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 列表表头
        columns = ("#1", "#2", "#3", "#4", "#5")
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        self.task_tree.heading("#1", text="序号")
        self.task_tree.heading("#2", text="任务内容")
        self.task_tree.heading("#3", text="分类")
        self.task_tree.heading("#4", text="优先级")
        self.task_tree.heading("#5", text="状态")

        # 设置列宽
        self.task_tree.column("#1", width=80, anchor=tk.CENTER)
        self.task_tree.column("#2", width=300, anchor=tk.W)
        self.task_tree.column("#3", width=100, anchor=tk.CENTER)
        self.task_tree.column("#4", width=100, anchor=tk.CENTER)
        self.task_tree.column("#5", width=100, anchor=tk.CENTER)

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

        sort_btn = ttk.Button(btn_frame, text="按优先级排序", command=self.sort_by_priority)
        sort_btn.pack(side=tk.LEFT, padx=5)

        stats_btn = ttk.Button(btn_frame, text="分类统计", command=self.show_category_stats)
        stats_btn.pack(side=tk.LEFT, padx=5)

        generate_btn = ttk.Button(btn_frame, text="生成测试数据", command=self.generate_test_tasks)
        generate_btn.pack(side=tk.LEFT, padx=5)

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

    def refresh_task_list(self, filtered_tasks=None):
        """刷新任务列表显示"""
        # 清空现有内容
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        # 重新添加任务
        tasks_to_show = filtered_tasks if filtered_tasks is not None else self.tasks
        for idx, task in enumerate(tasks_to_show, 1):
            status = "已完成" if task["completed"] else "未完成"
            category = task.get("category", "")
            priority = task.get("priority", "中")
            item = self.task_tree.insert("", tk.END, values=(idx, task["content"], category, priority, status))
            # 设置优先级颜色
            if priority == "高":
                self.task_tree.tag_configure("high", foreground="red")
                self.task_tree.item(item, tags=("high",))
            elif priority == "中":
                self.task_tree.tag_configure("medium", foreground="orange")
                self.task_tree.item(item, tags=("medium",))
            else:
                self.task_tree.tag_configure("low", foreground="gray")
                self.task_tree.item(item, tags=("low",))

    def add_task(self):
        """添加新任务"""
        content = self.task_entry.get().strip()
        if not content:
            messagebox.showwarning("提示", "任务内容不能为空！")
            return
        # 添加任务到列表
        self.tasks.append({
            "content": content,
            "completed": False,
            "category": self.category_var.get(),
            "priority": self.priority_var.get()
        })
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

    def filter_tasks(self, event=None):
        """根据搜索框内容过滤任务"""
        keyword = self.search_entry.get().strip().lower()
        if not keyword:
            self.refresh_task_list()
            return
        filtered = [task for task in self.tasks if keyword in task["content"].lower() or keyword in task.get("category", "").lower()]
        self.refresh_task_list(filtered)

    def sort_by_priority(self):
        """按优先级排序任务"""
        priority_order = {"高": 0, "中": 1, "低": 2}
        self.tasks.sort(key=lambda x: priority_order.get(x.get("priority", "中"), 1))
        self.refresh_task_list()

    def show_category_stats(self):
        """显示分类统计信息"""
        stats = {}
        for category in CATEGORIES:
            category_tasks = [task for task in self.tasks if task.get("category", "") == category]
            if not category_tasks:
                continue
            completed = sum(1 for task in category_tasks if task["completed"])
            total = len(category_tasks)
            rate = (completed / total) * 100 if total > 0 else 0
            stats[category] = (total, completed, rate)
        
        if not stats:
            messagebox.showinfo("统计", "暂无任务数据！")
            return
        
        stats_text = "分类统计结果：\n"
        for category, (total, completed, rate) in stats.items():
            stats_text += f"{category}: 共{total}个任务，完成{completed}个，完成率{rate:.1f}%\n"
        messagebox.showinfo("分类统计", stats_text)

    def generate_test_tasks(self):
        """生成测试任务数据"""
        task_contents = [
            "完成项目文档编写", "学习Python编程", "打扫房间卫生",
            "参加团队会议", "阅读技术书籍", "锻炼身体",
            "编写单元测试", "学习机器学习", "准备晚餐",
            "提交代码PR", "观看在线课程", "整理桌面"
        ]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("生成测试数据")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        
        ttk.Label(dialog, text="生成任务数量：").pack(pady=10)
        count_var = tk.IntVar(value=5)
        count_spinbox = ttk.Spinbox(dialog, from_=1, to=20, textvariable=count_var, width=10)
        count_spinbox.pack(pady=5)
        
        clear_var = tk.BooleanVar(value=False)
        clear_check = ttk.Checkbutton(dialog, text="清空现有数据后生成", variable=clear_var)
        clear_check.pack(pady=10)
        
        def confirm_generate():
            count = count_var.get()
            if clear_var.get():
                self.tasks = []
            for _ in range(count):
                self.tasks.append({
                    "content": random.choice(task_contents),
                    "completed": random.choice([True, False]),
                    "category": random.choice(CATEGORIES),
                    "priority": random.choice(PRIORITIES)
                })
            self.save_tasks()
            self.refresh_task_list()
            dialog.destroy()
            messagebox.showinfo("成功", f"已生成{count}个测试任务！")
        
        ttk.Button(dialog, text="生成", command=confirm_generate).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()