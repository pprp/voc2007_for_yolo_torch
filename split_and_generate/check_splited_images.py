import os
import xml.etree.ElementTree as ET

import cv2


def save_bounding_boxes_image(img_filename, annotation_filename):
    # Load the image
    img = cv2.imread(img_filename)

    # Load the annotation file
    annotation_tree = ET.parse(annotation_filename)

    # Loop over the bounding boxes in the annotation file
    for obj in annotation_tree.findall('object'):
        # Get the bounding box coordinates
        xmin = int(obj.find('bndbox').find('xmin').text)
        ymin = int(obj.find('bndbox').find('ymin').text)
        xmax = int(obj.find('bndbox').find('xmax').text)
        ymax = int(obj.find('bndbox').find('ymax').text)

        # Draw the bounding box on the image
        cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)

    # Save the image with the bounding boxes
    filename, extension = os.path.splitext(img_filename)
    output_filename = filename + '_vis' + extension
    cv2.imwrite(output_filename, img)


output_folder = './output'

# Loop over all the jpg files in the output folder
for filename in os.listdir(output_folder):
    if filename.endswith('.jpg'):
        # Check if there's a corresponding xml file
        xml_filename = os.path.join(output_folder,
                                    filename.split('.')[0] + '.xml')
        if os.path.exists(xml_filename):
            # Apply the save_bounding_boxes_image function to the jpg and xml pair
            img_filename = os.path.join(output_folder, filename)
            save_bounding_boxes_image(img_filename, xml_filename)
