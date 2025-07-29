# coding utf-8
import os
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import numpy as np
import cv2
import random
import math

# cSpell:ignoreRegExp /[^\s]{16,}/
# cSpell:ignoreRegExp /\b[A-Z]{3,15}\b/g
# cSpell:ignoreRegExp /\b[A-Z]\b/g

def imread_chinese(path):
    with open(path, 'rb') as f:
        data = f.read()
    img_array = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    return img


class CharsImageGenerator(object):
    """生成字符图像, 背景为白色, 字体为黑色"""
    # 数字和英文字母列表
    numerals = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                'U', 'V', 'W', 'X', 'Y', 'Z']

    def __init__(self, plate_type):
        self.plate_type = plate_type
        # 字符图片参数
        self.font_ch = ImageFont.truetype("./fonts/platech.ttf", 180, 0)  # 中文字体格式
        self.font_en = ImageFont.truetype('./fonts/platechar.ttf', 240, 0)  # 英文字体格式
        self.bg_color = (255, 255, 255)  # 车牌背景颜色
        self.fg_color = (0, 0, 0)  # 车牌号的字体颜色

        self.plate_height = 280  # 车牌高度
        self.left_offset = 32  # 车牌号左边第一个字符的偏移量
        self.height_offset = 10  # 高度方向的偏移量
        self.char_height = 180  # 字符高度
        self.chinese_original_width = 180  # 中文字符原始宽度
        self.english_original_width = 90  # 非中文字符原始宽度
        if plate_type in ['single_blue', 'single_yellow']:
            self.char_num = 7
            self.char_width = 90  # 字符校正后的宽度
            self.plate_width = 880  # 车牌的宽度
            self.char_interval = 24  # 字符间的间隔
            self.point_size = 20  # 第2个字符与第三个字符间有一个点, 该点的尺寸
        elif plate_type == 'small_new_energy':
            self.char_num = 8
            self.first_char_width = 90  # 第一个字符校正后的宽度
            self.char_width = 86  # 其余字符校正后宽度
            self.plate_width = 960  # 车牌的宽度
            self.char_interval = 18  # 字符间的间隔
            self.point_size = 62  # 第2个字符与第三个字符间有一个点, 该点的尺寸
        else:
            raise ValueError('目前不支持该类型车牌！')

    def generate_images(self, plate_num_str_list):
        if self.plate_type in ['single_blue', 'single_yellow', ]:
            plate_images = self.generate_440_140_plate(plate_num_str_list)
        elif self.plate_type == 'small_new_energy':
            plate_images = self.generate_480_140_plate(plate_num_str_list)
        else:
            raise ValueError('该类型车牌目前功能尚未完成！')

        return plate_images

    def generate_440_140_plate(self, plate_num_str_list):
        """ 生成440 * 140尺寸的7位车牌字符图片
        :param plate_nums:
        :return:
        """
        plate_images = list()
        for plate_num in plate_num_str_list:
            # 创建空白车牌号图片
            img = np.array(Image.new("RGB", (self.plate_width, self.plate_height), self.bg_color))
            # 每个字符的x轴起始、终止位置
            char_width_start = self.left_offset
            char_width_end = char_width_start + self.char_width
            img[:, char_width_start:char_width_end] = self.generate_char_image(
                plate_num[0])  # 生成的图片和img的第一维大小相同, 所以在img中直接使用符号":"

            char_width_start = char_width_end + self.char_interval
            char_width_end = char_width_start + self.char_width
            img[:, char_width_start:char_width_end] = self.generate_char_image(plate_num[1])
            # 隔开特殊间隙, 继续添加车牌的后续车牌号
            char_width_end = char_width_end + self.point_size + self.char_interval
            for i in range(2, len(plate_num)):
                char_width_start = char_width_end + self.char_interval
                char_width_end = char_width_start + self.char_width
                img[:, char_width_start:char_width_end] = self.generate_char_image(plate_num[i])

            plate_images.append(img)
            # chars_image debug
            # cv2.imshow("chars_image debug", img)
            # cv2.waitKey()

        return plate_images

    def generate_char_image(self, char):
        """ 生成字符图片
        :param char: 字符
        :return:
        """
        # 根据是否中文字符, 选择生成模式
        if char in CharsImageGenerator.numerals or char in CharsImageGenerator.alphabet:
            img = self.generate_en_char_image(char)
        else:
            img = self.generate_ch_char_image(char)

        return img

    def generate_ch_char_image(self, char):
        """ 生成中文字符图片
        :param char: 待生成的中文字符
        """
        img = Image.new("RGB", (self.chinese_original_width, self.plate_height), self.bg_color)
        ImageDraw.Draw(img).text((0, self.height_offset), char, self.fg_color, font=self.font_ch)
        img = img.resize((self.char_width, self.plate_height))

        return np.array(img)

    def generate_en_char_image(self, char):
        """" 生成英文字符图片
        :param char: 待生成的英文字符
        """
        img = Image.new("RGB", (self.english_original_width, self.plate_height), self.bg_color)
        ImageDraw.Draw(img).text((0, self.height_offset), char, self.fg_color, font=self.font_en)
        img = img.resize((self.char_width, self.plate_height))

        return np.array(img)


