from requests_html import HTMLSession, HTML

# from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options

import undetected_chromedriver as uc
# from undetected_chromedriver.options import ChromeOptions

import time, os, cv2
import numpy as np
import random

def mask_imgs(path_to_folder='No_person_converted_to_jpg', num_rand_imgs=3):

    # choose random imgs
    list_img_path = os.listdir(path_to_folder)
    list_of_test_img_path = []
    for idx in range(num_rand_imgs):
        idx = random.randint(0, len(list_img_path))
        item = list_img_path[idx]
        list_of_test_img_path.append(item)

    # get clothssegmentation
    dr = uc.Chrome()
    url = 'https://clothssegmentation.herokuapp.com/'
    dr.get(url)
    time.sleep(2)
    # find element that loads img
    drag_drop = dr.find_element(by=By.XPATH, value="//input[contains(@accept, '.jpg')]")
    time.sleep(1)

    # load original img, download mask, make background blue
    for img_name in list_of_test_img_path:
        # path of the original img
        path_to_im = path_to_folder + '/' + img_name
        # load img to site
        drag_drop.send_keys(os.path.abspath(path_to_im))
        time.sleep(5)

        # try grab mask from site
        count = 0
        while True:
            count += 1
            time.sleep(1)
            try:
                mask = dr.find_element(by=By.XPATH, value="//div[div[text() = 'Mask']]//img")
                break
            except:
                if count>15:
                    print("Can't find mask image by XPath = //div[div[text() = 'Mask']]//img\nWaited 15 s")
                    return

        # get mask
        s = HTMLSession()
        r = s.get(str(mask.get_attribute('src'))).content

        # read mask and  orig image
        mask = np.asarray(bytearray(r), dtype="uint8")
        mask = cv2.imdecode(mask, cv2.IMREAD_GRAYSCALE)
        img = cv2.imread(path_to_im)

        # paths to save mask and final version of image
        new_path_massk = f"masked_imgs/{img_name}_mask.jpg"
        new_path_img = f'masked_imgs/{img_name}_masked_img.jpg'
        cv2.imwrite(new_path_massk, mask)
        # make mask BINARY
        m, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)
        # image to make background of image 0,0,0
        mask_3d = np.stack((mask, mask, mask), axis=2)
        # cv2.imwrite('mask3D.jpeg', mask_3d)
        # cv2.imwrite('mask1D.jpeg', mask)

        # make background of image 0,0,0
        image = cv2.bitwise_and(img, mask_3d, mask=mask)
        # cv2.imwrite('image.jpeg', image)

        # create full blue image
        c = np.full(img.shape[:2], 100, dtype='uint8')
        b = np.full(img.shape[:2], 149, dtype='uint8')
        a = np.full(img.shape[:2], 237, dtype='uint8')
        blue_arr = np.stack((a, b, c), axis=2)

        # invert mask
        mask = cv2.bitwise_not(mask)
        # cv2.imwrite('mask2D_2.jpeg', mask)
        # cv2.imwrite('blue_arr.jpeg', blue_arr)

        # create image where background blue and the cloth 0,0,0
        img_masked = cv2.bitwise_or(blue_arr, image, mask=mask)

        # combine blue background and original cloth
        img_masked = cv2.bitwise_or(img_masked, image)
        cv2.imwrite(new_path_img, img_masked)




if __name__=='__main__':
    mask_imgs()

