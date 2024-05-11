import argparse
from io import BytesIO
import os
import subprocess
import time
import matplotlib.pyplot as plt
import json
import requests
from PIL import Image, UnidentifiedImageError
import random
import tkinter as tk
from tkinter import filedialog, simpledialog

# comfyUI服务器的IP地址作为全局变量
URL = "http://10.194.82.233:8188"

def generate_large_random_number():
    # 设置随机数的最小值和最大值
    min_value = 100000000000000
    max_value = 999999999999999
    
    # 生成并返回一个随机整数
    return random.randint(min_value, max_value)

# 调用函数并打印结果


def handle_data():
    # 打开JSON文件并加载数据
    with open('data.json', 'r') as file:
        data = json.load(file)

    # 提取月份和步数
    months = [item['month'] for item in data]
    steps = [item['steps'] for item in data]

    # 创建条形图
    plt.figure(figsize=(12, 6))
    x_positions = []  # 用于存储条形图的x位置
    group_spacing = 1  # 每三个条形之间的组间隔

    # 生成新的x坐标位置
    current_position = 0
    for i in range(len(months)):
        x_positions.append(current_position)
        current_position += 1
        if (i + 1) % 3 == 0:  # 每组三个条形后增加额外的间隔
            current_position += group_spacing

    # 绘制条形图
    plt.plot(x_positions, steps,linestyle='-', color='skyblue')  # 可调整条形宽度以适应新的间距

    # 关闭坐标轴
    plt.axis('off')

    # 保存图表到文件
    plt.savefig('output.png')

    # 关闭图表，以释放内存
    plt.close()




def upload_image(file_path):
    print(f"正在上传图片 {file_path}...")
    with open(file_path, 'rb') as file:
        response = requests.post(f"{URL}/upload/image", files={'image': file})
    try:
        response_json = response.json()
        print("服务器响应:", response_json)  # 打印服务器响应以检查其内容
        return response_json['name']
    except json.JSONDecodeError as e:
        print("JSON 解析错误:", e)
        print("服务器返回的原始数据:", response.text)  # 打印原始响应数据
        raise


def post_prompt(prompt_data):
    """提交prompt并获取prompt_id"""
    response = requests.post(f"{URL}/prompt", json=prompt_data)
    return response.json()['prompt_id']

def check_status(prompt_id):
    """检查处理状态"""
    response = requests.get(f"{URL}/history")
    while prompt_id not in response.json():
        response = requests.get(f"{URL}/history")
        time.sleep(1)
    return response.json()[prompt_id]['status']['completed'], response.json()[prompt_id]['outputs']['106']['images'] 

def get_file(file_names):
    print(f"正在获取文件 {file_names}...")
    images = []
    for file_name in file_names:
        response = requests.get(f"{URL}/view?filename={file_name['filename']}")
        if response.status_code != 200:
            print("获取图像时出现错误，HTTP 状态码:", response.status_code)
            print("服务器响应内容:", response.text)
            continue  # 跳过这个文件的处理

        # 尝试打开图像
        try:
            image = Image.open(BytesIO(response.content))
            images.append(image)
        except UnidentifiedImageError as e:
            print(f"无法识别的图像文件 {file_name}，可能文件类型不正确或损坏:", e)
            continue  # 跳过这个文件的处理

    if not images:
        print("没有有效的图像文件被加载。")
        return None

    # 合成图像
    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)

    combined_image = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for img in images:
        combined_image.paste(img, (x_offset, 0))
        x_offset += img.width

    # combined_image.save('combined_result.png')
    print("已保存合成图片为 combined_result.png")
    return combined_image


