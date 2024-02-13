import os
import base64
import subprocess
import ast
import requests
from datetime import datetime

# 获取当前时间戳，用于文件名
current_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

# 设置 util_results 文件夹路径
results_folder = 'util_results'

# 如果文件夹不存在，创建它
if not os.path.exists(results_folder):
    os.makedirs(results_folder)

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

# 提取导入的库及注释信息
def extract_libraries_with_comments(script_content):
    tree = ast.parse(script_content)

    imported_libraries = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_libraries[alias.name] = {'name': None, 'version': None}

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_libraries[node.module] = {'name': None, 'version': None}

        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
            comment = node.value.s.strip()
            if comment.startswith('#name-') or comment.startswith('#version-'):
                lib_name, lib_version = extract_comment_info(comment[1:])
                if lib_name in imported_libraries:
                    imported_libraries[lib_name]['name'] = lib_name
                    imported_libraries[lib_name]['version'] = lib_version

    return imported_libraries

# 提取注释中的库信息
def extract_comment_info(comment):
    # 从注释中提取类似于 "name-xxx" 或 "version-xxx" 的信息
    parts = comment.split('-')
    return parts[0].strip(), parts[1].strip() if len(parts) > 1 else None

# 安装缺失的库
def install_libraries(imported_libraries):
    for name, info in imported_libraries.items():
        version = f'=={info.get("version")}' if info.get("version") else ''
        try:
            library_name = info.get("name") or name
            subprocess.check_output(['pip', 'install', '--upgrade', f'{library_name}{version}'], text=True, stderr=subprocess.STDOUT)
            print(f'成功安装/升级库: {library_name}{version}')
        except subprocess.CalledProcessError as e:
            print(f'安装/升级库时出错：\n{e.output}')

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

# 读取脚本内容
with open('1.py', 'r') as script_file:
    script_content = script_file.read()

# 提取导入的库及注释信息
imported_libraries = extract_libraries_with_comments(script_content)

# 安装缺失的库
install_libraries(imported_libraries)

# 示例使用：执行 1.py
try:
    result = subprocess.check_output(['python3', '1.py'], text=True, stderr=subprocess.STDOUT)
    print(f'执行 1.py 结果：\n{result}')
except subprocess.CalledProcessError as e:
    print(f'执行 1.py 时出错：\n{e.output}')

# 上传结果到 GitHub
upload_results_to_github()
