'''
Description: 
Author: wangdx
Date: 2021-11-28 13:47:41
LastEditTime: 2021-11-28 14:33:57
'''

import cv2
import os
import torch
import math
import glob
from utils.ggcnn import GGCNN


def drawGrasps(img, grasps, mode):
    """
    绘制grasp
    img: img data
    grasps: list()	元素是 [row, col, angle, width]
    mode: line / region
    """
    assert mode in ['line', 'region']

    num = len(grasps)
    for i, grasp in enumerate(grasps):
        row, col, angle, width = grasp

        if mode == 'line':
            width = width / 2
            k = math.tan(angle)
            if k == 0:
                dx = width
                dy = 0
            else:
                dx = k / abs(k) * width / pow(k ** 2 + 1, 0.5)
                dy = k * dx

            cv2.line(img, (int(col + dx), int(row - dy)), (int(col - dx), int(row + dy)), (0, 0, 255), 1)
            
            color_b = 255 / num * i
            color_r = 0
            color_g = -255 / num * i + 255
            cv2.circle(img, (col, row), 2, (color_b, color_g, color_r), -1)
        
        else:
            color_b = 255 / num * i
            color_r = 0
            color_g = -255 / num * i + 255
            img[row, col] = [color_b, color_g, color_r]


def drawRect(img, rect):
    """
    绘制矩形
    rect: [x1, y1, x2, y2]
    """
    cv2.rectangle(img, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 1)


if __name__ == '__main__':
    # 模型路径
    model = './ckpt/epoch_0213_acc_0.6374.pth'
    input_path = 'data'

    # 运行设备
    device_name = "cuda:0" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_name)
    # 初始化
    ggcnn = GGCNN(model, device=device_name)
    
    img_depth_files = glob.glob(os.path.join(input_path, '*d.tiff'))

    for img_depth_file in img_depth_files:
        print('processing ', img_depth_file)
        # 读取图像
        img_depth = cv2.imread(img_depth_file, -1)
        img_rgb = cv2.imread(img_depth_file.replace('d.tiff', 'r.png'))
        # 预测
        grasps, x1, y1 = ggcnn.predict(img_depth, mode='max')
        # print(grasps)
        # 绘制预测结果
        drawGrasps(img_rgb, grasps, mode='line')  
        rect = [x1, y1, x1 + 300, y1 + 300]
        drawRect(img_rgb, rect)

        # 可视化
        cv2.imshow('grasp', img_rgb)
        cv2.waitKey()

    print('FPS: ', ggcnn.fps())
