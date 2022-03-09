
# import func from first task, it loads number_of_items_on_page * 2 imgs
# one with person and one with out
# IMPORTANT: this funk need clean folders 'Person' and 'No_person'
from scraper import scrape_images
url = 'https://www.ralphlauren.com/men-clothing-sweaters'

# scrap imgs to No_person/ and Person/ folders
scrape_images(url=url)

# This func scraps 212 + 900 imgs in 1440x2000 px rez
# it scraps every color and every corresponding images of person
# it takes 30 or 40 min to do the task
# and prints dict with info about scraped images
# IMPORTANT: this funk need clean folders 'Person' and 'No_person'
from scraper import scrape_images_extra
scrape_images_extra(url)

# converts imgs, loads from No_person/, export to No_person_converted_to_jpg/
from scraper import convert_to_jpg
# convert No_person/ imgs
convert_to_jpg('/home/globolik/.config/inkscape/extensions/first_task/No_person')

# func from second task, masks images using web browser to get mask
from mask_image import mask_imgs

# mask 3 random imgs
mask_imgs()












