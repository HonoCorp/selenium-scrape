from src.scraper import SeleniumScraper
import os

def main():
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(ROOT_DIR, 'data')
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR, 0o777)
    SeleniumScraper.data_dir = DATA_DIR

    locations = {
        "mombasa": "-4.043740,39.658871",
        "nairobi": "-1.286389,36.817223",
        "kisumu": "-0.091702,34.767956"
    }

    for location_name, location in locations.items():
        s = SeleniumScraper.fromLocation(location)
        s.default_filename = f'{location_name}.txt'
        message = s.scrape('Company')
        print(message)

if __name__ == '__main__':
    main()
