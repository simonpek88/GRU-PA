# coding utf-8
import base64
import json
import logging
import os
import time
from hashlib import md5

import jwt
import requests
from Crypto import Random
from Crypto.Cipher import AES
from mysql_pool_cpython import get_connection  # type: ignore
from openai import OpenAI

# cSpell:ignoreRegExp /[^\s]{16,}/
# cSpell:ignoreRegExp /\b[A-Z]{3,15}\b/g
# cSpell:ignoreRegExp /\b[A-Z]\b/g

def pad(data):
    # 计算需要填充的字节数
    length = 16 - (len(data) % 16)

    # 将数据编码为utf-8格式
    # 并将填充字符（长度为length）重复length次后编码为utf-8格式
    # 最后将编码后的数据和填充数据拼接返回
    return data.encode(encoding="utf-8") + (chr(length) * length).encode(encoding="utf-8")


def unpad(data):
    # 判断data的最后一个元素是否为整数
    # 如果是整数，则直接作为填充长度
    # 如果不是整数，则通过ord函数获取其ASCII码值作为填充长度
    return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]


def bytes_to_key(data, salt, output=48):
    # 将输入数据编码为utf-8格式
    data = data.encode(encoding="utf-8")
    # 断言盐的长度为8
    assert len(salt) == 8, len(salt)
    # 将盐附加到数据后面
    data += salt
    # 使用MD5算法对数据进行哈希处理，并获取哈希值的二进制表示
    key = md5(data).digest()
    final_key = key
    # 当生成的密钥长度小于指定输出长度时，继续生成密钥
    while len(final_key) < output:
        # 使用MD5算法对密钥和数据再次进行哈希处理，并获取哈希值的二进制表示
        key = md5(key + data).digest()
        # 将新生成的密钥附加到最终密钥后面
        final_key += key

    # 返回指定长度的最终密钥
    return final_key[:output]


def encrypt(message, passphrase):
    # 生成一个随机的8个字节的盐
    salt = Random.new().read(8)

    # 使用bytes_to_key函数生成密钥和IV
    key_iv = bytes_to_key(passphrase, salt, 32 + 16)

    # 分离密钥和IV
    key = key_iv[:32]
    iv = key_iv[32:]

    # 创建一个AES对象，使用CBC模式
    aes = AES.new(key, AES.MODE_CBC, iv)

    # 对消息进行加密，并在加密前添加"Salted__"前缀和盐
    # 加密后，使用base64编码返回结果
    return base64.b64encode(b"Salted__" + salt + aes.encrypt(pad(message)))


def decrypt(encrypted, passphrase):
    # 对加密数据进行base64解码
    encrypted = base64.b64decode(encrypted)

    # 判断加密数据前8个字节是否为"Salted__"
    assert encrypted[0:8] == b"Salted__"

    # 提取盐值，盐值位于"Salted__"之后，长度为8个字节
    salt = encrypted[8:16]

    # 使用bytes_to_key函数生成密钥和IV
    key_iv = bytes_to_key(passphrase, salt, 32 + 16)

    # 分离密钥和IV
    key = key_iv[:32]
    iv = key_iv[32:]

    # 创建一个AES对象，使用CBC模式
    aes = AES.new(key, AES.MODE_CBC, iv)

    # 对加密数据进行解密，并去除前16个字节（包括"Salted__"和盐值）
    # 然后对解密后的数据进行去填充处理
    return unpad(aes.decrypt(encrypted[16:]))


def getEncryptKeys(keyname):
    # 从数据库中查询键名为'key_text'的加密密钥
    sql = "SELECT aikey from aikeys where keyname = 'key_text'"
    # 执行SQL查询并获取结果中的第一个值作为密钥
    key = execute_sql(cur2, sql)[0][0]

    # 构建SQL查询语句，用于查询指定键名的加密数据
    sql = f"SELECT aikey from aikeys where keyname = '{keyname}'"
    # 执行SQL查询并获取结果中的第一个值作为加密数据
    encrypt_data = execute_sql(cur2, sql)[0][0]

    # 使用密钥对加密数据进行解密
    #encrypt_data = encrypt(data, key).decode("utf-8")
    decrypt_data = decrypt(encrypt_data, key).decode("utf-8")

    # 返回解密后的数据
    return decrypt_data


# noinspection GrazieInspection
def getUserEDKeys(userStr, edType):
    # 初始化加密后的字符串为空
    strED = ""
    # 构建SQL查询语句，从数据库中获取密钥
    sql = "SELECT aikey from aikeys where keyname = 'key_text'"
    # 执行SQL查询语句，获取密钥
    key = execute_sql(cur2, sql)[0][0]
    # 判断加密类型是否为"enc"（加密）
    if edType == "enc":
        # 对用户输入字符串进行加密，并将加密后的字符串解码为UTF-8格式
        strED = encrypt(userStr, key).decode("utf-8")
    # 判断加密类型是否为"dec"（解密）
    elif edType == "dec":
        # 对用户输入字符串进行解密，并将解密后的字符串解码为UTF-8格式
        strED = decrypt(userStr, key).decode("utf-8")

    # 返回加密或解密后的字符串
    return strED


