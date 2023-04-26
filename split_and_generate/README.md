# 滑窗程序交付

测试用图片在data下，output文件中包含了测试可视化结果。

## 图片框选和滑动窗口生成

`generate_window_annotations` 方法可以将图片框选的结果转换为滑动窗口的结果。

该函数读取输入的图像文件和相应的标注文件，并生成用于目标检测的滑动窗口及其相应的标注。生成的图像和标注将保存到输出文件中。

### 使用方法：
```python
generate_window_annotations(img_filename, annotation_filename, window_size=(300, 2000), stride=(150, 1000), output_folder='./output', threshold=0.2)
```
### 参数说明：
- img_filename：输入图像文件的路径
- annotation_filename：与输入图像对应的标注文件的路径
- window_size：滑动窗口的大小（默认为(300, 2000)）
- stride：滑动窗口的步长（默认为(150, 1000)）
- output_folder：生成的图像和标注文件的输出文件夹路径（默认为'./output'）
- threshold：bounding box与滑动窗口的交并比（IoU）的阈值（默认为0.2）

### 输出说明：

对于包含至少一个bounding box且其与滑动窗口的IoU大于阈值的每个滑动窗口，都会生成一个新的标注文件，其中bounding box的坐标相对于滑动窗口。相应的图像也会保存到输出文件夹中。

### 示例：
```python
img_filename = 'path/to/input/image.jpg'
annotation_filename = 'path/to/annotation/file.xml'
output_filename = 'path/to/output/image.jpg'
output_folder = 'path/to/output/folder'
window_size = (300, 2000)
stride = (150, 1000)
threshold = 0.2

save_bounding_boxes_image(img_filename, annotation_filename, output_filename)
generate_window_annotations(img_filename, annotation_filename, window_size, stride, output_folder, threshold)
``` 


## 检查滑动窗口的标注是否正确 - 可视化 

`save_bounding_boxes_image` 方法可以将标注文件中的bounding box可视化。

该函数读取输入的图像文件和相应的标注文件，并在图像中绘制bounding box。绘制后的图像将保存到输出文件中。

### 使用方法

```python
save_bounding_boxes_image(img_filename, annotation_filename, output_filename)
```

### 参数说明

- img_filename：输入图像文件的路径
- annotation_filename：与输入图像对应的标注文件的路径
- output_filename：绘制了bounding box的输出图像文件的路径