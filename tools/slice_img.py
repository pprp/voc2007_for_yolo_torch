import cv2
import numpy as np
import xml.etree.ElementTree as ET


def visualize(im, bboxes):
    '''Draw bounding boxes on the image'''
    for bbox in bboxes:
        x, y, w, h = bbox
        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return im



def process_annotation(annotation_path, outdir, slice_height=256, slice_width=256, 
                       zero_frac_thresh=0.2, overlap=0.2):
    '''Process annotation file and create new annotations for sliced images'''

    tree = ET.parse(annotation_path)
    root = tree.getroot()
    
    # extract image size from annotation
    size_elem = root.find('size')
    im_width = int(size_elem.find('width').text)
    im_height = int(size_elem.find('height').text)

    # compute the strides for width and height
    stride_h = int(np.ceil((1.0 - overlap) * slice_height))
    stride_w = int(np.ceil((1.0 - overlap) * slice_width))

    # compute the number of windows in height and width
    num_win_h = int(np.ceil((im_height - slice_height) / stride_h)) + 1
    num_win_w = int(np.ceil((im_width - slice_width) / stride_w)) + 1

    # create new annotation for each sliced image
    count = 0
    for i in range(num_win_h):
        for j in range(num_win_w):
            # compute the coordinates of the window
            y = i * stride_h
            x = j * stride_w
            ymax = min(y + slice_height, im_height)
            xmax = min(x + slice_width, im_width)

            # ignore windows with too many null pixels
            window_size = (ymax - y) * (xmax - x)
            bbox_list = []
            is_valid = True
            for obj in root.findall('object'):
                bbox_elem = obj.find('bndbox')
                xmin = int(bbox_elem.find('xmin').text)
                ymin = int(bbox_elem.find('ymin').text)
                xmax_obj = int(bbox_elem.find('xmax').text)
                ymax_obj = int(bbox_elem.find('ymax').text)

                # check if object is inside the window
                if xmin >= xmax or ymin >= ymax or xmax_obj <= x or ymax_obj <= y:
                    continue

                # adjust bounding box coordinates to fit in the window
                xmin = max(x, xmin) - x
                ymin = max(y, ymin) - y
                xmax_obj = min(xmax_obj, xmax) - x
                ymax_obj = min(ymax_obj, ymax) - y

                # check if adjusted bounding box has non-zero area
                bbox_size = (ymax_obj - ymin) * (xmax_obj - xmin)
                if bbox_size <= 0:
                    continue

                # add adjusted bounding box to list
                bbox_list.append((xmin, ymin, xmax_obj, ymax_obj))

                # compute fraction of null pixels in window
                window = np.zeros((slice_height, slice_width))
                window[ymin:ymax_obj, xmin:xmax_obj] = 1
                null_frac = 1.0 - (np.sum(window) / window_size)

                # check if fraction of null pixels is below threshold
                if null_frac > zero_frac_thresh:
                    is_valid = False
                    break

            # create new annotation if window is valid
            if is_valid:
                count += 1
                new_annotation_path = os.path.join(outdir, f"{count}.xml")
                new_root = ET.Element("annotation")

                # copy elements from original annotation to new annotation
                new_root.append(root.find("folder"))
                new_root.append(root.find("filename"))
                new_root.append(root.find("source"))
                new_root.append(root.find("owner"))
                size_elem = ET.SubElement(new_root, "size")
                size_elem.append(ET.Element("width", text=str(slice_width)))
                size_elem.append(ET.Element("height", text=str(slice_height)))
                size_elem.append(root.find("depth"))
                new_root.append(root.find("segmented"))

                # add adjusted bounding boxes to new annotation
                for bbox in bbox_list:
                    obj_elem = ET.SubElement(new_root, "object")
                    obj_elem.append(ET.Element("name", text="object"))
                    obj_elem.append(root.find("pose"))
                    obj_elem.append(root.find("truncated"))
                    obj_elem.append(root.find("difficult"))
                    bbox_elem = ET.SubElement(obj_elem, "bndbox")
                    bbox_elem.append(ET.Element("xmin", text=str(bbox[0])))
                    bbox_elem.append(ET.Element("ymin", text=str(bbox[1])))
                    bbox_elem.append(ET.Element("xmax", text=str(bbox[2])))
                    bbox_elem.append(ET.Element("ymax", text=str(bbox[3])))

                # write new annotation to file
                tree = ET.ElementTree(new_root)
                tree.write(new_annotation_path)

    print(f"Processed {count} slices")

def slice_im(image_path,
             out_name,
             outdir,
             slice_height=256,
             slice_width=256,
             zero_frac_thresh=0.2,
             overlap=0.2,
             verbose=False):
    '''Slice large satellite image into smaller pieces,
    ignore slices with a percentage null greater then zero_fract_thresh
    Assume three bands!'''

    image0 = cv2.imread(image_path, 1)  # color
    ext = '.' + image_path.split('.')[-1]
    win_h, win_w = image0.shape[:2]

    # if slice sizes are large than image, pad the edges
    pad = 0
    if slice_height > win_h:
        pad = slice_height - win_h
    if slice_width > win_w:
        pad = max(pad, slice_width - win_w)
    # pad the edge of the image with black pixels
    if pad > 0:
        border_color = (0, 0, 0)
        image0 = cv2.copyMakeBorder(image0,
                                    pad,
                                    pad,
                                    pad,
                                    pad,
                                    cv2.BORDER_CONSTANT,
                                    value=border_color)
        win_h, win_w = image0.shape[:2]

    # compute the strides for width and height
    stride_h = int(np.ceil((1.0 - overlap) * slice_height))
    stride_w = int(np.ceil((1.0 - overlap) * slice_width))

    # compute the number of windows in height and width
    num_win_h = int(np.ceil((win_h - slice_height) / stride_h)) + 1
    num_win_w = int(np.ceil((win_w - slice_width) / stride_w)) + 1

    # slice the image and save the windows
    count = 0
    for i in range(num_win_h):
        for j in range(num_win_w):
            # compute the coordinates of the window
            y = i * stride_h
            x = j * stride_w
            ymax = y + slice_height
            xmax = x + slice_width

            # slice the image
            window = image0[y:ymax, x:xmax]

            # ignore slices with too many null pixels
            if np.sum(window == 0) > zero_frac_thresh * window.size:
                continue

            # save the window
            out_path = f'{outdir}/{out_name}_{str(count)}{ext}'
            cv2.imwrite(out_path, window)

            # visualize the window and bounding box
            if verbose:
                bbox = (x, y, slice_width, slice_height)
                window = visualize(window, [bbox])
                cv2.imshow('Window', window)
                cv2.waitKey(1)

            count += 1

    if verbose:
        print('Number of windows:', count)


if __name__ == '__main__':
    # slice the image and visualize the windows
    # slice_im('large_image.tif', 'small_image', '.', verbose=True)
    
    
    annotation_path = "path/to/annotation.xml"
    outdir = "path/to/output/directory"
    process_annotation(annotation_path, outdir)
        