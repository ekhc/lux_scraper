import pandas as pd
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# 식당 url 얻기
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

res = driver.page_source  # 페이지 소스 가져오기
soup = BeautifulSoup(res, 'html.parser')  # html 파싱하여  가져온다


# frame 변경 메소드
def switch_frame(frame):
    driver.switch_to.default_content()  # frame 초기화
    driver.switch_to.frame(frame)  # frame 변경


df = pd.read_csv("input.csv")
max_li = 100
print(df)


def find_css_element(selector):
    try:
        res = driver.find_element(By.CSS_SELECTOR, selector)
    except NoSuchElementException:
        return None

    return res


def find_css_element_text(selector):
    try:
        res = driver.find_element(By.CSS_SELECTOR, selector).text
    except NoSuchElementException:
        return 'None'

    return res

def find_css_element_href(selector):
    try:
        res = driver.find_element(By.CSS_SELECTOR, selector).get_attribute('href')
    except NoSuchElementException:
        return 'None'

    return res


for i, keyword in enumerate(df['gu'].tolist()):
    # 검색 url 만들기
    naver_map_search_url = f'https://m.map.naver.com/search2/search.naver?query={keyword}%20웨딩플래너'  
    # 검색 url 접속 = 검색하기
    driver.get(naver_map_search_url)
    time.sleep(2)

    sid_dict = dict()
    try:     
        # Get list of wedding planners and data-sid
        li = driver.find_elements(By.CSS_SELECTOR, "._item._lazyImgContainer")
        for _, element in enumerate(li):
            sid = element.get_dom_attribute('data-sid')
            name = element.get_dom_attribute('data-title')
            sid_dict[sid] = name
        print(sid_dict)   
    except Exception as e:
        print(f"{type(e).__name__}: e")
    finally:
        driver.close()

    vendor_dict = dict()
    for k in sid_dict:
        naver_map_vendor_url = f"https://m.place.naver.com/place/{k}"
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(naver_map_vendor_url)
        vendor_dict[k] = {
            'name': find_css_element_text('.Fc1rA'),
            'num_customer_review': find_css_element_text('#app-root > div > div > div > div.place_section.OP4V8 > div.zD5Nm > div.dAsGb > span:nth-child(1) > a > em'),
            'num_blog_review': find_css_element_text('#app-root > div > div > div > div.place_section.OP4V8 > div.zD5Nm > div.dAsGb > span:nth-child(2) > a > em'),
            'address': find_css_element_text('#app-root > div > div > div > div:nth-child(6) > div > div.place_section.no_margin.vKA6F > div > div > div.O8qbU.tQY7D > div > a > span.LDgIH'),
            'phone_num': find_css_element_text('#app-root > div > div > div > div:nth-child(6) > div > div.place_section.no_margin.vKA6F > div > div > div.O8qbU.nbXkr > div > span.xlx7Q'),
            'website': find_css_element_text('#app-root > div > div > div > div:nth-child(6) > div > div.place_section.no_margin.vKA6F > div > div > div.O8qbU.yIPfO > div > div.jO09N > a'),
            'instagram': find_css_element_href('#app-root > div > div > div > div:nth-child(6) > div > div.place_section.no_margin.vKA6F > div > div > div.O8qbU.yIPfO > div > div.Cycl8 > span > a')
        }
        print(vendor_dict[k])
        driver.close()