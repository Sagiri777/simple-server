import os
import base64
import subprocess
from datetime import datetime
import sys
from flask import Flask, request
import requests
import socket
import ast

app = Flask(__name__)

# GitHub 相关配置
github_repo_owner = 'Sagiri777'  # 替换为你的 GitHub 用户名
github_repo_name = 'simple-server'  # 替换为你的 GitHub 仓库名

# 从 secrets 中加载 GitHub personal access token
github_token = os.getenv('GH_TOKEN')

# 获取当前时间戳，用于文件名
current_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

# 设置 util_results 文件夹路径
results_folder = 'util_results'

# 如果文件夹不存在，创建它
if not os.path.exists(results_folder):
    os.makedirs(results_folder)

app = Flask(__name__)

# 获取本机IP地址
ip_address = socket.gethostbyname(socket.gethostname())

# 为Flask指定实际端口
port = 5000

# 读取1.py文件内容
with open('1.py', 'r') as script_file:
    script_content = script_file.read()

# 提取导入的库及注释信息
imported_libraries = {}

def extract_libraries(script_content):
    tree = ast.parse(script_content)

    current_module = None

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_libraries[alias.name] = get_library_info(alias, node)
        elif isinstance(node, ast.ImportFrom):
            current_module = node.module
            for alias in node.names:
                imported_libraries[alias.name] = get_library_info(alias)
        elif isinstance(node, ast.Assign) and current_module:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    imported_libraries[target.id] = {'name': current_module}

def get_library_info(alias_or_module):
    library_info = {'name': None, 'version': None}
    if alias_or_module.name.startswith('# '):
        comments = alias_or_module.name[2:].split(',')
        for comment in comments:
            parts = comment.strip().split('-')
            if parts[0] == 'name' and len(parts) > 1:
                library_info['name'] = parts[1].strip()
            elif parts[0] == 'version' and len(parts) > 1:
                library_info['version'] = parts[1].strip()
    else:
        library_info['name'] = alias_or_module.name
    
    return library_info

# 提取导入的库及注释信息
extract_libraries(script_content)

# 安装缺失的库
for name, info in imported_libraries.items():
    version = f'=={info["version"]}' if info.get("version") else ''
    try:
        library_name = info.get("name") or name
        subprocess.check_output(['pip', 'install', '--upgrade', f'{library_name}{version}'], text=True, stderr=subprocess.STDOUT)
        print(f'成功安装/升级库: {library_name}{version}')
    except subprocess.CalledProcessError as e:
        print(f'安装/升级库时出错：\n{e.output}')

# 设置变量，用于判断是否执行额外的脚本
run_extra_script = 1  # 设置为1时执行，设置为其他值时不执行

if run_extra_script == 1:
    try:
        result = subprocess.check_output(['python3', '1.py'], text=True, stderr=subprocess.STDOUT)
        print(f'执行 1.py 结果：\n{result}')
    except subprocess.CalledProcessError as e:
        print(f'执行 1.py 出错：\n{e.output}')
    
    sys.exit()  # 执行完 1.py 后自动退出程序

print(f'喵~服务器IP地址是：{ip_address}，程序运行端口是：{port}')
# 遍历 util_results 文件夹中的文件并上传到 GitHub
def upload_results_to_github():
    for filename in os.listdir(results_folder):
        file_path = os.path.join(results_folder, filename)

        # 上传文件到 GitHub
        upload_url = f'https://api.github.com/repos/{github_repo_owner}/{github_repo_name}/contents/util_results/{filename}'
        with open(file_path, 'r') as file_content:
            content_base64 = base64.b64encode(file_content.read().encode()).decode()

        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json',
        }
        payload = {
            'message': f'Upload {filename}',
            'content': content_base64,
        }
        response = requests.put(upload_url, headers=headers, json=payload)

        if response.status_code == 200:
            print(f'文件 {filename} 上传成功！')
        else:
            print(f'文件 {filename} 上传失败，状态码：{response.status_code}')
upload_results_to_github()

# ... （以下为原有的路由和处理逻辑）

# ... （以下为原有的路由和处理逻辑）

# ... （以下为原有的路由和处理逻辑）
@app.route('/')
def home():
    return '欢迎来到喵~服务器'

@app.route('/command', methods=['POST'])
def receive_command():
    data = request.get_json()
    command = data.get('cmd')

    if command.startswith("py"):
        script_base64 = command[2:]
        decoded_script = base64.b64decode(script_base64).decode('utf-8')

        try:
            result = subprocess.check_output(['python3', '-c', decoded_script], text=True, stderr=subprocess.STDOUT)
            return f'执行结果：\n{result}'
        except subprocess.CalledProcessError as e:
            return f'执行错误：\n{e.output}'

    elif command.startswith("ip"):
        url = command[2:]
        try:
            response = requests.get(url)
            return f'对方服务器IP：{response.text}'
        except requests.RequestException as e:
            return f'获取对方服务器IP时出错：{str(e)}'

    else:
        try:
            result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
            return f'执行结果：\n{result}'
        except subprocess.CalledProcessError as e:
            return f'执行错误：\n{e.output}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
