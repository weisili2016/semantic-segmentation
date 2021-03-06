# -----------------------------------
# visualization.py, visualize road segmentation
# on Udacity testing data
# (c) Neil Nie, 2017
# All Rights Reserved.
# -----------------------------------

import models.enet_naive_upsampling.model as enet
import utils
import configs
import time
import cv2
import pandas as pd
import numpy as np
from PIL import Image
import pygame

# init pygame
pygame.init()
size = (configs.img_width, configs.img_height)
pygame.display.set_caption("road segmentation")
screen = pygame.display.set_mode(size, pygame.DOUBLEBUF)
screen.set_alpha(None)

camera_surface = pygame.surface.Surface((configs.img_width, configs.img_height), 0, 24).convert()
clock = pygame.time.Clock()


def test_video_stream():

    # init model
    m = enet.build(len(utils.labels), configs.img_height, configs.img_width)
    # m = icnet.build(3, 512, 512)
    m.load_weights("./weights/enet-c-v1-3.h5")
    m.summary()

    # load testing data
    label_path = configs.data_path + "extra_labels.csv"
    df_truth = pd.read_csv(label_path).values

    print("loaded dataset", len(df_truth))

    for i in range(len(df_truth)):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break

        path = configs.test_dataset + df_truth[i][0]

        image = Image.open(path)
        image = np.array(image, dtype=np.uint8)
        input = cv2.resize(image, (configs.img_width, configs.img_height))

        start = time.time()

        output = m.predict(np.array([input]))[0]
        im_mask = utils.convert_class_to_rgb(output, 0.02)

        end = time.time()
        print(1 / (end - start))

        im_mask = cv2.resize(im_mask, (configs.img_width, configs.img_height))
        image = cv2.resize(image, (configs.img_width, configs.img_height))
        img_pred = cv2.addWeighted(im_mask, 0.8, image, 0.8, 0)

        # show it in pygame
        # -----------------
        pygame.surfarray.blit_array(camera_surface, img_pred.swapaxes(0, 1))
        screen.blit(camera_surface, (0, 0))
        pygame.display.flip()


if __name__ == '__main__':

    test_video_stream()



