使用方法（超级简单）

先运行一次打开 Edge（只开一次就行）：

cmd"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="C:\edge-temp"

打开脚本，修改这一行：

PythonOFFSET = 0     # 改成 0、20、40、60、100... 你想继续的那一页

运行脚本 → 只会爬你指定的这一页 → 自动保存两个文件：
offset_0.xlsx、offset_20.xlsx ...
【总表】reuters_hegseth_all.xlsx（自动合并+去重）