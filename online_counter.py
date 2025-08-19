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

def add_user(user_identifier):
    """
    添加用户到在线列表

    Args:
        user_identifier (str): 用户标识符

    Returns:
        int: 当前在线人数
    """
    if not user_identifier:
        raise ValueError("user_identifier 不能为空")

    with user_lock:
        users = _load_online_users()
        current_time = time.time()

        # 添加用户
        users[str(user_identifier)] = current_time

        _save_online_users(users)
        return len(users)


def remove_user(user_identifier):
    """
    从在线列表中删除用户

    Args:
        user_identifier (str): 用户标识符

    Returns:
        int: 当前在线人数
    """
    if not user_identifier:
        raise ValueError("user_identifier 不能为空")

    with user_lock:
        users = _load_online_users()
        current_time = time.time()

        # 删除超过5分钟未活动的用户（清理过期数据）
        users = {user_id: last_active for user_id, last_active in users.items() 
                 if current_time - last_active < 300}

        # 删除指定用户
        users.pop(str(user_identifier), None)

        _save_online_users(users)
        return len(users)


def get_online_count():
    """
    获取当前在线人数（清理过期用户后）

    Returns:
        int: 当前在线人数
    """
    with user_lock:
        users = _load_online_users()
        current_time = time.time()

        # 清除超过30分钟未活动的用户
        users = {user_id: last_active for user_id, last_active in users.items()
                 if current_time - last_active < 1800}

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
    print("当前在线人数:", get_online_count())
    print("\n详细信息:")
    result = debug_online_users()
    import json as json_module
    print(json_module.dumps(result, indent=2, ensure_ascii=False))