# noinspection PyBroadException
def execute_sql(cur, sql, params=None):
    try:
        # 参数化查询以预防SQL注入
        if params:
            cur.execute(sql, params)
        else:
            # 如果sql是外部输入的，请确保它是安全的，或者使用其他方法来避免SQL注入
            cur.execute(sql)
        return cur.fetchall()
    except Exception as e:
        logging.error(f"An error occurred while executing SQL: {sql}, Error: {e}")
        return []


# noinspection PyBroadException
def execute_sql_and_commit(conn, cur, sql, params=None):
    try:
        # 参数化查询以预防SQL注入
        if params:
            cur.execute(sql, params)
        else:
            # 如果sql是外部输入的，请确保它是安全的，或者使用其他方法来避免SQL注入
            cur.execute(sql)
        conn.commit()
        return True
    except Exception as e:
        logging.error(f"An error occurred while executing SQL: {sql}, Error: {e}")
        return False


def updatePyFileinfo():
    ALLOW_FILE_TYPE = {'.py', '.md', '.ps1', '.bat', '.txt', '.sh'}
    ROOT_PATH = "./"

    # 尝试读取现有的JSON文件
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            try:
                file_records = json.load(f)
            except json.JSONDecodeError:
                file_records = {}
    else:
        file_records = {}

    updates = []
    inserts = []

    # 收集需要更新或插入的文件信息
    for root, dirs, files in os.walk(ROOT_PATH):
        if root == ROOT_PATH:
            for file in files:
                file_name, file_ext = os.path.splitext(file)
                # 修正判断逻辑：检查文件名是否以test-开头
                if file_ext.lower() in ALLOW_FILE_TYPE and not file_name.lower().startswith("test-"):
                    pathIn = os.path.join(root, file)
                    file_mtime = int(os.path.getmtime(pathIn))

                    # 检查是否需要更新或插入
                    if file_name not in file_records:
                        inserts.append(file_name)
                        file_records[file_name] = {
                            "pyLM": file_mtime,
                            "pyMC": 1
                        }
                    elif file_records[file_name]["pyLM"] != file_mtime:
                        updates.append(file_name)
                        file_records[file_name]["pyLM"] = file_mtime
                        file_records[file_name]["pyMC"] = file_records[file_name].get("pyMC", 0) + 1

    # 将更新后的数据写入JSON文件
    try:
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(file_records, f, ensure_ascii=False, indent=2)

        if inserts or updates:
            logging.info(f"Updated file info: {len(inserts)} inserts, {len(updates)} updates")
    except Exception as e:
        logging.error(f"Failed to write to JSON file: {e}")


def getVerInfo():
    try:
        # 尝试读取现有的JSON文件
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                try:
                    file_records = json.load(f)
                except json.JSONDecodeError:
                    file_records = {}
        else:
            file_records = {}

        # 计算pyMC字段总和
        verinfo = sum(item["pyMC"] for item in file_records.values())

        # 计算pyLM字段最大值
        verLM = max([item["pyLM"] for item in file_records.values()], default=0)

        return verinfo, verLM
    except Exception as e:
        print(f"File read error: {str(e)}")
        return 0, 0


def get_update_content(file_path):
    update_type, update_content = '', ''
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    file.close()
    flag_proc = False
    # 读取文件前30行，查找版本更新信息
    for line in lines[:100]:
        if line.startswith("- "):
            flag_proc = True
        if flag_proc:
            # 提取更新类型
            if line.startswith("- "):
                update_type = line[2:-1]
            # 提取具体更新内容
            elif line.startswith("  - "):
                update_content = line[4:-1]
                break

    return update_type, update_content


def gen_jwt():
    # Open PEM
    private_key = getEncryptKeys('hf_jwt_key')
    project_id_key = getEncryptKeys('hf_project_id')
    jwt_id_key = getEncryptKeys('hf_jwt_id')

    payload = {
        'iat': int(time.time()) - 30,
        'exp': int(time.time()) + 900,
        'sub': project_id_key
    }
    headers = {
        'kid': jwt_id_key
    }

    # Generate JWT
    encoded_jwt = jwt.encode(payload, private_key, algorithm='EdDSA', headers = headers)
    #print(f"JWT:  {encoded_jwt}")

    return encoded_jwt


def get_deepseek_balance():
    aikey = getEncryptKeys("deepseek")
    url = "https://api.deepseek.com/user/balance"

    payload={}
    headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {aikey}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    info = response.json()
    temp = info['balance_infos'][0]
    #print(f"余额: {temp['total_balance']} {temp['currency']}")

    return info['is_available'], temp['total_balance'], temp['currency']


def deepseek_AI(report_task, useModel='deepseek-chat'):
    # 模型版本可选deepseek-reasoner(R1)和deepseek-chat(V3) 默认V3
    try:
        aikey = getEncryptKeys("deepseek")
        client = OpenAI(api_key=aikey, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model=useModel,
            messages=[
                {
                    "role": "system",
                    "content": "根据我提供的内容请生成一份的周报, 要求书写规范, 用词正式, 输出为Markdown格式"
                },
                {
                    "role": "user",
                    "content": f"{report_task}"
                },
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"An error occurred while calling Deepseek AI: {e}")
        return None


conn2 = get_connection()
cur2 = conn2.cursor()
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

JSON_FILE = "verinfo.json"

if __name__ == '__main__':
    ds_balance = get_deepseek_balance()
    if ds_balance[0]:
        print(f"余额: {ds_balance[1]} {ds_balance[2]}")
    else:
        print("账户: 无效")
