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