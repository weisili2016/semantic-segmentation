# 
# utilities for semantic segmentation
# autonomous golf cart project
# (c) Yongyang Nie, Michael Meng
# ==============================================================================
#

import re
import cv2
import configs as configs
import numpy as np
import os
import scipy.misc
from glob import glob
from collections import namedtuple

Label = namedtuple('Label', [

    'name'        , # The identifier of this label, e.g. 'car', 'person', ... .
                    # We use them to uniquely name a class

    'id'          , # An integer ID that is associated with this label.
                    # The IDs are used to represent the label in ground truth images
                    # An ID of -1 means that this label does not have an ID and thus
                    # is ignored when creating ground truth images (e.g. license plate).
                    # Do not modify these IDs, since exactly these IDs are expected by the
                    # evaluation server.

    'color'       , # The color of this label
    ])


labels = [
    #       name            id      color
    Label('None',         1,     (0, 0, 0)      ),
    Label('Buildings',    6,     (70, 70, 70)   ),
    Label('Fences',       7,     (190, 153, 153)),
    Label('Other',        8,     (0, 0, 0)      ),
    Label('Pedestrians',  11,    (220, 20, 60)  ),
    Label('Poles',        20,    (153, 153, 153)),
    Label('RoadLines',    21,    (128, 64,128)  ),
    Label('Roads',        22,    (128, 64,128)  ),
    Label('Sidewalks',    23,    (70, 130, 180) ),
    Label('Vegetation',   24,    (220, 20, 60)  ),
    Label('Vehicles',     26,    (0, 0, 142)    ),
    Label('Walls',        27,    (0, 0, 70)     ),
    Label('TrafficSigns', 33,    (119, 11, 32)  ),
]


def bc_img(img, s = 1.0, m = 0.0):
    img = img.astype(np.int)
    img = img * s + m
    img[img > 255] = 255
    img[img < 0] = 0
    img = img.astype(np.uint8)
    return img


def prepare_dataset(path):

    inputs = os.listdir(path)
    imgs = os.listdir(path)

    for i in range(len(imgs)):
        imgs[i] = imgs[i][:-11] + "_road" + imgs[i][-11:]

    return inputs, imgs


def load_image(path):

    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (configs.img_width, configs.img_height))
    return img


def convert_rgb_to_class(image):

    outputs = []

    for i in range(len(labels)):

        label = labels[i]

        color = np.array(label[7], dtype=np.uint8)
        # objects found in the frame.
        mask = cv2.inRange(image, color, color)

        # divide each pixel by 255
        mask = np.true_divide(mask, 255)

        if len(outputs) == 0:
            outputs = mask
        else:
            outputs = np.dstack((outputs, mask))

    return outputs


def convert_class_to_rgb(image_labels, threshold=0.05):

    # convert any pixel > threshold to 1
    # convert any pixel < threshold to 0
    # then use bitwise_and

    output = np.zeros((configs.img_height, configs.img_width, 3), dtype=np.uint8)

    for i in range(len(labels)):

        if i != 44:
            split = image_labels[:, :, i]
            split[split > threshold] = 1
            split[split < threshold] = 0
            split[:] *= 255
            split = split.astype(np.uint8)
            color = labels[i][7]

            bg = np.zeros((configs.img_height, configs.img_width, 3), dtype=np.uint8)
            bg[:, :, 0].fill(color[0])
            bg[:, :, 1].fill(color[1])
            bg[:, :, 2].fill(color[2])

            res = cv2.bitwise_and(bg, bg, mask=split)

            # plt.imshow(np.hstack([bg, res]))
            # plt.show()

            output = cv2.addWeighted(output, 1.0, res, 1.0, 0)

    return output


def validation_generator(labels, batch_size):

    batch_images = np.zeros((batch_size, configs.img_height, configs.img_width, 3))
    batch_masks = np.zeros((batch_size, configs.img_height, configs.img_width, 3))

    while 1:

        for index in np.random.permutation(len(labels)):

            label = labels[index]
            image = load_image(configs.data_path + "leftImg8bit/val/" + label[1])
            gt_image = load_image(configs.data_path + "gtFine/val/" + label[2])

            batch_images[index] = image
            batch_masks[index] = gt_image

        yield batch_images, batch_masks



def train_generator(ls, batch_size):

    batch_images = np.zeros((batch_size, configs.img_height, configs.img_width, 3))
    batch_masks = np.zeros((batch_size, configs.img_height, configs.img_width, len(labels)))

    while 1:
        i = 0
        for index in np.random.permutation(len(ls)):

            label = ls[index]
            image = load_image(configs.data_path + label[0])
            gt_image = load_image(configs.data_path + label[1])

            batch_images[i] = image
            batch_masks[i] = convert_rgb_to_class(gt_image)
            i += 1
            if i == batch_size:
                break

        yield batch_images, batch_masks


if __name__ == "__main__":

    img = load_image("./testing_imgs/test.png")
    print(img.shape)
    array = convert_rgb_to_class(img)
    image = convert_class_to_rgb(array)
