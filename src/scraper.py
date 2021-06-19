from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException, NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import datetime

class SeleniumScraper:
    _target_css_selector = '.widget-pane-content-holder .section-layout.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc.siAUzd-neVct-Q3DXx-BvBYQ .V0h1Ob-haAclf > a'
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

    def scrape(self, search_term) -> str:
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
            written_file = self._write_links_to_file(filename=self.default_filename)
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

    def _process_link(self, link):
        '''Processes link

        Scrapes available information from the link:
            - name
            - description
            - address
            - website url
            - phone number
            - plus code

        company_dormain = driver.find_element_by_class_name('u2OlCc')
        address = driver.find_element_by_class_name('rogA2c')
        working_Hours = driver.find_element_by_class_name('LJKBpe-Tswv1b-text')
        contact = driver.find_element_by_class_name('QSFF4-text gm2-body-2')
        rating = driver.find_element_by_class_name('aMPvhf-fI6EEc-KVuj8d')
        reviews = driver.find_element_by_class_name('gm2-button-alt HHrUdb-v3pZbf')
        '''
        pass

    @staticmethod
    def spatialize_filename(file_name):
        timestring = f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
        return f'{os.path.splitext(file_name)[0]}-{timestring}{os.path.splitext(file_name)[1]}'

if __name__ == '__main__':
    pass