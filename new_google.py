import selenium
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import xlsxwriter
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

page_url ="https://www.google.com/maps/search/Companies/@-1.3288194,36.8859888,15z?authuser=0"
driver = webdriver.Chrome(executable_path="C:/Users/Bonke Sam/Downloads/chromedriver_win32 (1)/chromedriver.exe")

driver.set_window_size(1120, 1000)
driver.get(page_url)

company_cards = driver.find_element_by_class_name("a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd")
company_cards.click()

company_dormain = driver.find_element_by_class_name('u2OlCc')
address = driver.find_element_by_class_name('rogA2c')
working_Hours = driver.find_element_by_class_name('LJKBpe-Tswv1b-text')
contact = driver.find_element_by_class_name('QSFF4-text gm2-body-2')
rating = driver.find_element_by_class_name('aMPvhf-fI6EEc-KVuj8d')
reviews = driver.find_element_by_class_name('gm2-button-alt HHrUdb-v3pZbf')

print(company_name)