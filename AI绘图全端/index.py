import json
import random
import string

DB_FILE = r"D:\JetBrains\Toolbox\PyCharm Community\pythonproject\AI绘图网站\pythonProject1\文档\user_data.json"
def get_balance_for_key(provided_key):
    data = load_data()
    for _, user_data in data.items():
        if user_data.get('key') == provided_key:
            balance = user_data.get('balance', 0)
            try:
                return int(balance) > 0
            except ValueError:
                return False
    return False
def check_key(provided_key):
    data = load_data()
    for _, user_data in data.items():
        if user_data.get('key') == provided_key:
            return True
    return False
def decrement_balance(expected_key):
    data = load_data()
    for username, user_data in data.items():
        if user_data["key"] == expected_key:
            # 尝试将 balance 转换为整数
            try:
                balance = int(user_data.get("balance", 0))
                if balance > 0:
                    user_data["balance"] = str(balance - 1)
                    save_data(data)
                    return True
                else:
                    return False
            except ValueError:
                return False
    return False
def generate_key():
    letters_and_digits = string.ascii_letters + string.digits
    key = ''.join(random.choice(letters_and_digits) for _ in range(12))
    return key

def generate_unique_user_id():
    try:
        with open(DB_FILE, "r") as file:
            data = json.load(file)
            usernames = data.keys()
            if not usernames:
                return 100000000
            max_id = max(int(username) for username in usernames if username.isdigit())
            return max_id + 1
    except (FileNotFoundError, json.JSONDecodeError):
        return 100000000

def load_data():
    try:
        with open(DB_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
def check_nickname_exists(nickname):
    data = load_data()
    print(data)
    for username, user_data in data.items():
        print(username)
        print(user_data)
        if user_data["nickname"] == nickname:
            return True
    return False
def save_data(data):
    with open(DB_FILE, "w") as file:
        json.dump(data, file)
def check_nickname_password(nickname, password):
    data = load_data()
    print(f"Checking nickname: {nickname}, password: {password}")
    for username, user_data in data.items():
        if user_data["nickname"] == nickname and user_data["password"] == password:
            return True
    return False


def add_user(username, password, nickname, key, balance=100):
    data = load_data()
    if username not in data:
        data[username] = {
            "password": password,
            "nickname": nickname,
            "key": key,
            "balance": balance
        }
        save_data(data)
        return True
    else:
        return False

def check_user(username, password):
    data = load_data()
    if username in data and data[username]["password"] == password:
        return True
    else:
        return False

# # 生成一些虚拟用户数据
# usernames = ["user1", "user2", "user3"]
# passwords = ["pass1", "pass2", "pass3"]
# nicknames = ["nick1", "nick2", "nick3"]
#
# for i in range(len(usernames)):
#     username = str(generate_unique_user_id())
#     password = passwords[i]
#     nickname = nicknames[i]
#     key = generate_key()
#     add_user(username, password, nickname, key)
#
# # 读取并打印数据
# data = load_data()
# print(json.dumps(data, indent=4))
# expected_key = 'KNabz2tGlPNF'
# decrement_balance(expected_key)
# data = load_data()
# print(json.dumps(data, indent=4))