def next():

    # 步骤1: 上传图片
    filename = upload_image("output.png")
    
    # 步骤2: 提交prompt
    with open("request.json", 'r') as json_file:
        prompt_data = json.load(json_file)
    prompt_data['prompt']['17']['inputs']['image'] = filename
    prompt_data['prompt']['39']['inputs']['seed'] = generate_large_random_number()
    prompt_data['prompt']['58']['inputs']['seed'] = generate_large_random_number()
    prompt_data['prompt']['74']['inputs']['seed'] = generate_large_random_number()
    prompt_data['prompt']['87']['inputs']['seed'] = generate_large_random_number()
    prompt_id = post_prompt(prompt_data)
    
    # 步骤3: 轮询检查状态，直到完成
    while True:
        completed,outputname = check_status(prompt_id)
        if completed :
            break
        time.sleep(1)  # 等待一秒后再次检查
    print("生成完成")
    # 步骤4: 获取文件内容
    file_content = get_file(outputname)
    if file_content:
        file_content.save('result.png')  # 保存文件内容
        print("最终结果已保存为 result.png")
        subprocess.call(('open', 'result.png')) if os.name == 'posix' else None


def handle_data_from_file():
    # 从文件中读取数据
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not file_path:
        return

    with open(file_path, 'r') as file:
        data = json.load(file)

    # 提取月份和步数
    months = [item['month'] for item in data]
    steps = [item['steps'] for item in data]

    # 创建条形图
    plt.figure(figsize=(12, 6))
    x_positions = []  # 用于存储条形图的x位置
    group_spacing = 1  # 每三个条形之间的组间隔

    # 生成新的x坐标位置
    current_position = 0
    for i in range(len(months)):
        x_positions.append(current_position)
        current_position += 1
        if (i + 1) % 3 == 0:  # 每组三个条形后增加额外的间隔
            current_position += group_spacing

    # 绘制条形图
    plt.plot(x_positions, steps, linestyle='-', color='skyblue')  # 可调整条形宽度以适应新的间距

    # 关闭坐标轴
    plt.axis('off')

    # 保存图表到文件
    plt.savefig('output.png')

    # 关闭图表，以释放内存
    plt.close()
    next()


def handle_data_from_input():
    # 使用tkinter创建一个图形界面
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 弹出对话框，让用户输入JSON字符串
    json_input = simpledialog.askstring("输入JSON", "请输入JSON数据:")

    try:
        # 将输入的JSON字符串解析为字典列表
        data = json.loads(json_input)
    except json.JSONDecodeError:
        print("输入的JSON格式不正确，请重新输入！")
        return

   # 提取月份和步数
    months = [item['month'] for item in data]
    steps = [item['steps'] for item in data]

    # 创建条形图
    plt.figure(figsize=(12, 6))
    x_positions = []  # 用于存储条形图的x位置
    group_spacing = 1  # 每三个条形之间的组间隔

    # 生成新的x坐标位置
    current_position = 0
    for i in range(len(months)):
        x_positions.append(current_position)
        current_position += 1
        if (i + 1) % 3 == 0:  # 每组三个条形后增加额外的间隔
            current_position += group_spacing

    # 绘制条形图
    plt.plot(x_positions, steps, linestyle='-', color='skyblue')  # 可调整条形宽度以适应新的间距

    # 关闭坐标轴
    plt.axis('off')

    # 保存图表到文件
    plt.savefig('output.png')

    # 关闭图表，以释放内存
    plt.close()

    next()


def main():
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(description='处理JSON数据并生成条形图。')
    parser.add_argument('--cli', action='store_true', help='指定JSON文件的路径。')
    parser.add_argument('--gui', action='store_true', help='直接输入JSON字符串。')
    print(parser.parse_args())
    # 解析命令行参数
    args = parser.parse_args()
    
    if args.gui:
        # 创建主程序的图形界面
        root = tk.Tk()
        root.title("数据输入选择")

        # 选择数据输入方式的标签
        label = tk.Label(root, text="请选择你的数据输入方式：")
        label.pack()

        # 文件输入的按钮
        file_button = tk.Button(root, text="文件输入", command=handle_data_from_file)
        file_button.pack()

        # 输入框输入的按钮
        input_button = tk.Button(root, text="输入框输入", command=handle_data_from_input)
        input_button.pack()
        root.mainloop()

    elif args.cli:
        handle_data()
        next()

if __name__ == "__main__":
    main()