class LicensePlateImageGenerator(object):
    """根据车牌类型生成底牌图片"""
    single_blue_plate_bg = './Images/license_plate/background/single_blue1.bmp'
    small_new_energy_plate_bg = './Images/license_plate/background/small_new_energy.jpg'

    def __init__(self, plate_type):
        self.plate_type = plate_type

        if plate_type == 'single_blue':
            plate_image = imread_chinese(LicensePlateImageGenerator.single_blue_plate_bg)
        elif plate_type == 'small_new_energy':
            plate_image = imread_chinese(LicensePlateImageGenerator.small_new_energy_plate_bg)
        else:
            raise ValueError('该类型车牌目前功能尚未完成！')

        self.bg = plate_image

    def generate_template_image(self, width, height):

        return cv2.resize(self.bg, (width, height))


class ImageAugmentation(object):
    """图像增强操作: HSV变化, 添加背景, 高斯噪声, 污渍"""
    horizontal_sight_directions = ('left', 'mid', 'right')
    vertical_sight_directions = ('up', 'mid', 'down')

    def __init__(self, plate_type, template_image):
        self.plate_type = plate_type
        # 确定字符颜色是否应该为黑色
        if plate_type == 'single_blue':
            # 字符为白色
            self.is_black_char = False
        elif plate_type in ['single_yellow', 'small_new_energy']:
            # 字符为黑字
            self.is_black_char = True
        else:
            raise ValueError('暂时不支持该类型车牌')
        self.template_image = template_image
        # 透视变换
        self.angle_horizontal = 15
        self.angle_vertical = 15
        self.angle_up_down = 10
        self.angle_left_right = 5
        self.factor = 10
        # 色调, 饱和度, 亮度
        self.hue_keep = 0.8
        self.saturation_keep = 0.3
        self.value_keep = 0.2
        # 自然环境照片的路径列表
        self.env_data_paths = ImageAugmentation.search_file("background")
        # 高斯噪声level
        self.level = 1 + ImageAugmentation.rand_reduce(4)
        # 污渍
        self.smu = imread_chinese("./Images/license_plate/background/smu.jpg")

    def left_right_transfer(self, img, is_left=True, angle=None):
        """
        左右视角, 默认左视角
        :param img:
        :param is_left:
        :param angle: 角度
        :return:
        """
        if angle is None:
            angle = self.angle_left_right

        shape = img.shape
        size_src = (shape[1], shape[0])  # width, height
        # 源图像四个顶点坐标
        pts1 = np.float32([[0, 0], [0, size_src[1]], [size_src[0], 0], [size_src[0], size_src[1]]])
        # 计算图片进行投影倾斜后的位置
        interval = abs(int(math.sin((float(angle) / 180) * math.pi) * shape[0]))
        # 目标图像上四个顶点的坐标
        if is_left:
            pts2 = np.float32([[0, 0], [0, size_src[1]],
                               [size_src[0], interval], [size_src[0], size_src[1] - interval]])
        else:
            pts2 = np.float32([[0, interval], [0, size_src[1] - interval],
                               [size_src[0], 0], [size_src[0], size_src[1]]])
        # 获取 3x3的投影映射/透视变换 矩阵
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        dst = cv2.warpPerspective(img, matrix, size_src)

        return dst, matrix, size_src

    def up_down_transfer(self, img, is_down=True, angle=None):
        """ 上下视角, 默认下视角
        :param img: 正面视角原始图片
        :param is_down: 是否下视角
        :param angle: 角度
        :return:
        """
        if angle is None:
            angle = self.rand_reduce(self.angle_up_down)

        shape = img.shape
        size_src = (shape[1], shape[0])
        # 源图像四个顶点坐标
        pts1 = np.float32([[0, 0], [0, size_src[1]], [size_src[0], 0], [size_src[0], size_src[1]]])
        # 计算图片进行投影倾斜后的位置
        interval = abs(int(math.sin((float(angle) / 180) * math.pi) * shape[0]))
        # 目标图像上四个顶点的坐标
        if is_down:
            pts2 = np.float32([[interval, 0], [0, size_src[1]],
                               [size_src[0] - interval, 0], [size_src[0], size_src[1]]])
        else:
            pts2 = np.float32([[0, 0], [interval, size_src[1]],
                               [size_src[0], 0], [size_src[0] - interval, size_src[1]]])
        # 获取 3x3的投影映射/透视变换 矩阵
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        dst = cv2.warpPerspective(img, matrix, size_src)

        return dst, matrix, size_src

    def vertical_tilt_transfer(self, img, is_left_high=True):
        """ 添加按照指定角度进行垂直倾斜(上倾斜或下倾斜, 最大倾斜角度self.angle_vertical一半）
        :param img: 输入图像的numpy
        :param is_left_high: 图片投影的倾斜角度, 左边是否相对右边高
        """
        angle = self.rand_reduce(self.angle_vertical)

        shape = img.shape
        size_src = [shape[1], shape[0]]
        # 源图像四个顶点坐标
        pts1 = np.float32([[0, 0], [0, size_src[1]], [size_src[0], 0], [size_src[0], size_src[1]]])

        # 计算图片进行上下倾斜后的距离, 及形状
        interval = abs(int(math.sin((float(angle) / 180) * math.pi) * shape[1]))
        size_target = (int(math.cos((float(angle) / 180) * math.pi) * shape[1]), shape[0] + interval)
        # 目标图像上四个顶点的坐标
        if is_left_high:
            pts2 = np.float32([[0, 0], [0, size_target[1] - interval],
                               [size_target[0], interval], [size_target[0], size_target[1]]])
        else:
            pts2 = np.float32([[0, interval], [0, size_target[1]],
                               [size_target[0], 0], [size_target[0], size_target[1] - interval]])

        # 获取 3x3的投影映射/透视变换 矩阵
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        dst = cv2.warpPerspective(img, matrix, size_target)

        return dst, matrix, size_target

    def horizontal_tilt_transfer(self, img, is_right_tilt=True):
        """ 添加按照指定角度进行水平倾斜(右倾斜或左倾斜, 最大倾斜角度self.angle_horizontal一半）
        :param img: 输入图像的numpy
        :param is_right_tilt: 图片投影的倾斜方向（右倾, 左倾）
        """
        angle = self.rand_reduce(self.angle_horizontal)

        shape = img.shape
        size_src = [shape[1], shape[0]]
        # 源图像四个顶点坐标
        pts1 = np.float32([[0, 0], [0, size_src[1]], [size_src[0], 0], [size_src[0], size_src[1]]])

        # 计算图片进行左右倾斜后的距离, 及形状
        interval = abs(int(math.sin((float(angle) / 180) * math.pi) * shape[0]))
        size_target = (shape[1] + interval, int(math.cos((float(angle) / 180) * math.pi) * shape[0]))
        # 目标图像上四个顶点的坐标
        if is_right_tilt:
            pts2 = np.float32([[interval, 0], [0, size_target[1]],
                               [size_target[0], 0], [size_target[0] - interval, size_target[1]]])
        else:
            pts2 = np.float32([[0, 0], [interval, size_target[1]],
                               [size_target[0] - interval, 0], [size_target[0], size_target[1]]])

        # 获取 3x3的投影映射/透视变换 矩阵
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        dst = cv2.warpPerspective(img, matrix, size_target)

        return dst, matrix, size_target

    def sight_transfer(self, images, horizontal_sight_direction, vertical_sight_direction):
        """
        对图片进行视角变换
        :param images:
        :param horizontal_sight_direction: 水平视角变换方向
        :param vertical_sight_direction: 垂直视角变换方向
        :return:
        """
        flag = 0
        img_num = len(images)
        # 左右视角
        if horizontal_sight_direction == 'left':
            flag += 1
            images[0], matrix, size = self.left_right_transfer(images[0], is_left=True)
            for i in range(1, img_num):
                images[i] = cv2.warpPerspective(images[i], matrix, size)
        elif horizontal_sight_direction == 'right':
            flag -= 1
            images[0], matrix, size = self.left_right_transfer(images[0], is_left=False)
            for i in range(1, img_num):
                images[i] = cv2.warpPerspective(images[i], matrix, size)
        else:
            pass

        # 上下视角
        if vertical_sight_direction == 'down':
            flag += 1
            images[0], matrix, size = self.up_down_transfer(images[0], is_down=True)
            for i in range(1, img_num):
                images[i] = cv2.warpPerspective(images[i], matrix, size)
        elif vertical_sight_direction == 'up':
            flag -= 1
            images[0], matrix, size = self.up_down_transfer(images[0], is_down=False)
            for i in range(1, img_num):
                images[i] = cv2.warpPerspective(images[i], matrix, size)
        else:
            pass

        # 左下视角 或 右上视角
        if abs(flag) == 2:
            images[0], matrix, size = self.vertical_tilt_transfer(images[0], is_left_high=True)
            for i in range(1, img_num):
                images[i] = cv2.warpPerspective(images[i], matrix, size)

            images[0], matrix, size = self.horizontal_tilt_transfer(images[0], is_right_tilt=True)
            for i in range(1, img_num):
                images[i] = cv2.warpPerspective(images[i], matrix, size)
        # 左上视角 或 右下视角
        elif abs(flag) == 1:
            images[0], matrix, size = self.vertical_tilt_transfer(images[0], is_left_high=False)
            for i in range(1, img_num):
                images[i] = cv2.warpPerspective(images[i], matrix, size)

            images[0], matrix, size = self.horizontal_tilt_transfer(images[0], is_right_tilt=False)
            for i in range(1, img_num):
                images[i] = cv2.warpPerspective(images[i], matrix, size)
        else:
            pass

        return images

    @staticmethod
    def search_file(search_path, file_format='.jpg'):
        """在指定目录search_path下, 递归目录搜索指定尾缀的文件"""
        file_path_list = []
        for root_path, dir_names, file_names in os.walk(search_path):
            for filename in file_names:
                if filename.endswith(file_format):
                    file_path_list.append(os.path.join(root_path, filename))

        return file_path_list

    @staticmethod
    def rand_reduce(val):

        return int(np.random.random() * val)

    def add_gauss(self, img, level=None):
        """ 添加高斯模糊
        :param img: 待加噪图片
        :param level: 加噪水平
        """
        if level is None:
            level = self.level

        return cv2.blur(img, (level * 2 + 1, level * 2 + 1))

    def add_single_channel_noise(self, single):
        """ 添加高斯噪声
        :param single: 单一通道的图像数据
        """
        diff = 255 - single.max()
        noise = np.random.normal(0, 1 + self.rand_reduce(6), single.shape)
        noise = (noise - noise.min()) / (noise.max() - noise.min())
        noise = diff * noise
        noise = noise.astype(np.uint8)
        dst = single + noise

        return dst

    def add_noise(self, img):
        """添加噪声"""
        img[:, :, 0] = self.add_single_channel_noise(img[:, :, 0])
        img[:, :, 1] = self.add_single_channel_noise(img[:, :, 1])
        img[:, :, 2] = self.add_single_channel_noise(img[:, :, 2])

        return img

    def add_smudge(self, img, smu=None):
        """添加污渍"""
        if smu is None:
            smu = self.smu
        # 截取某一部分
        rows = self.rand_reduce(smu.shape[0] - img.shape[0])
        cols = self.rand_reduce(smu.shape[1] - img.shape[1])
        add_smu = smu[rows:rows + img.shape[0], cols:cols + img.shape[1]]
        img = cv2.bitwise_not(img)
        img = cv2.bitwise_and(add_smu, img)
        img = cv2.bitwise_not(img)

        return img

    def rand_environment(self, img, env_data_paths=None):
        """ 添加自然环境的噪声
        :param img: 待加噪图片
        :param env_data_paths: 自然环境图片路径列表
        """
        if env_data_paths is None:
            env_data_paths = self.env_data_paths
        # 随机选取环境照片
        print(env_data_paths)
        index = self.rand_reduce(len(env_data_paths))
        env = imread_chinese(env_data_paths[index])
        env = cv2.resize(env, (img.shape[1], img.shape[0]))
        # 找到黑背景, 反转为白
        bak = (img == 0)
        for i in range(bak.shape[2]):
            bak[:, :, 0] &= bak[:, :, i]
        for i in range(bak.shape[2]):
            bak[:, :, i] = bak[:, :, 0]
        bak = bak.astype(np.uint8) * 255
        # 环境照片用白掩码裁剪, 然后与原图非黑部分合并
        inv = cv2.bitwise_and(bak, env)
        img = cv2.bitwise_or(inv, img)

        return img

    def rand_hsv(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # 色调, 饱和度, 亮度
        hsv[:, :, 0] = hsv[:, :, 0] * (self.hue_keep + np.random.random() * (1 - self.hue_keep))
        hsv[:, :, 1] = hsv[:, :, 1] * (self.saturation_keep + np.random.random() * (1 - self.saturation_keep))
        hsv[:, :, 2] = hsv[:, :, 2] * (self.value_keep + np.random.random() * (1 - self.value_keep))
        img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        return img

    def augment(self, img, horizontal_sight_direction=None, vertical_sight_direction=None):
        if horizontal_sight_direction is None:
            horizontal_sight_direction = ImageAugmentation.horizontal_sight_directions[random.randint(0, 2)]
        if vertical_sight_direction is None:
            vertical_sight_direction = ImageAugmentation.vertical_sight_directions[random.randint(0, 2)]


        if not self.is_black_char:
            # 转为黑底白字
            img = cv2.bitwise_not(img)
            img = cv2.bitwise_or(img, self.template_image)
            # 基于视角的变换
            img = self.sight_transfer([img], horizontal_sight_direction, vertical_sight_direction)
            img = img[0]
            #img = self.rand_environment(img)
            img = self.rand_hsv(img)
        else:
            # 底牌加车牌文字
            img = cv2.bitwise_and(img, self.template_image)
            # 基于视角的变换
            img = self.sight_transfer([img], horizontal_sight_direction, vertical_sight_direction)
            img = img[0]
            img = self.rand_environment(img)
            img = self.rand_hsv(img)

        img = self.add_gauss(img)
        img = self.add_noise(img)
        img = self.add_smudge(img)

        return img

class LicensePlateGenerator(object):

    @staticmethod
    def generate_license_plate_images(plate_type, plate_num_str_list, save_path):
        print('\r>> 生成车牌号图片...')

        # 生成车牌号码, 白底黑字
        chars_image_generator = CharsImageGenerator(plate_type)
        chars_images = chars_image_generator.generate_images(plate_num_str_list)

        # 生成车牌底牌
        license_template_generator = LicensePlateImageGenerator(plate_type)
        template_image = license_template_generator.generate_template_image(chars_image_generator.plate_width, chars_image_generator.plate_height)

        print('\r>> 生成车牌图片...')

        # 数据增强及车牌字符颜色修正, 并保存
        augmentation = ImageAugmentation(plate_type, template_image)
        plate_height = 72
        plate_width = int(chars_image_generator.plate_width * plate_height / chars_image_generator.plate_height)
        i = 1
        for index, char_image in enumerate(chars_images):
            image_name = plate_num_str_list[index] + ".png"
            image_path = os.path.join(save_path, image_name)
            image = augmentation.augment(char_image)
            image = cv2.resize(image, (plate_width, plate_height))
            cv2.imencode('.png', image)[1].tofile(image_path)
            print("\r>> {} done...".format(image_name))

            i += 1


def create_plate_image(vehicle_num, vehicle_type):
    save_path = f"./Images/license_plate"
    plate_num_str_list = [vehicle_num]
    if vehicle_type == '燃油车':
        ground_type = 'single_blue'
    elif vehicle_type == '新能源车':
        ground_type = 'small_new_energy'

    LicensePlateGenerator.generate_license_plate_images(ground_type, plate_num_str_list, save_path)

create_plate_image('浙A5B5T3', '燃油车')
