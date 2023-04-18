import cv2
import numpy as np


def visualize(im, bboxes):
    '''Draw bounding boxes on the image'''
    for bbox in bboxes:
        x, y, w, h = bbox
        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return im


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
            out_path = outdir + '/' + out_name + '_' + str(count) + ext
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
