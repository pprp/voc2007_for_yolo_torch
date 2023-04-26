import os
import xml.etree.ElementTree as ET

import cv2


def generate_window_annotations(img_filename,
                                annotation_filename,
                                window_size=(300, 2000),
                                stride=(150, 1000),
                                output_folder='./output',
                                threshold=0.2):
    """ traverse the image and generate new annotations for each window
    Args:
        img_filename: path to the image file
        annotation_filename: path to the annotation file
        window_size: size of the sliding window
        stride: stride of the sliding window
        output_folder: path to the output folder
        threshold: minimum overlap between the window and the bounding box
    """

    # Load the image
    img = cv2.imread(img_filename)

    # Initialize a flag to indicate if at least one bounding box was found in the window
    bbox_found = False

    # Loop over the image to generate windows
    for y in range(0, img.shape[0], stride[1]):
        for x in range(0, img.shape[1], stride[0]):
            # Calculate the window bounds
            x_min = x
            x_max = x + window_size[0]
            if x_max > img.shape[1]:
                x_min = img.shape[1] - window_size[0]
                x_max = img.shape[1]
            y_min = y
            y_max = y + window_size[1]
            if y_max > img.shape[0]:
                y_min = img.shape[0] - window_size[1]
                y_max = img.shape[0]

            # Extract the window from the image
            window = img[y_min:y_max, x_min:x_max]

            # Create the annotation XML tree for the window
            annotation_tree = ET.ElementTree()
            annotation_root = ET.Element('annotation')
            annotation_tree._setroot(annotation_root)

            # Add the image filename to the annotation tree
            folder = ET.SubElement(annotation_root, 'folder')
            folder.text = os.path.dirname(os.path.abspath(img_filename))
            filename = ET.SubElement(annotation_root, 'filename')
            filename.text = os.path.basename(img_filename)
            path = ET.SubElement(annotation_root, 'path')
            path.text = os.path.abspath(img_filename)

            # Add the image size to the annotation tree
            size = ET.SubElement(annotation_root, 'size')
            width = ET.SubElement(size, 'width')
            width.text = str(window_size[0])
            height = ET.SubElement(size, 'height')
            height.text = str(window_size[1])
            depth = ET.SubElement(size, 'depth')
            depth.text = str(window.shape[2])

            # Loop over the bounding boxes in the original annotation file
            for obj in ET.parse(annotation_filename).findall('object'):
                xmin = int(obj.find('bndbox').find('xmin').text)
                ymin = int(obj.find('bndbox').find('ymin').text)
                xmax = int(obj.find('bndbox').find('xmax').text)
                ymax = int(obj.find('bndbox').find('ymax').text)

                # Calculate the bounding box coordinates relative to the window
                bbox_x_min = max(xmin - x_min, 0)
                bbox_y_min = max(ymin - y_min, 0)
                bbox_x_max = min(xmax - x_min, window_size[0])
                bbox_y_max = min(ymax - y_min, window_size[1])

                # Skip objects outside the window
                if bbox_x_min >= bbox_x_max or bbox_y_min >= bbox_y_max:
                    continue

                # Calculate the intersection coordinates
                inter_x_min = max(xmin, x_min)
                inter_y_min = max(ymin, y_min)
                inter_x_max = min(xmax, x_max)
                inter_y_max = min(ymax, y_max)

                # Calculate the intersection area
                inter_area = max(0, inter_x_max - inter_x_min) * max(
                    0, inter_y_max - inter_y_min)

                # Calculate the bounding box and window areas
                bbox_area = (xmax - xmin) * (ymax - ymin)
                window_area = window_size[0] * window_size[1]

                # Calculate the union area
                union_area = bbox_area  #+ window_area - inter_area

                # Calculate the IoU
                iou = inter_area / union_area

                if iou < threshold:
                    continue

                # Create the bounding box element for the annotation tree
                bbox = ET.SubElement(annotation_root, 'object')
                name = ET.SubElement(bbox, 'name')
                name.text = obj.find('name').text
                pose = ET.SubElement(bbox, 'pose')
                pose.text = obj.find('pose').text
                truncated = ET.SubElement(bbox, 'truncated')
                truncated.text = obj.find('truncated').text
                difficult = ET.SubElement(bbox, 'difficult')
                difficult.text = obj.find('difficult').text
                box = ET.SubElement(bbox, 'bndbox')
                xmin = ET.SubElement(box, 'xmin')
                xmin.text = str(bbox_x_min)
                ymin = ET.SubElement(box, 'ymin')
                ymin.text = str(bbox_y_min)
                xmax = ET.SubElement(box, 'xmax')
                xmax.text = str(bbox_x_max)
                ymax = ET.SubElement(box, 'ymax')
                ymax.text = str(bbox_y_max)

                # Set the flag to indicate that at least one bounding box was found in the window
                bbox_found = True

            # Save the annotation file if at least one bounding box was found in the window
            if bbox_found:
                annotation_name = f'./output/window_{x_min}-{y_min}_{x_max}-{y_max}.xml'
                annotation_tree.write(annotation_name)
                bbox_found = False

                # Save the window image and annotation files
                window_filename = f'./output/window_{x_min}-{y_min}_{x_max}-{y_max}.jpg'
                cv2.imwrite(window_filename, window)


if __name__ == '__main__':
    generate_window_annotations('./data/Untitled.jpg',
                                './data/Untitled.xml',
                                window_size=(300, 300),
                                stride=(150, 150),
                                output_folder='./output')
