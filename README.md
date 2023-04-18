# voc2007_for_torch

> 服务于于代码： https://github.com/ultralytics/yolov3
> 目前更新比较多，适配旧代码：https://github.com/GiantPandaCV/yolov3-point
> 也可以查看 https://github.com/pprp/deep_sort_yolov3_pytorch 中的yolov3部分的代码
> 如果有问题欢迎发issue进行提问，欢迎关注微信公众号：GiantPandaCV

![](https://img-blog.csdnimg.cn/20200116212417846.jpg)

如果不太理解，可以先看一下教程：https://www.cnblogs.com/pprp/p/10863496.html，然后再运行代码。

明确一下：所谓格式都是人为规定的，如果您发现代码无法运行，请先理解一下要求的格式。


这个库准备了一些python脚本，实现了以下功能：

- 检查图片和标注文件的对应关系
- 批量改动xml文件中对象的名称
- 创建Main文件中的四个txt文件
- 从xml文件中读取信息，转化为labels中的txt文件

## 0. 介绍

1. 将您的jpg格式的图片放在JPEGImges文件夹中
2. 将对应的xml格式的标注文件放在Annotations文件夹中
3. 按照您的数据集要求修改create_all.py中的参数部分
4. 运行create_all.py文件
5. 按照create_all.py文件中最后的提示处理。


## 1. 数据集检查

以下是一个标准的voc2007数据集文件排放方式。

```
  - data
       - VOC2007
            - Annotations (标签XML文件，用对应的labelimg生成的)
            - ImageSets (生成的方法是用python生成)
                - Main
                    - test.txt
                    - train.txt
                    - trainval.txt
                    - val.txt
            - JPEGImages(原始文件)
            - labels (xml文件对应的txt文件)
```

其中JPEGImages中的图片与Annotations中的xml文件个数应该是一致且一一对应的关系。

这里创建了一个简单的脚本进行评估一致性,需要建立新的文件夹Allempty， 意思是以xml文件为基准进行图片检查，如果图片不存在对应xml文件，那将图片移动到Allempty文件夹中。

脚本：check_jpgAndxml.py

```python
import os, shutil

def checkJpgXml(dir1, dir2, dir3, is_move=True):
    """
    dir1 是图片所在文件夹
    dir2 是标注文件所在文件夹
    dir3 是创建的，如果图片没有对应的xml文件，那就将图片放入dir3
    is_move 是确认是否进行移动，否则只进行打印
    """
    if not os.path.exists(dir3):
        os.mkdir(dir3)
    cnt = 0
    for file in os.listdir(dir1):
        f_name,f_ext = file.split(".")
        if not os.path.exists(os.path.join(dir2, f_name+".xml")):
            print(f_name)
            if is_move:
                cnt += 1
                shutil.move(os.path.join(dir1,file), os.path.join(dir3, file))
    if cnt > 0:
        print("有%d个文件不符合要求，已打印。"%(cnt))
    else:
        print("所有图片和对应的xml文件都是一一对应的。")

if __name__ == "__main__":
    dir1 = r".\JPEGImages"
    dir2 = r".\Annotations"
    dir3 = r".\Allempty"
    checkJpgXml(dir1, dir2, dir3, False)
```

## 2. 按照比例划分训练/验证/测试集合

脚本：create_main.py

```python
import os
import random

trainval_percent = 0.8
train_percent = 0.8

xmlfilepath = 'Annotations'
txtsavepath = 'ImageSets\Main'
total_xml = os.listdir(xmlfilepath)

num=len(total_xml)
list=range(num)
tv=int(num*trainval_percent)
tr=int(tv*train_percent)
trainval= random.sample(list,tv)
train=random.sample(trainval,tr)

ftrainval = open('ImageSets/Main/trainval.txt', 'w')
ftest = open('ImageSets/Main/test.txt', 'w')
ftrain = open('ImageSets/Main/train.txt', 'w')
fval = open('ImageSets/Main/val.txt', 'w')

for i  in list:
    name=total_xml[i][:-4]+'\n'
    if i in trainval:
        ftrainval.write(name)
        if i in train:
            ftrain.write(name)
        else:
            fval.write(name)
    else:
        ftest.write(name)

ftrainval.close()
ftrain.close()
fval.close()
ftest.close()
```

trainval_percent: 表示训练集和验证集占所有图片的比例。

train_percent: 表示训练集占训练集和验证集的比例。

## 3. 根据xml文件生成labels文件夹中的txt文件

脚本：voc_label.py

```python
# -*- coding: utf-8 -*-
"""
需要修改的地方：
1. sets中替换为自己的数据集
2. classes中替换为自己的类别
3. 将本文件放到VOC2007目录下
4. 直接开始运行
"""

import xml.etree.ElementTree as ET
import pickle
import os
from os import listdir, getcwd
from os.path import join
sets=[('2007', 'train'), ('2007', 'val'), ('2007', 'test')]  #替换为自己的数据集
classes = ["cow"]     #修改为自己的类别

def convert(size, box):
    dw = 1./(size[0])
    dh = 1./(size[1])
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

def convert_annotation(year, image_id):
    in_file = open('Annotations/%s.xml'%(image_id))  #将数据集放于当前目录下
    out_file = open('labels/%s.txt'%(image_id), 'w')
    tree=ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult)==1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w,h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')
wd = getcwd()
for year, image_set in sets:
    if not os.path.exists('labels/'):
        os.makedirs('labels/')
    image_ids = open('ImageSets/Main/%s.txt'%(image_set)).read().strip().split()
    list_file = open('%s_%s.txt'%(year, image_set), 'w')
    for image_id in image_ids:
        list_file.write('JPEGImages/%s.jpg\n'%(image_id))
        convert_annotation(year, image_id)
    list_file.close()
# os.system("cat 2007_train.txt 2007_val.txt > train.txt")     #修改为自己的数据集用作训练
```

## 4. 构建文件夹，按照pytorch版本的要求进行整理

当前文件夹构成：

```
  - data
       - VOC2007
            - Annotations (标签XML文件，用对应的labelimg生成的)
            - ImageSets (生成的方法是用python生成)
                - Main
                    - test.txt
                    - train.txt
                    - trainval.txt
                    - val.txt
            - JPEGImages(原始文件)
            - labels (xml文件对应的txt文件)
            - Allempty (用来存放不合要求的图片)
            - images (用于pytorch版本的图片保存)
            	- train2014
            		- 001.jpg
            		- 002.jpg
            	- val2014
            		- 100.jpg
            		- 101.jpg
            - label (用于pytorch版本的标签保存)
            	- train2014
            		- 001.txt
            		- 002.txt
            	- val2014
            		- 100.txt
            		- 101.txt
```

有群友反映这里的label不太理解，在这里统一解释一下，pytorch的yolov3是需要images和labels文件夹的，但是由于voc2007本身通过voc_label脚本构建的时候就存在labels文件夹，命名冲突，所以这里暂且命名为label，然后在使用的时候手动将label改为labels即可。

不过也不用很担心，最新更新了create_all.py里将所有步骤合并到一起，只需要修改一下create all文件中的参数，然后就可以一键从VOC2007格式转为pytorch所需要的yolov3的格式。

文件夹构造好以后，运行脚本：`make_for_yolov3_torch.py`

```python
import os, shutil

"""
需要满足以下条件：
1. 在JPEGImages中准备好图片
2. 在labels中准备好labels
3. 创建好如下所示的文件目录：
    - images
        - train2014
        - val2014
    - labels(由于voc格式中有labels文件夹，所以重命名为label)
        - train2014
        - val2014
"""


def make_for_torch_yolov3(dir_image,
                                 dir_label,
                                 dir1_train,
                                 dir1_val,
                                 dir2_train,
                                 dir2_val,
                                 main_trainval,
                                 main_test):
    if not os.path.exists(dir1_train):
        os.mkdir(dir1_train)
    if not os.path.exists(dir1_val):
        os.mkdir(dir1_val)
    if not os.path.exists(dir2_train):
        os.mkdir(dir2_train)
    if not os.path.exists(dir2_val):
        os.mkdir(dir2_val)

    with open(main_trainval, "r") as f1:
        for line in f1:
            print(line[:-1])
            # print(os.path.join(dir_image, line[:-1]+".jpg"), os.path.join(dir1_train, line[:-1]+".jpg"))
            shutil.copy(os.path.join(dir_image, line[:-1]+".jpg"),
                        os.path.join(dir1_train, line[:-1]+".jpg"))
            shutil.copy(os.path.join(dir_label, line[:-1]+".txt"),
                        os.path.join(dir2_train, line[:-1]+".txt"))


    with open(main_test, "r") as f2:
        for line in f2:
            print(line[:-1])
            shutil.copy(os.path.join(dir_image, line[:-1]+".jpg"),
                        os.path.join(dir1_val, line[:-1]+".jpg"))
            shutil.copy(os.path.join(dir_label, line[:-1]+".txt"),
                        os.path.join(dir2_val, line[:-1]+".txt"))

if __name__ == "__main__":
    '''
    https://github.com/ultralytics/yolov3
    这个pytorch版本的数据集组织
    - images
        - train2014 # dir1_train
        - val2014 # dir1_val
    - labels
        - train2014 # dir2_train
        - val2014 # dir2_val
    trainval.txt, test.txt 是由create_main.py构建的
    '''

    dir_image = r"C:\Users\pprp\Desktop\VOCdevkit\VOC2007\JPEGImages"
    dir_label = r"C:\Users\pprp\Desktop\VOCdevkit\VOC2007\labels"

    dir1_train = r"C:\Users\pprp\Desktop\VOCdevkit\VOC2007\images\train2014"
    dir1_val = r"C:\Users\pprp\Desktop\VOCdevkit\VOC2007\images\val2014"

    dir2_train = r"C:\Users\pprp\Desktop\VOCdevkit\VOC2007\label\train2014"
    dir2_val = r"C:\Users\pprp\Desktop\VOCdevkit\VOC2007\label\val2014"

    main_trainval = r"C:\Users\pprp\Desktop\VOCdevkit\VOC2007\ImageSets\Main\trainval.txt"
    main_test = r"C:\Users\pprp\Desktop\VOCdevkit\VOC2007\ImageSets\Main\test.txt"

    make_for_torch_yolov3(dir_image,
                            dir_label,
                            dir1_train,
                            dir1_val,
                            dir2_train,
                            dir2_val,
                            main_trainval,
                            main_test)
```
