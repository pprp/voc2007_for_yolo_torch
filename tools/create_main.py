import os
import random


def create_main_txts(trainval_percent, train_percent):
    xmlfilepath = 'Annotations'
    txtsavepath = 'ImageSets/Main'

    if not os.path.exists(txtsavepath):
        os.makedirs(txtsavepath)

    total_xml = os.listdir(xmlfilepath)
    num = len(total_xml)
    list = range(num)
    tv = int(num * trainval_percent)
    tr = int(tv * train_percent)
    trainval = random.sample(list, tv)
    train = random.sample(trainval, tr)

    ftrainval = open('ImageSets/Main/trainval.txt', 'w')
    ftest = open('ImageSets/Main/test.txt', 'w')
    ftrain = open('ImageSets/Main/train.txt', 'w')
    fval = open('ImageSets/Main/val.txt', 'w')

    for i in list:
        name = total_xml[i][:-4] + '\n'
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


if __name__ == '__main__':
    pass
