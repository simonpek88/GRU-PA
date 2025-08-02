# coding utf-8
import os
import warnings

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# cSpell:ignoreRegExp /[^\s]{16,}/
# cSpell:ignoreRegExp /\b[A-Z]{3,15}\b/g
# cSpell:ignoreRegExp /\b[A-Z]\b/g

# 忽略PNG警告
warnings.filterwarnings("ignore", "(?s).*iCCP.*")

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
        elif plate_type in ['small_new_energy', 'small_yellow_new_energy']:
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
        elif self.plate_type in ['small_new_energy', 'small_yellow_new_energy']:
            plate_images = self.generate_440_140_plate(plate_num_str_list)
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
    single_yellow_plate_bg = './Images/license_plate/background/single_yellow1.bmp'
    small_new_energy_plate_bg = './Images/license_plate/background/small_new_energy.jpg'
    small_new_energy_yellow_plate_bg = './Images/license_plate/background/big_new_energy.jpg'

    def __init__(self, plate_type):
        self.plate_type = plate_type

        if plate_type == 'single_blue':
            plate_image = imread_chinese(LicensePlateImageGenerator.single_blue_plate_bg)
        elif plate_type == 'single_yellow':
            plate_image = imread_chinese(LicensePlateImageGenerator.single_yellow_plate_bg)
        elif plate_type == 'small_new_energy':
            plate_image = imread_chinese(LicensePlateImageGenerator.small_new_energy_plate_bg)
        elif plate_type == 'small_yellow_new_energy':
            plate_image = imread_chinese(LicensePlateImageGenerator.small_new_energy_yellow_plate_bg)
        else:
            raise ValueError('该类型车牌目前功能尚未完成！')

        self.bg = plate_image

    def generate_template_image(self, width, height):

        return cv2.resize(self.bg, (width, height))


