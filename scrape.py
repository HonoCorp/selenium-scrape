from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import datetime

links = []

def build_links(driver, url, target_css_selector, next_button_id='ppdPk-Ej1Yeb-LgbsSe-tJiF1e', overlay_class='qq71r-qrlFte-bF1uUb'):
    '''Populates the list of links with GoogleMap links based on the provided url and target_css_selector'''
    global links
    # initializes the wait object for later use
    wait = WebDriverWait(driver, 10)
    # open the url in browser
    driver.get(url)
    try:
        while True:
            for elem in driver.find_elements_by_css_selector(target_css_selector):
                # retrieve and add each link to the list of links
                links.append(elem.get_attribute('href'))
            # wait until the transparent overlay is invisible
            wait.until(EC.invisibility_of_element((By.CLASS_NAME, overlay_class)))
            # wait until the next button is clickable
            wait.until(EC.element_to_be_clickable((By.ID, next_button_id))).click()
    except TimeoutException as e:
        print('Finished scraping...')
    except Exception as e:
        print(f'An exception was raised while scraping. {e}')

def write_links_to_file(filename='links.txt', dirname=None, use_datetime=True):
    '''Writes the list of links to file'''
    global links
    # write to the current working directory, by default
    file_name = os.path.join(os.getcwd(), filename)
    # write to specified directory, if it is valid
    if dirname != None and os.path.exists(dirname) and os.path.isdir(dirname):
        file_name = os.path.join(dirname, filename)
    # append datetime to the filename, if use_datetime
    if use_datetime:        
        timestring = datetime.date.today().strftime("%Y%m%d%H%M%S")
        file_name = f'{os.path.splitext(file_name)[0]}-{timestring}.{os.path.splitext(file_name)[1]}'
    # open file in write mode
    with open(file_name, 'w') as f:
        for link in links:
            # write each link on a separate line in the file
            f.write(link)
            f.write('\n')
    # returns the link to the file that was written
    return file_name

"""
Using a context manager to run the selenium webdriver ensures better use of memory
and other system resources. The with keyword allows us to easy use a context manager
in Python.

Running the Chrome webdriver requires an extra chrome executable to be downloaded 
and added to your PATH.

You can download the chromedriver that is compatible with your version of chrome browser from 
https://chromedriver.storage.googleapis.com/index.html

For directions on how to add chromedriver to your PATH, go to 
https://www.selenium.dev/documentation/en/webdriver/driver_requirements/#adding-executables-to-your-path
"""
with webdriver.Chrome() as driver:
    url ="https://www.google.com/maps/search/Companies/@-1.3288194,36.8859888,15z?authuser=0"
    target_css_selector = '.widget-pane-content-holder .section-layout.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc.siAUzd-neVct-Q3DXx-BvBYQ .V0h1Ob-haAclf > a'
    driver.maximize_window()
    # scrape the links
    build_links(driver, url, target_css_selector)
    # write the list of links to a file
    written_file = write_links_to_file()
    print(f'Scraped links written to the file at {written_file}')

    # TO DO: process each link in the file and scrape the necessary information