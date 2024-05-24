import os
import zipfile
import json
import shutil

# # 指定 zip 文件所在目录
# zip_dir = 'path/to/zip/files'

# # 指定新建的 token 文件目录
# token_dir = 'path/to/new/token/directory'

# 指定 zip 文件所在目录
zip_dir = os.path.join(os.getcwd(), '')

# 指定新建的 token 文件目录
token_dir = os.path.join(os.getcwd(), 'token_files')

# 创建新的 token 目录
os.makedirs(token_dir, exist_ok=True)

# 用于存储所有 token.json 数据
all_tokens = []

# 遍历 zip 目录下的所有文件
for filename in os.listdir(zip_dir):
    if filename.endswith('.zip'):
        # 打开 zip 文件
        with zipfile.ZipFile(os.path.join(zip_dir, filename), 'r') as zip_ref:
            # 检查 zip 文件中是否包含 token.json 文件
            if 'Documents/token.json' in zip_ref.namelist():
                # 提取 token.json 文件到临时目录
                zip_ref.extract('Documents/token.json', path=token_dir)
                # 读取 token.json 文件的内容
                with open(os.path.join(token_dir, 'Documents', 'token.json'), 'r') as temp_file:
                    token_data = json.load(temp_file)
                # 将 zip 文件名添加到 token 数据中
                token_data['source_file'] = filename
                # 将更新后的 token 数据添加到列表中
                all_tokens.append(token_data)
                # 删除临时文件
                os.remove(os.path.join(token_dir, 'Documents', 'token.json'))

# 将所有 token 数据写入到新的 token.json 文件中
with open(os.path.join(token_dir, 'token.json'), 'w') as token_file:
    json.dump(all_tokens, token_file, indent=4)

print('提取完成!')
