from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException, NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import datetime
import csv

class SeleniumScraper:
    _target_css_selector = 'a.a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd' #'.widget-pane-content-holder .section-layout.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc.siAUzd-neVct-Q3DXx-BvBYQ .V0h1Ob-haAclf > a'
    _next_button_id = 'ppdPk-Ej1Yeb-LgbsSe-tJiF1e'
    _overlay_class = 'qq71r-qrlFte-bF1uUb'
    _links = []
    _data_dir = os.path.dirname(os.path.abspath(__file__))
    _default_filename = 'links.txt'
    _maps_url_prefix = 'https://www.google.com/maps/search/a/@'
    _latitude = -1.3288194
    _longitude = 36.8859888
    _zoom = 15

    def __init__(self) -> None:
        self.url = f'{SeleniumScraper._maps_url_prefix}{self.location},{SeleniumScraper._zoom}z?authuser=0'

    def __repr__(self) -> str:
        return f'SeleniumScraper({self.url})'

    def __str__(self) -> str:
        return self.__repr__()

    @classmethod
    def fromLocation(cls, location):
        '''Returns an instance for the given location
        
        location must be a comma-delimited string of latitude and longitude
        
        Returns an instance of SeleniumScraper'''
        instance = cls()
        instance.location = location
        return instance

    @property
    def location(self):
        return f'{self._latitude},{self._longitude}'

    @location.setter
    def location(self, location):
        '''Sets the location
        
        location must be a comma-delimited string of latitude and longitude'''
        latlng = location.split(',')
        if len(latlng) != 2:
            raise InvalidArgumentException('location must be a comma-delimited string of latitude and longitude')
        self._latitude = latlng[0].strip()
        self._longitude = latlng[1].strip()
        self.url = f'{SeleniumScraper._maps_url_prefix}{self._latitude},{self._longitude},{SeleniumScraper._zoom}z?authuser=0'

    @property
    def target_css_selector(self):
        return self._target_css_selector

    @target_css_selector.setter
    def target_css_selector(self, selector):
        self._target_css_selector = selector

    @property
    def next_button_id(self):
        return self._next_button_id

    @next_button_id.setter
    def next_button_id(self, id):
        self._next_button_id = id

    @property
    def overlay_class(self):
        return self._overlay_class

    @overlay_class.setter
    def overlay_class(self, overlay_class):
        self._overlay_class = overlay_class

    @property
    def links(self):
        return self._links

    @links.setter
    def links(self, links):
        self._links = links

    @property
    def data_dir(self):
        return self._data_dir

    @data_dir.setter
    def data_dir(self, dir):
        self._data_dir = dir

    @property
    def default_filename(self):
        return self._default_filename

    @default_filename.setter
    def default_filename(self, filename):
        self._default_filename = filename

    def scrape(self, search_term, filename=None, dirname=None, spatialize=True, process_output=False) -> str:
        '''
        Using a context manager to run the selenium webdriver ensures better use of memory
        and other system resources. The with keyword allows us to easy use a context manager
        in Python.

        Running the Chrome webdriver requires an extra chrome executable to be downloaded 
        and added to your PATH.

        You can download the chromedriver that is compatible with your version of chrome browser from 
        https://chromedriver.storage.googleapis.com/index.html

        For directions on how to add chromedriver to your PATH, go to 
        https://www.selenium.dev/documentation/en/webdriver/driver_requirements/#adding-executables-to-your-path

        url = "https://www.google.com/maps/search/Companies/@-1.3288194,36.8859888,15z?authuser=0"
        target_css_selector = '.widget-pane-content-holder .section-layout.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc.siAUzd-neVct-Q3DXx-BvBYQ .V0h1Ob-haAclf > a'
        '''
        with webdriver.Chrome() as driver:
            driver.maximize_window()
            # scrape the links
            self._build_links(driver, search_term)
            # write the list of links to a file
            filename = filename or self.default_filename
            written_file = self._write_links_to_file(filename=filename, dirname=dirname, spatialize=spatialize)
            if process_output:
                driver.quit()
                self.process_file(written_file, overwrite_output_file=True)
                return f'Scraped links processed and written to the file at {written_file}'
            return f'Scraped links written to the file at {written_file}'

    def _build_links(self, driver, search_term):
        '''Populates the list of links with GoogleMap links based on the provided url and target_css_selector'''
        # be sure to start with an empty list of links
        self.links = []
        # initializes the wait object for later use
        wait = WebDriverWait(driver, 10)
        # open the url in browser
        driver.get(self.url)
        wait.until(EC.presence_of_element_located((By.NAME, 'q'))).send_keys(f'{Keys.BACK_SPACE}{search_term}{Keys.RETURN}')
        # wait.until(EC.invisibility_of_element((By.CSS_SELECTOR, '.loading .sbcb_a::after')))
        wait.until(EC.url_contains('data='))
        try:
            while True:
                for elem in driver.find_elements_by_css_selector(self.target_css_selector):
                    # retrieve and add each link to the list of links
                    self.links.append(elem.get_attribute('href'))
                # wait until the transparent overlay is invisible
                wait.until(EC.invisibility_of_element((By.CLASS_NAME, self.overlay_class)))
                # wait until the next button is clickable, then click it
                wait.until(EC.element_to_be_clickable((By.ID, self.next_button_id))).click()
        except TimeoutException as e:
            pass
        except ElementClickInterceptedException as e:
            print(f'An overlay prevented a click on the next button.\nYou may want to use a different overlay_class.')
        except Exception as e:
            print(f'An exception was raised while scraping. {e}')
            raise RuntimeError

    def _write_links_to_file(self, filename='links.txt', dirname=None, spatialize=True):
        '''Writes the list of links to the specified filename.

        dirname argument allows for the use of a different directory.
        use_datetime argument controls whether datetime information is added to filename.

        Returns the path to the file that was written.'''
        # write to the data directory, by default
        file_name = os.path.join(self.data_dir, filename)
        # write to specified directory, if it is valid
        if dirname != None and os.path.exists(dirname) and os.path.isdir(dirname):
            file_name = os.path.join(dirname, filename)
        # append datetime to the filename, if spatialize
        if spatialize:
            file_name = SeleniumScraper.spatialize_filename(file_name)
        # open file in write mode
        with open(file_name, 'w') as f:
            for link in self.links:
                # write each link on a separate line in the file
                f.write(link)
                f.write('\n')
        # returns the link to the file that was written
        return file_name

    def process_file(self, filename, overwrite_output_file=False):
        '''Processes the links in filename and optionally overwrites
        the existing output file.
        '''
        if not os.path.isfile(filename):
            raise FileNotFoundError(f'{filename} does not exist')

        fileparts = os.path.splitext(filename)
        if(os.path.isfile(f'{fileparts[0]}.csv')) and not overwrite_output_file:
            raise FileExistsError(f'{filename} exists already. Use overwrite_output_file option to overwrite it.')

        output_filename = f'{fileparts[0]}.csv' 
        
        with open(filename, 'r') as f:
            with open(output_filename, 'w') as w:
                fields = ["name", "description", "industry", "rating", "reviews", "address", "website", "phone", "plus_code"]
                csv_writer = csv.DictWriter(w, fieldnames=fields, delimiter=',')
                csv_writer.writeheader()
                for line in f:
                    data = self._process_link(line.strip())
                    csv_writer.writerow(data)

    def _process_link(self, link) -> dict:
        '''Processes link

        Scrapes the following information from the link, if available:
            - name
            - description
            - industry
            - rating
            - reviews
            - address
            - website
            - phone
            - plus_code
        '''
        class_widget = 'Yr7JMd-pane.Yr7JMd-pane-visible'
        selectors = { 
            "name": f'.{class_widget} .x3AX1-LfntMc-header-title-title.gm2-headline-5 span:first-of-type',
            "description": f'.{class_widget} .x3AX1-LfntMc-header-title-VdSJob span:first-of-type',
            "rating": f'.{class_widget} .OAO0-ZEhYpd-vJ7A6b.OAO0-ZEhYpd-vJ7A6b-qnnXGd .aMPvhf-fI6EEc-KVuj8d',
            "address": f'.{class_widget} .RcCsl.dqIYcf-RWgCYc-text.w4vB1d.C9yzub-TSZdd-on-hover-YuD1xf.AG25L [data-item-id="address"] .AeaXub .rogA2c .QSFF4-text.gm2-body-2',
            "website": f'.{class_widget} .RcCsl.dqIYcf-RWgCYc-text.w4vB1d.C9yzub-TSZdd-on-hover-YuD1xf.AG25L [data-item-id="authority"] .AeaXub .rogA2c .QSFF4-text.gm2-body-2',
            "phone": f'.{class_widget} .RcCsl.dqIYcf-RWgCYc-text.w4vB1d.C9yzub-TSZdd-on-hover-YuD1xf.AG25L [data-item-id*="phone:tel:"] .AeaXub .rogA2c .QSFF4-text.gm2-body-2',
            "plus_code": f'.{class_widget} .RcCsl.dqIYcf-RWgCYc-text.w4vB1d.C9yzub-TSZdd-on-hover-YuD1xf.AG25L [data-item-id="oloc"] .AeaXub .rogA2c .QSFF4-text.gm2-body-2'
        }

        with webdriver.Chrome() as driver:
            driver.maximize_window()
            wait = WebDriverWait(driver, 10)
            driver.get(link)
            wait.until(EC.url_contains('data='))
            fields = ("name", "description", "rating", "address", "website", "phone", "plus_code")
            data = dict()
            for field in fields:
                try:
                    data[field] = ''
                    elem = driver.find_element(By.CSS_SELECTOR, selectors[field])
                    if not elem:
                        continue
                    data[field] = elem.text
                except NoSuchElementException as e:
                    continue
            return data

    @staticmethod
    def spatialize_filename(file_name):
        timestring = f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
        return f'{os.path.splitext(file_name)[0]}-{timestring}{os.path.splitext(file_name)[1]}'

if __name__ == '__main__':
    pass