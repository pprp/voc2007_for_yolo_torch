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