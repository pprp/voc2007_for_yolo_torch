import os
import cv2
import random
import shutil
from xml.etree.ElementTree import parse, Element


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
        f_name, f_ext = file.split(".")
        if not os.path.exists(os.path.join(dir2, f_name + ".xml")):
            print(f_name)
            if is_move:
                cnt += 1
                shutil.move(os.path.join(dir1, file), os.path.join(dir3, file))
    if cnt > 0:
        print("有%d个文件不符合要求，已打印。" % (cnt))
    else:
        print("所有图片和对应的xml文件都是一一对应的。")


def mk(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        print("There are %d files in %s" % (len(os.listdir(path), path)))


def plot_one_box(x, img, color=None, label=None, line_thickness=None):
    tl = line_thickness or round(
        0.001 * (img.shape[0] + img.shape[1]) / 2) + 1  # line thickness
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(img, c1, c2, color, thickness=tl)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(img, c1, c2, color, -1)  # filled
        cv2.putText(img,
                    label, (c1[0] - 3, c1[1] - 2),
                    0,
                    tl / 3, [225, 255, 255],
                    thickness=tf,
                    lineType=cv2.LINE_AA)


def rescale_img_bbox(xml_path, jpg_path, resizedSize, save_xml_path,
                     save_jpg_path):
    fileName = os.path.basename(jpg_path).split('.')[0]

    dom = parse(xml_path)
    root = dom.getroot()
    img = cv2.imread(jpg_path)
    img = cv2.resize(img, (resizedSize, resizedSize))

    ssize = root.find('size')
    w = int(ssize.find('width').text)
    h = int(ssize.find('height').text)

    for obj in root.iter('object'):
        # get scale
        w_scale = resizedSize / w
        h_scale = resizedSize / h

        # get coords
        tmp_name = obj.find('name').text
        xmlbox = obj.find('bndbox')
        x1, y1 = xmlbox.find('xmin').text, xmlbox.find('ymin').text
        x2, y2 = xmlbox.find('xmax').text, xmlbox.find('ymax').text
        print("IN:", x1, y1, x2, y2)
        x1, y1 = int(x1), int(y1)
        x2, y2 = int(x2), int(y2)

        #rescale
        x1, x2 = x1 * w_scale, x2 * w_scale
        y1, y2 = y1 * h_scale, y2 * h_scale

        # make new xml
        xmlbox.find('xmin').text = str(int(x1))
        xmlbox.find('ymin').text = str(int(y1))
        xmlbox.find('xmax').text = str(int(x2))
        xmlbox.find('ymax').text = str(int(y2))

        _box = [x1, y1, x2, y2]
        print("out:", _box)
        # plot_one_box(_box, img, label=tmp_name)

    cv2.imwrite(os.path.join(save_jpg_path, fileName + ".jpg"), img)
    dom.write(os.path.join(save_xml_path, fileName + ".xml"),
              xml_declaration=True)
    for obj in root.iter('object'):
        for whobj in root.iter('size'):
            whobj.find('width').text = str(int(resizedSize))
            whobj.find('height').text = str(int(resizedSize))


def changeName(xml_fold, origin_name, new_name):
    '''
    xml_fold: xml存放文件夹
    origin_name: 原始名字，比如弄错的名字，原先要cow,不小心打成cwo
    new_name: 需要改成的正确的名字，在上个例子中就是cow
    '''
    files = os.listdir(xml_fold)
    cnt = 0
    for xmlFile in files:
        file_path = os.path.join(xml_fold, xmlFile)
        dom = parse(file_path)
        root = dom.getroot()
        for obj in root.iter('object'):  #获取object节点中的name子节点
            tmp_name = obj.find('name').text
            if tmp_name == origin_name:  # 修改
                obj.find('name').text = new_name
                print("change %s to %s." % (origin_name, new_name))
                cnt += 1
        dom.write(file_path, xml_declaration=True)  #保存到指定文件
    print("有%d个文件被成功修改。" % cnt)

# if __name__ == "__main__":
#     changeName(xml_fold=r"/home/ubuntu/yolov3/voc2007Crack-labels（1）\C00",
#                origin_name='C00',
#                new_name='crack')


if __name__ == "__main__":
    # jpg_path = r"/home/ubuntu/yolov3/voc2007crack (329).jpg"
    # xml_path = r"/home/ubuntu/yolov3/voc2007crack (329).xml"

    jpg_dirs = "/home/ubuntu/yolov3/voc2007/JPEGImages"
    xml_dirs = "/home/ubuntu/yolov3/voc2007/Annotations"
    empty_dirs = "/home/ubuntu/yolov3/voc2007/empty"

    checkJpgXml(jpg_dirs, xml_dirs, empty_dirs)

    save_jpg_path = "/home/ubuntu/yolov3/voc2007/outjpgs"
    save_xml_path = "/home/ubuntu/yolov3/voc2007/outxmls"

    resizedSize = 416

    for file in os.listdir(jpg_dirs):
        fileName = file.split('.')[0]
        print(fileName)
        jpg_file_path = os.path.join(jpg_dirs, fileName + ".jpg")
        xml_file_path = os.path.join(xml_dirs, fileName + ".xml")

        rescale_img_bbox(xml_file_path, jpg_file_path, resizedSize,
                         save_xml_path, save_jpg_path)
