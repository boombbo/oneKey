# ClearBrowsingHistory.ps1

# 路径可能因用户和Chrome的安装目录不同而不同
$chromeDataPath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default"
$historyDB = "$chromeDataPath\History"

# 使用SQLite命令行工具执行SQL命令
# 这里假设sqlite3.exe位于C:\path\to\sqlite3.exe
#& "C:\Users\All Users\miniconda3\Library\bin\sqlite3.exe" $historyDB "DELETE FROM urls; DELETE FROM visits;"
