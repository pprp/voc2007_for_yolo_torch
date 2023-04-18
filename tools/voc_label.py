"""
需要修改的地方：
1. sets中替换为自己的数据集
3. 将本文件放到VOC2007目录下
4. 直接开始运行
"""

import os
import pickle
import xml.etree.ElementTree as ET
from os import listdir
from os.path import join

sets = [('2007', 'train'), ('2007', 'val'), ('2007', 'test')]  #替换为自己的数据集


def convert(size, box):
    # 进行归一化
    dw = 1. / (size[0])
    dh = 1. / (size[1])
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


def convert_annotation(year, image_id, classes):
    in_file = open('Annotations/%s.xml' % (image_id), 'r',
                   encoding='utf-8')  #将数据集放于当前目录下
    out_file = open('voc_labels/%s.txt' % (image_id), 'w')
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult) == 1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text),
             float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w, h), b)
        out_file.write(
            str(cls_id) + ' ' + ' '.join([str(a) for a in bb]) + '\n')


def gen_voc_lable(classes):
    for year, image_set in sets:
        if not os.path.exists('voc_labels/'):
            os.makedirs('voc_labels/')
        image_ids = open('ImageSets/Main/%s.txt' %
                         (image_set)).readlines()  #.strip()#.split()
        # print(image_ids)
        print('*' * 20)
        list_file = open('%s_%s.txt' % (year, image_set), 'w')
        for image_id in image_ids:
            image_id = image_id[:-1]
            print(image_id)
            list_file.write('./data/images/%s2014/%s.jpg\n' %
                            (image_set, image_id))
            convert_annotation(year, image_id, classes)
        list_file.close()
