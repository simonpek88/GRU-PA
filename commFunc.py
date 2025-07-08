# coding utf-8
import base64
import importlib.metadata
import logging
import os
import sys
import time
from hashlib import md5

from Crypto import Random
from Crypto.Cipher import AES
from pybadges import badge

from mysql_pool import get_connection

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
    for root, dirs, files in os.walk("./"):
        # 当遍历到根目录时
        if root == "./":
            for file in files:
                # 判断文件后缀是否为.py且文件名不以"test-"开头
                if os.path.splitext(file)[1].lower() == '.py' and not os.path.splitext(file)[0].lower().startswith("test-"):
                    # 获取文件的完整路径
                    pathIn = os.path.join(root, file)
                    # 获取文件名（不含后缀）
                    pyFile = os.path.splitext(file)[0]
                    # 获取文件的最后修改时间（时间戳）
                    file_mtime = int(os.path.getmtime(pathIn))
                    # 构造SQL查询语句，从verinfo表中查询当前文件的信息
                    sql = f"SELECT ID, pyLM from verinfo where pyFile = '{pyFile}'"
                    # 执行SQL查询语句
                    rows = execute_sql(cur2, sql)
                    # 如果查询结果为空，表示该文件在verinfo表中没有记录
                    if not rows:
                        # 构造SQL插入语句，将文件信息插入到verinfo表中
                        sql = f"INSERT INTO verinfo(pyFile, pyLM, pyMC) VALUES('{pyFile}', {int(time.time())}, 1)"
                        # 执行SQL插入语句并提交事务
                        execute_sql_and_commit(conn2, cur2, sql)
                    # 如果查询结果不为空，但文件的最后修改时间与verinfo表中记录的时间不一致
                    elif rows[0][1] != file_mtime:
                        # 构造SQL更新语句，更新verinfo表中该文件的信息
                        sql = f"UPDATE verinfo SET pyLM = {file_mtime}, pyMC = pyMC + 1 where pyFile = '{pyFile}'"
                        # 执行SQL更新语句并提交事务
                        execute_sql_and_commit(conn2, cur2, sql)


def getVerInfo():
    try:
        # 查询pyMC字段总和
        sql = "SELECT SUM(pyMC) FROM verinfo"
        result = execute_sql(cur2, sql)
        verinfo = result[0][0] if result else 0

        # 查询pyLM字段最大值
        sql = "SELECT MAX(pyLM) FROM verinfo"
        result = execute_sql(cur2, sql)
        verLM = result[0][0] if result else 0

        # 查询特定文件记录的pyLM * pyMC总和以及pyMC总和
        sql = "SELECT SUM(pyLM * pyMC), SUM(pyMC) FROM verinfo WHERE pyFile = %s"
        tmpTable = execute_sql(cur2, sql, ('thumbs-up-stars',))

        return verinfo, verLM
    except Exception as e:
        print(f"Database error: {str(e)}")

        return 0, 0


def get_update_content(file_path):
    update_type, update_content = '', ''
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    file.close()
    flag_proc = False
    # 读取文件前30行，查找版本更新信息
    for line in lines[:30]:
        if line.startswith("### 版本"):
            flag_proc = True
        if flag_proc:
            # 提取更新类型
            if line.startswith("- "):
                update_type = line[2:-1]
            # 提取具体更新内容
            elif line.startswith("  - "):
                update_content = line[4:]
                break

    return update_type, update_content


def gen_badge(badge_text_pack, db_type='MySQL'):
    badge_folder = './Images/badges'
    badge_ver_color = 'blue'

    # 获取python版本
    with open(f'{badge_folder}/Python-badge.svg', 'w') as f:
        f.write(badge(left_text='Python', right_text=sys.version[:sys.version.find('(')].strip()))

    if db_type == 'MySQL':
        # 执行查询以获取MySQL版本
        cur2.execute("SELECT VERSION()")
        # 获取查询结果
        db_ver = cur2.fetchone()[0]
    elif db_type == 'sqlite3':
        # 执行查询以获取 SQLite 版本号
        cur2.execute("SELECT sqlite_version()")
        # 获取查询结果
        db_ver = cur2.fetchone()[0]
    else:
        db_ver = 'unknown'
    with open(f'{badge_folder}/{db_type}-badge.svg', 'w') as f:
        f.write(badge(left_text=db_type, right_text=db_ver))

    # 获取指定package的版本号
    for package in badge_text_pack:
        package_version = importlib.metadata.version(package)

        with open(f'{badge_folder}/{package}-badge.svg', 'w') as f:
            if package == 'streamlit_antd_components':
                package = 'Ant Comp'
            f.write(badge(left_text=package, right_text=package_version))


conn2 = get_connection()
cur2 = conn2.cursor()
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
