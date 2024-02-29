import tkinter as tk
from threading import Thread
from tkinter import Label, Entry, Button, Spinbox, messagebox
from queue import Queue
import subprocess
import logging
import os
import re
import json
from tkinter import simpledialog


# Configure logging
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

    def _threaded_open(self, url, profile):
        self.queue.put(profile)
        process = self.open_chrome(url, profile)
        if process:
            self.processes.append(process)
        self.queue.get()
        self.queue.task_done()

    def open_chrome(self, url, profile):
        # 移除了 --incognito 参数以避免无痕模式
        command = f'"{self.chrome_path}" --profile-directory="{profile}" {url}'
        try:
            process = subprocess.Popen(command, shell=True)
            logging.info(f"Opened Chrome with profile {profile}")
            return process
        except Exception as e:
            logging.error(f"Error opening Chrome with profile {profile}: {e}")
            return None


    def close_and_clear_chrome(self):
        try:
            subprocess.run(["taskkill", "/IM", "chrome.exe", "/F"], check=True)
            subprocess.run(["PowerShell.exe", "-ExecutionPolicy", "Bypass",
                           "-File", "ClearBrowsingHistory.ps1"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while killing Chrome or clearing history: {e}")
            messagebox.showerror('Error', 'Failed to close Chrome or clear history.')
        except FileNotFoundError as e:
            print(f"An error occurred: File not found. {e}")
            messagebox.showerror('Error', 'File not found.')
        else:
            messagebox.showinfo('Success', 'Chrome history cleared successfully')
        finally:
            print("This block is always executed, can be used for cleanup.")



def execute_mul_processor(url, num_profiles, chrome_manager):
    profiles = [f'Profile {i}' for i in range(1, num_profiles + 1)]
    chrome_manager.open_chrome_with_url(url, profiles)
    

def setup_ui(chrome_manager):
    window = tk.Tk()
    window.title("Chrome Profile Opener")

    Label(window, text="Enter URL:").pack()
    url_entry = Entry(window, width=50)
    url_entry.pack()

    Label(window, text="需要打开的页面数量:").pack()
    num_profiles = Spinbox(window, from_=1, to=100)
    num_profiles.pack()

    open_button = Button(window, text="确认打开", command=lambda: execute_mul_processor(url_entry.get(), int(num_profiles.get()), chrome_manager))
    open_button.pack()
    
    data_directory = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    # 加载预设值
    preset_file = os.path.join(data_directory, 'presets.json')
    if os.path.exists(preset_file):
        with open(preset_file, 'r') as file:
            presets = json.load(file)
    else:
        presets = []

    def save_preset(url):
        if re.match(r'^https?:\/\/\S+\.\S+$', url):
            presets.append(url)
            with open(preset_file, 'w') as file:
                json.dump(presets, file)
        else:
            messagebox.showerror("Error", "Invalid URL format. Please re-enter.")

    def add_preset():
        url = simpledialog.askstring("添加预设网站链接", "Enter the website URL:")
        if url:
            save_preset(url)

    def choose_preset():
        preset_window = tk.Toplevel(window)
        preset_window.title("选择一个预设")
        
        def set_url_from_preset():
            chosen_url = preset_var.get()
            url_entry.delete(0, tk.END)
            url_entry.insert(0, chosen_url)
            preset_window.destroy()

        preset_var = tk.StringVar(preset_window)
        preset_var.set(presets[0] if presets else "")
        
        for url in presets:
            tk.Radiobutton(preset_window, text=url, variable=preset_var, value=url).pack()

        tk.Button(preset_window, text="选择", command=set_url_from_preset).pack()

    preset_button = tk.Button(window, text="添加预设链接", command=add_preset)
    preset_button.pack()

    choose_preset_button = tk.Button(window, text="选择预设连接", command=choose_preset)
    choose_preset_button.pack()

    def on_close_and_clear_click():
        chrome_manager.close_and_clear_chrome()

    close_and_clear_button = tk.Button(window, text="关闭", command=on_close_and_clear_click)
    close_and_clear_button.pack()

    window.mainloop()

if __name__ == "__main__":
    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    chrome_manager = ChromeManager(chrome_path)
    setup_ui(chrome_manager)  # 传递 chrome_manager 实例