import json
import threading
import time
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from base_driver import Driver

csv_path = "./item_status.csv"
item_url_list_file_path = './items_url.json'


def get_items_div(home_driver):
    items_div = WebDriverWait(home_driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "/html/body/div[1]/div/main/div/div/div[3]/div/div/div/div[3]/div[3]/div[2]/div/div/div")))
    return items_div


def prepare_items_url_list():
    home_driver = Driver(url="https://opensea.io/collection/catalog-lu-store").driver
    url_list = []
    num = 0
    while set(url_list).__len__() < 2100:
        jscode = 'window.scrollTo({},{})'.format(num * 862, 862 * num)
        home_driver.execute_script(jscode)
        time.sleep(5)
        for i in get_items_div(home_driver):
            item_a = i.find_element(By.TAG_NAME, "a")
            href = item_a.get_attribute('href')
            url_list.append(href)
        print(set(url_list).__len__())
        num += 1
    with open('./items_url.json', "w") as f:
        json.dump(list(set(url_list)), fp=f)
    home_driver.close()
    return url_list


def upload_execl(url_list):
    column_dict = {"NO": [], "URL": [], "status": []}
    column_list = ['NO', 'URL', "status"]
    num = 1
    for url in url_list[:2]:
        if not url:
            continue
        status = []
        column_dict['URL'].append(url)
        column_dict['NO'].append(num)
        item_driver = Driver(url=url).driver
        try:
            refresh_metedata = item_driver.find_element(By.XPATH,
                                                        value="/html/body/div[1]/div/main/div/div/div/div[1]/div/div[1]/div[2]/section[1]/div/div[2]/div/button[1]/div/i")
            refresh_metedata.click()
            status.append('Clicked')
            text = item_driver.find_element(By.XPATH, value="/html/body/div[1]/div[2]/div/div")
            inner_html = text.get_attribute("innerHTML")
            if "We\'ve queued this item for an update" in inner_html:
                status.append("Queued")
            else:
                status.append("Error")
            item_driver.quit()
            column_dict['status'].append(str(status))

        except Exception as e:
            status.append('Error')
        num += 1
    print(column_dict)
    df = pd.DataFrame(column_dict)
    df = df[column_list]
    return df
    # df.to_csv('./item_status.csv', index=False)


# def post_theadings(item_url_list):
#     thread_pool = []
#     for i in range(0, 50):
#         th = threading.Thread(target=upload_execl, args=item_url_list)
#         thread_pool.append(th)
#     for thread in thread_pool:
#         thread.start()


if __name__ == '__main__':
    # prepare_items_url_list()
    with open(item_url_list_file_path) as f:
        item_url_list = json.load(f)
    upload_execl(url_list=item_url_list)
