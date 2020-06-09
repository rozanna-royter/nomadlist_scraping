import os, time
from selenium import webdriver

SCROLL_DOWN_LOOP_COUNT = 5
# def start_driver():
#     driver = webdriver.Chrome("/usr/local/bin/chromedriver")
#     return driver


def get_cities_list(d):
    go_to_url(d, 'https://nomadlist.com')
    time.sleep(5)
    d.find_element_by_xpath("//option[@data-sort='users_been_count']").click()
    time.sleep(5)
    scroll_down(d, SCROLL_DOWN_LOOP_COUNT)
    city_list = []
    city_elements = d.find_elements_by_css_selector("li[data-type='city']")
    for c in city_elements:
        city_list.append(c.get_attribute("data-slug"))
    return city_list


def scroll_down(d, num):
    for i in range(num):
        d.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)


def go_to_url(d, url):
    d.get(url)


def main():
    driver = webdriver.Chrome("/usr/local/bin/chromedriver")
    driver.maximize_window()

    cities_list = get_cities_list(driver)
    print(cities_list)
    print(len(cities_list))

    time.sleep(5)
    driver.quit()


if __name__ == '__main__':
    main()



