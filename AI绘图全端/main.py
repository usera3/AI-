import random
import time

import flask
import requests
from flask import request, make_response, jsonify, render_template
from flask_cors import CORS

app = flask.Flask(__name__)
CORS(app)
import index
def upload_image_to_api(image_url):
    response = requests.post("https://mozi102.pythonanywhere.com/upload", json={"image_url": image_url})
    if response.status_code == 200:
        return response.json()["new_url"]
    else:
        return f"请求失败，状态码：{response.status_code}，错误信息：{response.text}"
def modify_balance_for_key(key, new_balance):
    data = index.load_data()
    for username, user_data in data.items():
        if user_data["key"] == key:
            user_data["balance"] = new_balance
            index.save_data(data)
            return True
    return False
def upload_image_to_imgbb(image_url):
    api_key = "c484b0041827b28ceb258842b2a83565"
    url = "https://api.imgbb.com/1/upload"
    params = {
        "key": api_key,
        "image": image_url
    }
    try:
        response = requests.post(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data["data"]["url"]
        else:
            print(f"上传失败，状态码：{response.status_code}")
            return None
    except Exception as e:
        print(f"请求出错：{e}")
        return None
def read_random_key_from_txt(file_path):
    keys = []
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                key = line.strip()
                if key:
                    keys.append(key)
        if keys:
            random_key = random.choice(keys)
            return random_key
        else:
            return None
    except FileNotFoundError:
        print(f"文件 {file_path} 不存在。")
        return None

def generate_image_with_prodia(style_preset="anime", upscale=True, prompt=None, model="anythingV5_PrtRE.safetensors [893e49b9]", negative_prompt="blurry, noisy, pixelated, cartoonish, abstract, simplistic, cropped, off-center, disproportional, washed-out, oversaturated, dull colors, low quality, deformed, glitchy and bad lighting, flat.", steps=28, cfg_scale=7, seed=-1, sampler="DPM++ 2M Karras", width=1024, height=1024, X_Prodia_Key="c765886d-2729-4d17-ac68-d74441dca8e0"):
    url = "https://api.prodia.com/v1/sd/generate"
    headers = {
        "X-Prodia-Key": X_Prodia_Key,
        "accept": "application/json",
        "content-type": "application/json"
    }
    data = {
        'prompt': prompt,
        'style_preset': style_preset,
        'upscale': upscale,
        'model': model,
        'negative_prompt': negative_prompt,
        'steps': int(steps),  # 尝试将 steps 转换为整数
        'cfg_scale': int(cfg_scale),  # 尝试将 cfg_scale 转换为整数
        'seed': int(seed),  # 尝试将 seed 转换为整数
        'sampler': sampler,
        'width': int(width),  # 尝试将 width 转换为整数
        'height': int(height),  # 尝试将 height 转换为整数
        'X_Prodia_Key': X_Prodia_Key
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        print(response)
        try:
            response_json = response.json()
            print(f"API 响应内容：{response_json}")
            job_id = response_json.get('job')
            if job_id:
                status_url = f"https://api.prodia.com/v1/job/{job_id}"
                while True:
                    status_response = requests.get(status_url, headers=headers)
                    try:
                        status_result = status_response.json()
                        print(f"状态检查响应内容：{status_result}")
                        status = status_result.get('status')
                        if status == 'succeeded':
                            image_url = status_result.get('imageUrl')
                            if image_url:
                                return image_url
                            else:
                                print("任务已成功，但未找到图像 URL，可能存在问题。")
                                return None
                        elif status in ['pending', 'processing', 'generating']:
                            print(f"状态：{status}，等待中...")
                            time.sleep(5)
                        else:
                            print(f"出现意外状态：{status}。")
                            return None
                    except ValueError as ve:
                        print(f"解析状态检查响应时出错：{ve}")
                        return None
            else:
                print("未获取到任务 ID。")
                return None
        except ValueError as ve:
            print(f"解析 API 响应时出错：{ve}")
            return None
    except requests.RequestException as e:
        print("请求出错:", e)
        return None

sourcekey_path = r"D:\JetBrains\Toolbox\PyCharm Community\pythonproject\AI绘图网站\pythonProject1\文档\sourcekey.txt"


@app.route('/generate_image', methods=['POST'])
def generate_image():
    data = flask.request.get_json()
    print(data)
    prompt = data.get('prompt')
    style_preset = data.get('style_preset')
    upscale = data.get('upscale')
    model = data.get('model')
    negative_prompt = data.get('negative_prompt')
    steps = data.get('steps')
    cfg_scale = data.get('cfg_scale')
    seed = data.get('seed')
    sampler = data.get('sampler')
    width = data.get('width')
    height = data.get('height')

    provided_key = data.get('my_key')
    # 假设正确的密钥为 expected_key

    check_key_flag=index.check_key(provided_key)
    if not check_key_flag:
        return flask.jsonify({'error': '密钥错误，无法继续'}), 403
    if not index.get_balance_for_key(provided_key):
        return flask.jsonify({'error': '身份通过但余额不足，无法继续'}), 422
    X_Prodia_Key = read_random_key_from_txt(sourcekey_path)
    print(X_Prodia_Key)
    image_url = generate_image_with_prodia(style_preset=style_preset, upscale=upscale, prompt=prompt, model=model, negative_prompt=negative_prompt, steps=steps, cfg_scale=cfg_scale, seed=seed, sampler=sampler, width=width, height=height, X_Prodia_Key=X_Prodia_Key)
    image_url=upload_image_to_imgbb(image_url)
    image_url=upload_image_to_api(image_url)

    if image_url:
        a=index.decrement_balance(provided_key)
        if a:
            return flask.jsonify({'image_url': image_url})
        else:
            return flask.jsonify({'error':'服务端结算异常,中止服务'}),501
    else:
        return flask.jsonify({'error': '图像生成失败'}), 500


@app.route('/login_register', methods=['POST'])
def login_register():
    # 假设这里用一个简单的字典模拟用户数据存储
    user_data = index.load_data()
    data = request.get_json()
    nickname = data.get('nickname')
    password = data.get('password')
    a=index.check_nickname_exists(nickname)
    print(a)
    # 判断昵称是否存在
    if not a:
        username = str(index.generate_unique_user_id())
        key = index.generate_key()
        index.add_user(username, data.get('password'), nickname, key)
        return make_response(jsonify({'message': '注册成功！'}), 302)
    else:

        for username, user_info in user_data.items():
            if user_info["nickname"] == nickname and user_info["password"] == password:
                return make_response(jsonify({'message': '登录成功！'}), 300)
            elif user_info["nickname"] == nickname and user_info["password"] != password:
                return make_response(jsonify({'message': '密码错误'}), 301)
                # 如果遍历完都没有找到匹配的，返回一个错误信息
        return make_response(jsonify({'message': '昵称存在但密码错误或其他问题'}), 400)
@app.route('/get_key', methods=['POST'])
def get_key():
    data = request.get_json()
    nickname = data.get('nickname')
    password = data.get('password')
    user_data = index.load_data()
    for username, user_info in user_data.items():
        if user_info["nickname"] == nickname and user_info["password"] == password:
            return make_response(jsonify({'key': user_info["key"], 'balance': user_info["balance"]}), 200)
    return make_response(jsonify({'message': '昵称或密码错误，无法获取密钥'}), 401)

@app.route('/modify_balance', methods=['POST'])
def modify_balance_api():
    data = request.get_json()
    key = data.get('key')
    new_balance = data.get('new_balance')
    if key and new_balance is not None:
        success = modify_balance_for_key(key, new_balance)
        if success:
            return jsonify({'message': '充值成功！'})
        else:
            return jsonify({'message': '密钥不存在. 操作失败.'}), 404
    else:
        return jsonify({'message': '无效的请求. 密钥和氪金数目必须填写.'}), 400
@app.route('/login')
def show_page1():
    return render_template('login.html')


@app.route('/index')
def show_page2():
   return render_template('index.html')
@app.route('/docs')
def show_page3():
   return render_template('API.html')
@app.route('/shop')
def show_page4():
   return render_template('shop.html')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=20000)