from requests_html import HTMLSession, HTML

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import undetected_chromedriver as uc
from undetected_chromedriver.options import ChromeOptions
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

from time import sleep
from pathlib import Path

import io
from PIL import Image

from collections import Counter


def scrape_images(url, headless=False):
    # saves the images in particular folders

    """
    :param url: intended to be https://www.ralphlauren.com/men-clothing-sweaters
    :param headless: browser mode
    :return:

    """
    try:

        chrome_options = ChromeOptions()
        chrome_options.headless = headless
        print('chrome_options', chrome_options.arguments)
        dr = uc.Chrome(options=chrome_options)

    except:
        print('setup error, check internet')
        return
    sleep(1)
    dr.get(url)
    sleep(20)  # TODO: make optimal

    # Xpath selectors
    # div that contains all Polo Ralph Lauren
    all_polo_XPath = "//div[div[text() = 'Polo Ralph Lauren']]"
    # picture element with links to img
    imgsXPath = all_polo_XPath + "//div[contains(@class, 'product-image ')]//picture[@class='rlc-picture']"
    # [View more] button
    load_more_XPath = "(//a[contains(@class,  'more-button button inverse')])[1]"

    # how many times to press load more b
    amount_items = 133
    loads_by_button = 30
    # add '+ 1' for safety
    press_b = int(amount_items / loads_by_button // 1 + 1)  # TODO: make adaptive (read amount number froom page)
    exists = True
    count = 0
    count_prev = 0
    time_to_wait_load_more: int = 8
    # load all imgs
    while exists:
        if count >= press_b:
            break
        try:
            # click load more and wait
            e = dr.find_element(by=By.XPATH, value=load_more_XPath)
            e.click()
            count += 1
            print(f'Pressed [View more] button {count} times')

            sleep(time_to_wait_load_more)

        except:
            # if click not worked = quit
            if count_prev == count:
                print(
                    f'cant find elemen [View more], XPath {load_more_XPath}\nalready  pressed {count} times\n'
                    f'This can be caused by: \n'
                    f'slow internet -> increase time_to_wait_load_more in line 59 \n'
                    f'yor blocked by site, try loading url in selenium, refresh, solve captcha, try again. Or use '
                    f'your phone internet \n'
                )
                dr.quit()
                return
            count_prev = count
    # select all elements with imgs
    list_webelements = dr.find_elements(by=By.XPATH, value=imgsXPath)

    # use requests for faster get()
    s = HTMLSession()
    print(f'Found {len(list_webelements)} items\nStarting to load')
    # count duplicates in items names
    counter = Counter()
    count_iters = 0

    # XPath to bagged images with person where img with person is the same as img with no person
    bagged_img_XPath = "((//div[div[text() = 'Polo Ralph Lauren']]//div[contains(@class, 'product-image ')]//picture[contains(@aria-label, '{}')])[2]//source)[1]"


    # links to imgs look like this
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_lifestyle?$plpDeskRF$          no person main_page small
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_lifestyle?$rl_df_pdp_5_7_lif$  no person item page small
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_lifestyle?$rl_df_zoom_lif$     no person item page big
    #
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_alternate10?$rl_df_pdp_5_7_a10$    person_1 item page small
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_alternate10?$rl_df_zoom_a10$       person_1 item page big
    #
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_alternate1?$rl_df_pdp_5_7$         person_2 item page small
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_alternate1?$rl_df_zoom$            person_2 item page big
    #
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_alternate3?$rl_df_pdp_5_7$         etc
    #
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_alternate4?$rl_df_pdp_5_7$

    # if we can get only 1 link of item with particular color we can get all imgs of that item with the color


    # iterate over elements, load images by get(), save in separate folders
    for elemet in list_webelements:
        count_iters += 1
        print(f'iter №{count_iters}')

        title = elemet.get_attribute('aria-label')
        counter[str(title)] += 1

        # load inner HTML of element
        e_html = HTML(html=elemet.get_attribute('innerHTML'))

        # load element with No person
        attrs = e_html.find('img')[0].attrs
        link = attrs['src']
        print(f'Name {title}')
        print(link)
        # get image data
        response = s.get(link).html.raw_html
        img = io.BytesIO(response)
        img = Image.open(img)
        if counter[str(title)] == 1:
            num_duplicate = ''
        else:
            num_duplicate = str(counter[str(title)])
        name = str(title) + '_' + num_duplicate
        path = Path(f'No_person/{name}.jpeg')
        # save image
        img.save(fp=path, format='jpeg')

        # load element With Person
        # check if link to img with person is the same as img with no person
        attrs = e_html.find('source')[0].attrs
        link = attrs['srcset']
        if not 'alternate' in link:
            elemet = dr.find_element(by=By.XPATH, value=bagged_img_XPath.format(str(title)))
            link = str(elemet.get_attribute('srcset'))

        print(link)
        response = s.get(link).html.raw_html
        img = io.BytesIO(response)
        img = Image.open(img)
        path = Path(f'Person/{name}_person.jpeg')
        img.save(fp=path, format='jpeg')


    dr.quit()


import os, cv2
def convert_to_jpg(path_folder):
    if not os.path.isdir(path_folder):
        print(f'os.path.isdir(path_to_folder)={os.path.isdir(path_folder)}')
        return
    path_to_new_folder = path_folder + '_converted_to_jpg/'
    if os.path.isdir(path_to_new_folder):
        print(f"remove dir {(path_folder + '_converted')}")
        return

    list_of_imgs_paths = os.listdir(path_folder)
    os.mkdir(path_to_new_folder)
    for path_im in list_of_imgs_paths:
        path_old_im = path_folder +'/'+path_im
        img = cv2.imread(path_old_im)

        idx_of_dot = path_im[::-1].find('.') + 1
        new_path = path_to_new_folder + path_im[:-idx_of_dot]+ '.jpg'

        print(new_path)
        cv2.imwrite(
            new_path,
            img, [cv2.IMWRITE_JPEG_PROGRESSIVE])

import numpy as np


def scrape_images_extra(url, headless=False):
    # saves the images in particular folders

    """
    :param url: intended to be https://www.ralphlauren.com/men-clothing-sweaters
    :param headless: browser mode
    :return:

    """
    try:
        chrome_options = ChromeOptions()
        chrome_options.headless = headless
        print('chrome_options', chrome_options.arguments)
        dr = uc.Chrome(options=chrome_options)
    except:
        print('setup error, check internet')
        return

    sleep(1)
    dr.get(url)
    sleep(5)  # TODO: make optimal

    # Xpath selectors
    # div that contains all Polo Ralph Lauren
    all_polo_XPath = "//div[div[text() = 'Polo Ralph Lauren']]"
    # picture element with links to img
    div_item = all_polo_XPath + "//div[@class='product-tile ']"
    imgsXPath = "//div[contains(@class, 'product-image ')]//picture[@class='rlc-picture']"
    # [View more] button
    load_more_XPath = "(//a[contains(@class,  'more-button button inverse')])[1]"

    # how many times to press load more b
    amount_items = 140
    loads_by_button = 30
    # add '+ 1' for safety
    press_b = int(amount_items / loads_by_button // 1 + 1)  # TODO: make adaptive (read amount number froom page)
    exists = True
    count = 0
    count_prev = 0
    time_to_wait_load_more: int = 10
    # load all imgs
    while exists:
        if count >= press_b:
            break
        try:
            # click load more and wait
            e = dr.find_element(by=By.XPATH, value=load_more_XPath)
            e.click()
            count += 1
            print(f'Pressed [View more] button {count} times')

            sleep(time_to_wait_load_more)

        except:
            # if click not worked = quit
            if count_prev == count:
                print(
                    f'cant find elemen [View more], XPath {load_more_XPath}\nalready  pressed {count} times\n'
                    f'This can be caused by: \n'
                    f'slow internet -> increase time_to_wait_load_more in line 59 \n'
                    f'yor blocked by site, try loading url in selenium, refresh, solve captcha, try again. Or use '
                    f'your phone internet \n'
                )
                dr.quit()
                return
            count_prev = count
    # select all elements with imgs
    list_webelements = dr.find_elements(by=By.XPATH, value=div_item)

    # use requests for faster get()
    s = HTMLSession()
    print(f'Found {len(list_webelements)} items\nStarting to load')
    # count duplicates in items names
    counter = Counter()
    count_iters = 0


    # links to imgs look like this
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_lifestyle?$plpDeskRF$          no person main_page small
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_lifestyle?$rl_df_pdp_5_7_lif$  no person item page small
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_lifestyle?$rl_df_zoom_lif$     no person item page big
    #
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_alternate10?$rl_df_pdp_5_7_a10$    person_1 item page small
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_alternate10?$rl_df_zoom_a10$       person_1 item page big
    #
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_alternate1?$rl_df_pdp_5_7$         person_2 item page small
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_alternate1?$rl_df_zoom$            person_2 item page big
    #
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_alternate3?$rl_df_pdp_5_7$         etc
    #
    # https://www.rlmedia.io/is/image/PoloGSI/s7-1355988_alternate4?$rl_df_pdp_5_7$

    # if we can get only 1 link of item with particular color we can get all imgs of that item with the color


    # dict to store info:
    # item_name - str name
    # color1 - tuple bgr (12,255,121) OR 'no_color' if only 1 color
    # {'item_name' :
    #               {'(12,255,121)' :
    #                           {'person' : ['image_name_1.jpeg', 'image_name_2.jpeg']
    #                            'no_person' : 'image_name_3.jpeg'
    #                            }
    #               {'(122,215,133)' :
    #                           }
    # 'item_name' :
    # }
    # IF DUPLICATE item_names is on the site, then item_name, item_name_2, item_name_3



    dict_store_info = dict()
    links_to_items_with_to_many_colors = []
    # iterate over elements, load images by get(), save in separate folders
    for elemet in list_webelements:
        count_iters += 1
        print(f'iter №{count_iters}')

        # check for duplicates
        title = str(elemet.get_attribute('data-pname'))
        counter[title] += 1
        if counter[title] == 1:
            num_duplicate = ''
        else:
            num_duplicate = '_' + str(counter[title])

        name = title+num_duplicate
        print(name)
        dict_store_info[name] = {}

        # load inner HTML of element
        e_html = HTML(html=elemet.get_attribute('innerHTML'))

        # css to find li with imgs
        li_imgs = "div[class=swatches-cont] li img"
        # css to find find if there is other colors
        li_more_colors = "div[class=swatches-cont] li[class=more-colors-count]"

        # link endings
        link_endings = [
            '_lifestyle?$rl_df_zoom_lif$',
            '_alternate10?$rl_df_zoom_a10$',
            '_alternate1?$rl_df_zoom$',
            '_alternate3?$rl_df_zoom$',
            '_alternate4?$rl_df_zoom$',
        ]
        # if only 1 color then download two images
        if len(e_html.find(li_imgs))==0:
            picture_attrs = e_html.find('img')[0].attrs

            # get all 5 possible images for item (3 with person, 1 with zoomed person, 1 just clothes)
            link = str(picture_attrs['src'])
            color = 'no_color'
            # add color to item_name
            dict_store_info[name][color] = {}

            idx_in_link = link.find('_')
            link_start = link[0:idx_in_link]
            # get and save img with no person
            r = s.get(url=link_start + link_endings[0]).html.raw_html
            img = io.BytesIO(r)
            img = Image.open(img)
            name_to_save = f'No_person/{name}_{1}_1.jpeg'
            print(name_to_save)
            path = Path(name_to_save)
            img.save(fp=path, format='jpeg')

            # add no_person img to color
            dict_store_info[name][color]['no_person'] = name_to_save
            # init person with []
            dict_store_info[name][color]['person'] = []
            for num, end in enumerate(link_endings[1:]):
                r = s.get(url=link_start+end)
                if 'Unable to find image' in r.text:
                    print(link_start+end, 'Not found by site')
                    continue
                r = r.html.raw_html


                img = io.BytesIO(r)
                img = Image.open(img)
                name_to_save = f'Person/{name}_{1}_{num}_person.jpeg'
                print(name_to_save)
                path = Path(name_to_save)
                img.save(fp=path, format='jpeg')
                # add person img to color
                dict_store_info[name][color]['person'].append(name_to_save)


        # if all colors on page then iterate over them
        elif len(e_html.find(li_more_colors))==0:
            for num_, img_e in enumerate(e_html.find(li_imgs)):
                # get color of cloth img
                try:
                    color_image_link = img_e.attrs['src']
                except:
                    None
                try:
                    color_image_link = img_e.attrs['data-yo-src']
                except:
                    None
                if not 'http' in color_image_link:
                    color_image_link = img_e.attrs['src']
                # print(color_image_link)
                r = s.get(color_image_link).content
                color_img = np.asarray(bytearray(r), dtype="uint8")
                color_img = cv2.imdecode(color_img, cv2.IMREAD_COLOR)
                # calculate median of small image of a color
                b = np.median(color_img.T[0].flatten())
                g = np.median(color_img.T[1].flatten())
                r = np.median(color_img.T[2].flatten())
                color = (int(b),int(g),int(r))
                # add color
                dict_store_info[name][color] = {}

                # make start of the link from <img>.attrs
                link = img_e.attrs['data-thumb']
                idx_start = link.find('https')
                idx_end = link.find('$"')
                link = link[idx_start:idx_end+1]
                idx_end = link.find('_')
                link_start = 'https://' + link[idx_start:idx_end]
                # get first img no_person
                r = s.get(url=link_start + link_endings[0])

                if 'Unable to find image' in r.text:
                    print(link_start+end, 'Not found by site')
                    continue
                r = r.html.raw_html

                img = io.BytesIO(r)
                img = Image.open(img)
                name_to_save = f'No_person/{name}_{num_}_{1}.jpeg'
                print(name_to_save)
                path = Path(name_to_save)
                img.save(fp=path, format='jpeg')

                # add no_person img to color
                dict_store_info[name][color]['no_person'] = name_to_save
                # init person with []
                dict_store_info[name][color]['person'] = []
                # get all person imgs
                for num, end in enumerate(link_endings[1:]):
                    # print(link_start + end)
                    link_ = link_start + end
                    r = s.get(url=link_)

                    if 'Unable to find image' in r.text:
                        print(link_, 'Not found by site')
                        continue
                    r = r.html.raw_html
                    # print(link_)
                    img = io.BytesIO(r)
                    img = Image.open(img)
                    name_to_save = f'Person/{name}_{num_}_{num}_person.jpeg'
                    print(name_to_save)
                    path = Path(name_to_save)
                    img.save(fp=path, format='jpeg')
                    # add person img to color
                    dict_store_info[name][color]['person'].append(name_to_save)
        else:
            # if not all colors are on page
            link_to_item_page ='https://www.ralphlauren.com' + str(e_html.find('a')[0].attrs['href'])
            links_to_items_with_to_many_colors.append([link_to_item_page, name])
    print(links_to_items_with_to_many_colors)
    for item in links_to_items_with_to_many_colors:
        name = item[1]
        link = str(item[0])
        print(name)
        print(link)
        dr.get(link)
        sleep(2)
        dr.maximize_window()
        sleep(2)
        elemets_img = dr.find_elements(by=By.XPATH, value="//*[@id='product-content']//div[@class='value']//img")
        for num_, element in enumerate(elemets_img):

            # get color of cloth img
            color_image_link = str(element.get_attribute('src'))
            r = s.get(color_image_link).content
            color_img = np.asarray(bytearray(r), dtype="uint8")
            color_img = cv2.imdecode(color_img, cv2.IMREAD_COLOR)
            # calculate median of small image of a color
            b = np.median(color_img.T[0].flatten())
            g = np.median(color_img.T[1].flatten())
            r = np.median(color_img.T[2].flatten())
            color = (int(b), int(g), int(r))
            # add color
            dict_store_info[name][color] = {}

            link_endings = [
                '_lifestyle?$rl_df_zoom_lif$',
                '_alternate10?$rl_df_zoom_a10$',
                '_alternate1?$rl_df_zoom$',
                '_alternate3?$rl_df_zoom$',
                '_alternate4?$rl_df_zoom$',
            ]

            # make start of link
            # link start, second part (+ color_image_link[47:54])
            # is a number which by it self points to every possible image of item in the color
            link_start = 'https://www.rlmedia.io/is/image/PoloGSI/s7-'+ color_image_link[47:54]

            r = s.get(url=link_start + link_endings[0])
            if 'Unable to find image' in r.text:
                print(link_, 'Not found by site')
                continue
            r = r.html.raw_html

            img = io.BytesIO(r)
            img = Image.open(img)
            name_to_save = f'No_person/{name}_{num_}_1.jpeg'
            path = Path(name_to_save)
            img.save(fp=path, format='jpeg')
            print(name_to_save)
            # add no_person img to color
            dict_store_info[name][color]['no_person'] = name_to_save
            # init person with []
            dict_store_info[name][color]['person'] = []

            for num, end in enumerate(link_endings[1:]):
                r = s.get(url=link_start + end)
                if 'Unable to find image' in r.text:
                    print(link_start + end, 'Not found by site')
                    continue
                r = r.html.raw_html

                img = io.BytesIO(r)
                img = Image.open(img)
                name_to_save = f'Person/{name}_{num_}_{num}_person.jpeg'
                print(name_to_save)
                path = Path(name_to_save)
                img.save(fp=path, format='jpeg')
                # add person img to color
                dict_store_info[name][color]['person'].append(name_to_save)


    dr.quit()

    print(dict_store_info)


if __name__ == '__main__':
    url = 'https://www.ralphlauren.com/men-clothing-sweaters'
    # url = 'https://www.google.ru/'
    scrape_images_extra(url=url)
