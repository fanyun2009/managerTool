import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# 配置常量
TASK_FILE = "tasks.json"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


class TaskManagerApp:
    def __init__(self, root):
        # 主窗口配置
        self.root = root
        self.root.title("任务管理工具 - 增强版")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(700, 500)  # 设置最小尺寸
        self.root.resizable(True, True)  # 允许调整窗口大小

        # 任务数据存储
        self.tasks = []
        self.load_tasks()  # 加载本地任务

        # 创建UI组件
        self.create_widgets()

    def create_widgets(self):
        # 1. 顶部输入区域 - 使用两行布局
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(fill=tk.X)

        # 第一行：任务内容输入
        row1_frame = ttk.Frame(input_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(row1_frame, text="新增任务：").pack(side=tk.LEFT, padx=5)
        self.task_entry = ttk.Entry(row1_frame, width=50)
        self.task_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 第二行：分类、优先级选择和添加按钮
        row2_frame = ttk.Frame(input_frame)
        row2_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 分类选择
        ttk.Label(row2_frame, text="分类：").pack(side=tk.LEFT, padx=5)
        self.category_var = tk.StringVar(value="工作")
        self.category_combo = ttk.Combobox(row2_frame, textvariable=self.category_var, 
                                          values=["工作", "学习", "生活"], width=10, state="readonly")
        self.category_combo.pack(side=tk.LEFT, padx=5)

        # 优先级选择
        ttk.Label(row2_frame, text="优先级：").pack(side=tk.LEFT, padx=15)
        self.priority_var = tk.StringVar(value="中")
        self.priority_combo = ttk.Combobox(row2_frame, textvariable=self.priority_var,
                                          values=["高", "中", "低"], width=8, state="readonly")
        self.priority_combo.pack(side=tk.LEFT, padx=5)

        # 添加按钮
        add_btn = ttk.Button(row2_frame, text="添加任务", command=self.add_task, width=12)
        add_btn.pack(side=tk.LEFT, padx=15)

        # 2. 任务列表区域
        list_frame = ttk.Frame(self.root, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 列表表头
        columns = ("#1", "#2", "#3", "#4", "#5")
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        self.task_tree.heading("#1", text="序号")
        self.task_tree.heading("#2", text="任务内容")
        self.task_tree.heading("#3", text="分类")
        self.task_tree.heading("#4", text="优先级")
        self.task_tree.heading("#5", text="状态")

        # 设置列宽
        self.task_tree.column("#1", width=50, anchor=tk.CENTER)
        self.task_tree.column("#2", width=250, anchor=tk.W)
        self.task_tree.column("#3", width=60, anchor=tk.CENTER)
        self.task_tree.column("#4", width=60, anchor=tk.CENTER)
        self.task_tree.column("#5", width=60, anchor=tk.CENTER)

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)

        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 3. 搜索和排序区域 - 使用更紧凑的布局
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # 左侧：搜索框
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(search_frame, text="搜索：").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_var.trace("w", self.on_search_change)
        
        # 右侧：排序选项
        sort_frame = ttk.Frame(control_frame)
        sort_frame.pack(side=tk.LEFT)
        
        ttk.Label(sort_frame, text="排序：").pack(side=tk.LEFT, padx=5)
        self.sort_var = tk.StringVar(value="默认")
        self.sort_combo = ttk.Combobox(sort_frame, textvariable=self.sort_var,
                                        values=["默认", "优先级高→低", "优先级低→高", "分类"], 
                                        width=12, state="readonly")
        self.sort_combo.pack(side=tk.LEFT, padx=5)
        self.sort_var.trace("w", self.on_sort_change)

        # 4. 统计区域
        stats_frame = ttk.Frame(self.root, padding="10")
        stats_frame.pack(fill=tk.X)
        
        self.stats_label = ttk.Label(stats_frame, text="统计信息加载中...")
        self.stats_label.pack(side=tk.LEFT, padx=5)

        # 5. 底部操作区域 - 使用更紧凑的布局
        btn_frame = ttk.Frame(self.root, padding="10")
        btn_frame.pack(fill=tk.X)

        # 左侧：主要操作按钮
        main_btn_frame = ttk.Frame(btn_frame)
        main_btn_frame.pack(side=tk.LEFT)
        
        complete_btn = ttk.Button(main_btn_frame, text="标记完成", command=self.mark_complete, width=10)
        complete_btn.pack(side=tk.LEFT, padx=3)

        delete_btn = ttk.Button(main_btn_frame, text="删除选中", command=self.delete_task, width=10)
        delete_btn.pack(side=tk.LEFT, padx=3)

        clear_btn = ttk.Button(main_btn_frame, text="清空所有", command=self.clear_tasks, width=10)
        clear_btn.pack(side=tk.LEFT, padx=3)

        # 右侧：生成测试数据按钮
        gen_btn_frame = ttk.Frame(btn_frame)
        gen_btn_frame.pack(side=tk.RIGHT)
        
        generate_btn = ttk.Button(gen_btn_frame, text="生成测试数据", command=self.generate_test_data, width=12)
        generate_btn.pack(side=tk.LEFT, padx=3)

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
        
        # 获取搜索关键词
        search_keyword = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        
        # 过滤任务
        filtered_tasks = []
        for idx, task in enumerate(self.tasks, 1):
            # 搜索过滤
            if search_keyword and search_keyword not in task["content"].lower():
                continue
            filtered_tasks.append((idx, task))
        
        # 排序处理
        if hasattr(self, 'sort_var') and self.sort_var.get() != "默认":
            sort_type = self.sort_var.get()
            if sort_type == "优先级高→低":
                priority_order = {"高": 0, "中": 1, "低": 2}
                filtered_tasks.sort(key=lambda x: priority_order.get(x[1].get("priority", "中"), 3))
            elif sort_type == "优先级低→高":
                priority_order = {"低": 0, "中": 1, "高": 2}
                filtered_tasks.sort(key=lambda x: priority_order.get(x[1].get("priority", "中"), 3))
            elif sort_type == "分类":
                filtered_tasks.sort(key=lambda x: x[1].get("category", "工作"))
        
        # 重新添加任务
        for idx, task in filtered_tasks:
            status = "已完成" if task["completed"] else "未完成"
            # 设置优先级颜色
            priority = task.get("priority", "中")
            tag = f"priority_{priority}"
            self.task_tree.insert("", tk.END, values=(idx, task["content"], task.get("category", "工作"), priority, status), tags=(tag,))
        
        # 设置优先级颜色
        self.task_tree.tag_configure("priority_高", foreground="red")
        self.task_tree.tag_configure("priority_中", foreground="orange")
        self.task_tree.tag_configure("priority_低", foreground="gray")
        
        # 更新统计信息
        self.update_statistics()

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

    def update_statistics(self):
        """更新统计信息"""
        if not self.tasks:
            self.stats_label.config(text="暂无任务")
            return
        
        # 按分类统计
        categories = {}
        for task in self.tasks:
            category = task.get("category", "工作")
            if category not in categories:
                categories[category] = {"total": 0, "completed": 0}
            categories[category]["total"] += 1
            if task["completed"]:
                categories[category]["completed"] += 1
        
        # 生成统计文本
        stats_text = ""
        for category, stats in categories.items():
            completion_rate = (stats["completed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            stats_text += f"{category}: {stats['total']}个任务，完成率{completion_rate:.1f}% | "
        
        self.stats_label.config(text=stats_text[:-3] if stats_text else "暂无任务")

    def generate_test_data(self):
        """生成测试数据"""
        import random
        
        # 测试任务内容
        task_templates = [
            "完成项目报告", "学习新技术", "整理文档", "参加会议", "代码审查",
            "制定计划", "阅读技术文章", "优化代码", "测试功能", "修复bug",
            "写文档", "准备演示", "团队讨论", "客户沟通", "数据分析",
            "系统维护", "备份数据", "更新依赖", "性能优化", "安全检查",
            "买菜做饭", "打扫卫生", "洗衣服", "健身运动", "看电影",
            "读书学习", "写日记", "整理房间", "购买日用品", "联系朋友"
        ]
        
        # 生成选项对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("生成测试数据")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 数量选择
        ttk.Label(dialog, text="生成数量：").pack(pady=5)
        count_var = tk.IntVar(value=10)
        count_spin = ttk.Spinbox(dialog, from_=1, to=50, textvariable=count_var, width=10)
        count_spin.pack(pady=5)
        
        # 是否清空现有数据
        clear_var = tk.BooleanVar(value=False)
        clear_check = ttk.Checkbutton(dialog, text="清空现有数据", variable=clear_var)
        clear_check.pack(pady=10)
        
        def generate():
            count = count_var.get()
            if clear_var.get():
                self.tasks = []
            
            # 生成随机任务
            categories = ["工作", "学习", "生活"]
            priorities = ["高", "中", "低"]
            
            for _ in range(count):
                task = {
                    "content": random.choice(task_templates),
                    "completed": random.choice([True, False]),
                    "category": random.choice(categories),
                    "priority": random.choice(priorities)
                }
                self.tasks.append(task)
            
            self.save_tasks()
            self.refresh_task_list()
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        # 按钮
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="生成", command=generate).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=cancel).pack(side=tk.LEFT, padx=5)

    def on_search_change(self, *args):
        """搜索内容变化时的处理"""
        self.refresh_task_list()

    def on_sort_change(self, *args):
        """排序选项变化时的处理"""
        self.refresh_task_list()


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()