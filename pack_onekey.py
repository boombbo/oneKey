# pack_onekey.py
from PyInstaller.__main__ import run

if __name__ == '__main__':
    opts = [
        'oneKey.py',  # 主程序文件
        '--add-data=data_directory;data_directory',  # 添加 data_directory 目录
        '--add-data=data;data',  # 添加 data 目录
        '--add-data=ClearBrowsingHistory.bat;.',  # 添加 ClearBrowsingHistory.bat 文件
        '--add-data=ClearBrowsingHistory.ps1;.',  # 添加 ClearBrowsingHistory.ps1 文件
        '--noconsole',  # 不显示控制台窗口
        '--onefile',  # 打包成一个文件
    ]

    run(opts)
