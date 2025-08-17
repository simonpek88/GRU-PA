# coding utf-8
import hashlib
import json
import os
import threading
import time

# cSpell:ignoreRegExp /[^\s]{16,}/
# cSpell:ignoreRegExp /\b[A-Z]{3,15}\b/g
# cSpell:ignoreRegExp /\b[A-Z]\b/g

# 全局变量
ONLINE_USERS_FILE = "./online_users.json"
user_lock = threading.Lock()

def get_online_count(user_identifier=None):
    """
    获取当前在线人数

    Args:
        user_identifier (str, optional): 用户标识符，可以是:
            - 用户ID
            - Session ID
            - IP地址
            - 或其他唯一标识符
            如果未提供，则使用更稳定的标识方法

    Returns:
        int: 当前在线人数
    """
    with user_lock:
        users = _load_online_users()
        current_time = time.time()

        # 清除超过5分钟未活动的用户
        users = {user_id: last_active for user_id, last_active in users.items() 
                 if current_time - last_active < 300}

        # 添加或更新当前用户
        user_id = _get_current_user_id(user_identifier)
        users[user_id] = current_time

        _save_online_users(users)
        return len(users)

def _load_online_users():
    """加载在线用户数据"""
    if os.path.exists(ONLINE_USERS_FILE):
        try:
            with open(ONLINE_USERS_FILE, 'r') as f:
                data = json.load(f)
                # 确保返回的是字典类型
                if isinstance(data, dict):
                    return data
                else:
                    return {}
        except (json.JSONDecodeError, IOError, TypeError):
            return {}
    return {}

def _save_online_users(users_data):
    """保存在线用户数据"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(ONLINE_USERS_FILE) if os.path.dirname(ONLINE_USERS_FILE) else '.', exist_ok=True)
        with open(ONLINE_USERS_FILE, 'w') as f:
            json.dump(users_data, f, indent=2)
    except IOError:
        pass

def _get_current_user_id(user_identifier=None):
    """
    获取当前用户ID

    Args:
        user_identifier (str, optional): 用户标识符

    Returns:
        str: 用户唯一标识符
    """
    # 如果提供了用户标识符，直接使用
    if user_identifier:
        return str(user_identifier)

    # 尝试从环境变量获取
    remote_addr = os.environ.get('REMOTE_ADDR', '')
    user_agent = os.environ.get('HTTP_USER_AGENT', '')

    # 如果能获取到IP地址，则基于IP生成稳定的标识符
    if remote_addr:
        # 只使用IP地址生成标识符，忽略User-Agent以增加稳定性
        return hashlib.md5(remote_addr.encode('utf-8')).hexdigest()

    # 如果在本地运行或者无法获取IP，使用主机名和进程ID
    try:
        import socket
        hostname = socket.gethostname()
        pid = os.getpid()
        identifier_string = f"{hostname}:{pid}"
        return hashlib.md5(identifier_string.encode('utf-8')).hexdigest()
    except:
        # 最后fallback到使用时间戳
        return str(time.time())

# 添加一个调试函数，用于查看当前在线用户
def debug_online_users():
    """
    调试函数：查看当前在线用户

    Returns:
        dict: 当前在线用户信息
    """
    with user_lock:
        users = _load_online_users()
        current_time = time.time()

        # 显示所有用户和他们的最后活动时间
        active_users = {}
        for user_id, last_active in users.items():
            time_diff = current_time - last_active
            active_users[user_id] = {
                "last_active": last_active,
                "time_ago": f"{time_diff:.1f}秒前",
                "is_active": time_diff < 300
            }

        return {
            "total_users": len(users),
            "active_users": len([u for u, t in users.items() if current_time - t < 300]),
            "users_detail": active_users
        }

if __name__ == "__main__":
    # 测试时使用固定标识符
    print("当前在线人数:", get_online_count("test_user"))
    print("\n详细信息:")
    result = debug_online_users()
    import json as json_module
    print(json_module.dumps(result, indent=2, ensure_ascii=False))
