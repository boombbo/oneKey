import tkinter as tk
from threading import Thread
from tkinter import Label, Entry, Button, Spinbox, messagebox, simpledialog
from queue import Queue
import subprocess
import logging
import os
import re
import json

# 配置日志
logging.basicConfig(filename='process_words_log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

class ChromeManager:
    def __init__(self, chrome_path, max_concurrent=5):
        self.chrome_path = chrome_path
        self.max_concurrent = max_concurrent
        self.queue = Queue(maxsize=max_concurrent)
        self.processes = []

    def open_chrome_with_url(self, url, profiles):
        threads = []
        for profile in profiles:
            thread = Thread(target=self._threaded_open, args=(url, profile))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

    def close_all_processes(self):
        for process in self.processes:
            if process.poll() is None:  # 如果进程仍在运行
                process.terminate()     # 尝试终止进程
            process.wait()             # 等待进程结束

    def _threaded_open(self, url, profile):
        self.queue.put(profile)
        process = self.open_chrome(url, profile)
        if process:
            self.processes.append(process)
        self.queue.get()
        self.queue.task_done()

    def open_chrome(self, url, profile):
    # 构建 Chrome 启动命令，其中包括指定的配置文件目录
        command = f'"{self.chrome_path}" --profile-directory="{profile}" {url}'
        try:
            # 配置 subprocess 以不显示终端窗口
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE  # 隐藏控制台窗口

            process = subprocess.Popen(command, shell=True, startupinfo=startupinfo)
            logging.info(f"开启Chrome配置文件 {profile}")
            return process
        except Exception as e:
            logging.error(f"开启Chrome配置文件 {profile}: {e}时出错")
            self.queue.get()          # 确保即使发生异常也要从队列中移除
            self.queue.task_done()
            return None

    def close_and_clear_chrome(self):
        try:
            subprocess.run(["taskkill", "/IM", "chrome.exe", "/F"], check=True)
            subprocess.run(["PowerShell.exe", "-ExecutionPolicy", "Bypass", "-File", "ClearBrowsingHistory.ps1"], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror('错误', '无法关闭Chrome或清除历史记录.')
        except FileNotFoundError:
            messagebox.showerror('错误', '文件未找到.')
        else:
            messagebox.showinfo('成功', '成功清除Chrome历史记录')

def setup_ui(chrome_manager):
    window = tk.Tk()
    window.title("Chrome Profile Opener")

    data_directory = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    preset_file = os.path.join(data_directory, 'presets.json')
    presets = []
    if os.path.exists(preset_file):
        with open(preset_file, 'r') as file:
            presets = json.load(file)

       # 与链接预设相同的数据目录
    data_directory = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    # 用户预设文件
    user_preset_file = os.path.join(data_directory, 'user_presets.json')
    user_presets = []
    if os.path.exists(user_preset_file):
        with open(user_preset_file, 'r') as file:
            user_presets = json.load(file)

    # 更新用户预设的 JSON 文件
    def update_user_presets_json():
        with open(user_preset_file, 'w') as file:
            json.dump(user_presets, file)

    # 添加用户预设
    def add_user_preset():
        profile_name = simpledialog.askstring("添加用户配置文件预设", "Enter the profile name:")
        if profile_name:
            if profile_name not in user_presets:
                user_presets.append(profile_name)
                update_user_presets_json()
                messagebox.showinfo("成功", "配置文件添加到预设中.")
            else:
                messagebox.showerror("错误", "此配置文件已经存在于预设中.")

    # 选择用户预设
    def choose_user_preset():
        preset_window = tk.Toplevel(window)
        preset_window.title("选择一个用户预设")
        preset_var = tk.StringVar(preset_window)
        preset_var.set(user_presets[0] if user_presets else "")
        for profile_name in user_presets:
            tk.Radiobutton(preset_window, text=profile_name, variable=preset_var, value=profile_name).pack()
        tk.Button(preset_window, text="选择", command=lambda: set_custom_profile_from_preset(preset_var.get(), preset_window)).pack()
        tk.Button(preset_window, text="删除选定预设", command=lambda: delete_selected_user_preset(preset_var)).pack()
        tk.Button(preset_window, text="删除所有预设", command=delete_all_user_presets).pack()

    # 设置自定义配置文件名从预设
    def set_custom_profile_from_preset(profile_name, window):
        custom_profile_entry.delete(0, tk.END)
        custom_profile_entry.insert(0, profile_name)
        window.destroy()

    # 删除选定的用户预设
    def delete_selected_user_preset(preset_var):
        selected_profile = preset_var.get()
        if selected_profile in user_presets:
            user_presets.remove(selected_profile)
            update_user_presets_json()
            messagebox.showinfo("成功", "删除预设配置文件: " + selected_profile)

    # 删除所有用户预设
    def delete_all_user_presets():
        user_presets.clear()
        update_user_presets_json()
        messagebox.showinfo("成功", "所有预设配置文件已被删除.")

    # 用户预设相关的 UI 按钮
    Button(window, text="添加用户配置文件预设", command=add_user_preset).pack()
    Button(window, text="选择用户配置文件预设", command=choose_user_preset).pack()

    def update_presets_json():
        with open(preset_file, 'w') as file:
            json.dump(presets, file)

    Label(window, text="输入URL:").pack()
    url_entry = Entry(window, width=50)
    url_entry.pack()

    Label(window, text="要打开的页面数:").pack()
    num_profiles = Spinbox(window, from_=1, to=100)
    num_profiles.pack()

    Label(window, text="输入自定义配置文件名 (逗号分隔):").pack()
    Label(window, text="示例输入格式: profile1, profile12, profile22").pack()
    custom_profile_entry = Entry(window, width=50)
    custom_profile_entry.pack()

    def open_fixed_number_of_profiles():
        url = url_entry.get()
        num = int(num_profiles.get())
        profiles = [f'Profile {i}' for i in range(1, num + 1)]
        chrome_manager.open_chrome_with_url(url, profiles)

    def open_custom_profiles():
        url = url_entry.get()
        custom_profiles = custom_profile_entry.get().split(',')
        custom_profiles = [profile.strip() for profile in custom_profiles if profile.strip()]
        if url and custom_profiles:
            chrome_manager.open_chrome_with_url(url, custom_profiles)
        else:
            messagebox.showerror("错误", "请输入有效的URL和至少一个配置文件名.")

    Button(window, text="打开指定数量的配置页面", command=open_fixed_number_of_profiles).pack()
    Button(window, text="打开自定义账户的配置页面", command=open_custom_profiles).pack()

    def save_preset(url):
        if re.match(r'^https?:\\/\\/\\S+\\.\\S+$', url):
            if url not in presets:
                presets.append(url)
                update_presets_json()
                messagebox.showinfo("成功", "URL添加到预设.")
            else:
                messagebox.showerror("错误", "此URL已经存在于预设中.")
        else:
            messagebox.showerror("错误", "无效的URL格式. 请重新输入.")

    def add_preset():
        url = simpledialog.askstring("添加预设网站链接", "Enter the website URL:")
        if url:
            save_preset(url)

    def delete_selected_preset(preset_var):
        selected_url = preset_var.get()
        if selected_url in presets:
            presets.remove(selected_url)
            update_presets_json()
            messagebox.showinfo("成功", "删除预设URL: " + selected_url)

    def delete_all_presets():
        presets.clear()
        update_presets_json()
        messagebox.showinfo("成功", "所有预设URL已被删除.")

    def choose_preset():
        preset_window = tk.Toplevel(window)
        preset_window.title("选择一个预设")
        preset_var = tk.StringVar(preset_window)
        preset_var.set(presets[0] if presets else "")
        for url in presets:
            tk.Radiobutton(preset_window, text=url, variable=preset_var, value=url).pack()
        tk.Button(preset_window, text="选择", command=lambda: set_url_from_preset(preset_var.get(), preset_window)).pack()
        tk.Button(preset_window, text="删除选定链接", command=lambda: delete_selected_preset(preset_var)).pack()
        tk.Button(preset_window, text="删除所有链接", command=delete_all_presets).pack()

    def set_url_from_preset(url, window):
        url_entry.delete(0, tk.END)
        url_entry.insert(0, url)
        window.destroy()

    Button(window, text="添加预设链接", command=add_preset).pack()
    Button(window, text="选择预设连接", command=choose_preset).pack()
    Button(window, text="关闭并清理Chrome", command=chrome_manager.close_and_clear_chrome).pack()

    def on_close():
        chrome_manager.close_all_processes()  # 关闭所有子进程
        window.destroy()                      # 销毁窗口

    window.protocol("WM_DELETE_WINDOW", on_close)

    window.mainloop()

if __name__ == "__main__":
    chrome_path = "C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe"
    chrome_manager = ChromeManager(chrome_path)
    setup_ui(chrome_manager)

