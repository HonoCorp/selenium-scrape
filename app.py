from src.scraper import SeleniumScraper
from src.locations import locations, location_choices, location_default
import os
import optparse

parser = None

def configure_parser():
    global parser
    global location_choices
    global location_default   

    parser = optparse.OptionParser()

    help = '''Usage:
    %prog [options] search_term

    Scrape the specified location option for the search_term
    and store the output in a file.
    '''

    parser.set_usage(help)

    parser.add_option(
        '-o',
        '--output',
        help = 'Name of output file',
        dest = 'output_file',
        default = 'links.txt',
        type = 'string',
        action = 'store'
    )

    parser.add_option(
        '-d',
        '--directory',
        help = 'Name of output directory',
        dest = 'directory',
        default = '',
        type = 'string',
        action = 'store'
    )

    parser.add_option(
        '-s',
        '--spatialize-output',
        help = 'Whether to add datetime info to output filename',
        dest = 'spatialize',
        default = True,
        action = 'store'
    )

    parser.add_option(
        '-l',
        '--location',
        help = f'Location to scrape. Valid choices are {location_choices}. Default: {location_default}',
        dest = 'location',
        default = location_default,
        type = 'choice',
        choices = location_choices
    )

def read_cmd() -> tuple:
    global parser
    global location_choices
    (options, arguments) = parser.parse_args()
    try:
        assert len(arguments) == 1
        assert options.location in location_choices
        return (options, arguments)
    except:
        parser.print_help()
        raise

def main():
    global locations
    global location_choices
    global location_default 
    configure_parser()

    try:
        (options, arguments) = read_cmd()
    except:
        return

    search_term = arguments[0]

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(ROOT_DIR, 'data')
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR, 0o777)

    SeleniumScraper.data_dir = DATA_DIR

    message = SeleniumScraper.fromLocation(locations[options.location]).scrape(
        search_term=search_term, 
        filename=options.output_file, 
        dirname=options.directory, 
        spatialize=options.spatialize)
    print(message)

if __name__ == '__main__':
    main()