class ImageAugmentation(object):
    """图像增强操作: HSV变化, 添加背景, 高斯噪声, 污渍"""

    def __init__(self, plate_type, template_image):
        self.plate_type = plate_type
        # 确定字符颜色是否应该为黑色
        if plate_type == 'single_blue':
            # 字符为白色
            self.is_black_char = False
        elif plate_type in ['single_yellow', 'small_new_energy', 'small_yellow_new_energy']:
            # 字符为黑字
            self.is_black_char = True
        else:
            raise ValueError('暂时不支持该类型车牌')
        self.template_image = template_image
        # 色调, 饱和度, 亮度
        self.hue_keep = 0.8
        self.saturation_keep = 0.3
        self.value_keep = 0.2
        # 高斯噪声level
        self.level = 1 + ImageAugmentation.rand_reduce(4)
        # 污渍
        self.smu = imread_chinese("./Images/license_plate/background/smu.jpg")

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

    def rand_hsv(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # 色调, 饱和度, 亮度
        hsv[:, :, 0] = hsv[:, :, 0] * (self.hue_keep + np.random.random() * (1 - self.hue_keep))
        hsv[:, :, 1] = hsv[:, :, 1] * (self.saturation_keep + np.random.random() * (1 - self.saturation_keep))
        hsv[:, :, 2] = hsv[:, :, 2] * (self.value_keep + np.random.random() * (1 - self.value_keep))
        img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        return img

    def augment(self, img, horizontal_sight_direction=None, vertical_sight_direction=None):
        if not self.is_black_char:
            # 转为黑底白字
            img = cv2.bitwise_not(img)
            img = cv2.bitwise_or(img, self.template_image)
            #img = self.rand_hsv(img)
        else:
            # 底牌加车牌文字
            img = cv2.bitwise_and(img, self.template_image)
            #img = self.rand_hsv(img)

        img = self.add_gauss(img)
        img = self.add_noise(img)
        img = self.add_smudge(img)

        return img


class LicensePlateGenerator(object):
    @staticmethod
    def generate_license_plate_images(plate_type, plate_num_str_list, save_path):

        # 生成车牌号码, 白底黑字
        chars_image_generator = CharsImageGenerator(plate_type)
        chars_images = chars_image_generator.generate_images(plate_num_str_list)

        # 生成车牌底牌
        license_template_generator = LicensePlateImageGenerator(plate_type)
        template_image = license_template_generator.generate_template_image(chars_image_generator.plate_width, chars_image_generator.plate_height)

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

            i += 1


def overlay_image_preserve_transparency(main_image_path, template_path, overlay_path, output_path=None, threshold=0.8):
    try:
        main_image_pil = Image.open(main_image_path)
        # 确保是RGBA模式
        if main_image_pil.mode != 'RGBA':
            main_image_pil = main_image_pil.convert('RGBA')
    except:
        # 如果PIL无法读取，使用OpenCV读取并转换
        main_image_bgr = imread_chinese(main_image_path)
        main_image_rgb = cv2.cvtColor(main_image_bgr, cv2.COLOR_BGR2RGB)
        main_image_pil = Image.fromarray(main_image_rgb).convert('RGBA')

    # 读取OpenCV格式的主图用于模板匹配
    main_image_cv = imread_chinese(main_image_path)
    template_image = imread_chinese(template_path)

    # 模板匹配
    result = cv2.matchTemplate(main_image_cv, template_image, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)

    # 获取模板尺寸
    template_h, template_w = template_image.shape[:2]

    # 读取需要覆盖的图片
    try:
        overlay_image = Image.open(overlay_path)
        if overlay_image.mode != 'RGBA':
            overlay_image = overlay_image.convert('RGBA')
    except:
        overlay_image_bgr = imread_chinese(overlay_path)
        overlay_image_bgr = cv2.resize(overlay_image_bgr, (template_w, template_h))
        overlay_image_rgb = cv2.cvtColor(overlay_image_bgr, cv2.COLOR_BGR2RGB)
        overlay_image = Image.fromarray(overlay_image_rgb).convert('RGBA')

    # 调整覆盖图片大小以匹配模板尺寸
    overlay_image = overlay_image.resize((template_w, template_h), Image.Resampling.LANCZOS)

    # 在找到的位置进行覆盖
    match_found = False
    for (x, y) in zip(*locations[::-1]):
        # 确保坐标在合理范围内且x<70（根据你原来的条件）
        if x < main_image_pil.width and y < main_image_pil.height and x < 70:
            # 在主图上粘贴覆盖图片，保持透明度
            main_image_pil.paste(overlay_image, (x, y), overlay_image)
            match_found = True
            break  # 只处理第一个匹配位置

    # 保存结果
    if match_found:
        # 保存为PNG格式以保留透明度
        main_image_pil.save(output_path, 'PNG')

    return match_found


def overlay_image_on_transparent_background(main_image_path, template_path, overlay_path, output_path=None, threshold=0.8):
    main_image = Image.open(main_image_path)
    if main_image.mode != 'RGBA':
        main_image = main_image.convert('RGBA')

    # 获取主图尺寸
    main_w, main_h = main_image.size

    # 创建透明背景，尺寸与主图相同
    result_image = Image.new('RGBA', (main_w, main_h), (0, 0, 0, 0))

    # 先粘贴主图
    result_image.paste(main_image, (0, 0))

    # 读取OpenCV格式的图片用于模板匹配
    main_image_cv = imread_chinese(main_image_path)
    template_image = imread_chinese(template_path)

    # 模板匹配
    result_cv = cv2.matchTemplate(main_image_cv, template_image, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result_cv >= threshold)

    # 获取模板尺寸
    template_h, template_w = template_image.shape[:2]

    # 读取需要覆盖的图片
    overlay_image = Image.open(overlay_path)
    if overlay_image.mode != 'RGBA':
        overlay_image = overlay_image.convert('RGBA')

    # 调整覆盖图片大小以匹配模板尺寸
    overlay_image = overlay_image.resize((template_w, template_h), Image.Resampling.LANCZOS)

    # 在找到的位置进行覆盖
    match_found = False
    for (x, y) in zip(*locations[::-1]):
        # 确保坐标在合理范围内且x<70
        if x < main_w and y < main_h and x < 80 and x > 47 and y > 120 and y < 180:
            # 在结果图上粘贴覆盖图片
            result_image.paste(overlay_image, (x, y), overlay_image)
            match_found = True
            break  # 只处理第一个匹配位置

    # 保存结果
    if match_found:
        result_image.save(output_path, 'PNG')

    return match_found


# 使用示例
def create_plate_image(vehicle_num_pack, brand_logo_pack, vehicle_model_pack, userID_pack, vehicle_type='燃油蓝牌'):
    save_path = f"./Images/license_plate/user_vlp"
    img_folder = './Images/license_plate/vehicle_model'
    spec_model = ['passat', 'lavida', 'song_plus']
    if vehicle_type == '燃油蓝牌':
        ground_type = 'single_blue'
    elif vehicle_type == '燃油黄牌':
        ground_type = 'single_yellow'
    elif vehicle_type == '新能源绿牌':
        ground_type = 'small_new_energy'
    elif vehicle_type == '新能源黄牌':
        ground_type = 'small_yellow_new_energy'
    else:
        ground_type = None

    if ground_type:
        LicensePlateGenerator.generate_license_plate_images(ground_type, vehicle_num_pack, save_path)
        for index, value in enumerate(vehicle_num_pack):
            vlp_file = f"{save_path}/{value}.png"
            brand_logo_file = f"./Images/license_plate/vehicle_logo/{brand_logo_pack[index]}.png"
            vlp_brand_file = f"{save_path}/{brand_logo_pack[index]}_{value}.png"
            vlp_model_template_file = f"{img_folder}/{vehicle_model_pack[index]}.png"
            vlp_model_file = f"{save_path}/{userID_pack[index]}_{value}_{brand_logo_pack[index]}_{vehicle_model_pack[index]}.png"
            if not os.path.exists(vlp_brand_file) and os.path.exists(vlp_file) and os.path.exists(brand_logo_file):
                img1 = Image.open(vlp_file)
                img2 = Image.open(brand_logo_file)
                # 确保两张图片都是RGBA模式以支持透明度
                if img1.mode != 'RGBA':
                    img1 = img1.convert('RGBA')
                if img2.mode != 'RGBA':
                    img2 = img2.convert('RGBA')
                # 创建透明背景的图片
                stitch_img = Image.new("RGBA", (img1.width + img2.width + 10, 72), (0, 0, 0, 0))
                stitch_img.paste(img2, (0, 0))
                stitch_img.paste(img1, (img2.width + 10, 0))
                stitch_img.save(vlp_brand_file)
                img1.close()
                img2.close()
            if not os.path.exists(vlp_model_file) and os.path.exists(vlp_file) and os.path.exists(vlp_model_template_file):
                if vehicle_model_pack[index].lower() in spec_model:
                    lp_template_file = f'{img_folder}/lp_template_{vehicle_model_pack[index].lower()}.png'
                else:
                    lp_template_file = f'{img_folder}/lp_template.png'
                overlay_image_on_transparent_background(
                    main_image_path=vlp_model_template_file,
                    template_path=lp_template_file,
                    overlay_path=vlp_file,
                    output_path=vlp_model_file,
                    threshold=0.4
                )


# 使用示例
if __name__ == '__main__':
    # 使用示例
    #create_plate_image(['京HFR720'], ['dffx'], '燃油蓝牌')

    img_folder = './Images/license_plate/vehicle_model'
    # 在透明背景上合成主图和覆盖图
    result = overlay_image_on_transparent_background(
        main_image_path=f'{img_folder}/GLB220.png',
        template_path=f'{img_folder}/lp_template.png',
        overlay_path='./Images/license_plate/user_vlp/京K65158.png',
        output_path=f'./Images/license_plate/user_vlp/test_vlp.png',
        threshold=0.4
    )
    print(result)
