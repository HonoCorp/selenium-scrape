import os
import optparse
from src.scraper import SeleniumScraper

parser = None

def configure_parser():
    global parser

    parser = optparse.OptionParser()

    help = '''Usage:
    %prog [options] filename

    Process the specified file and store 
    the output in a csv file with same name.
    '''

    parser.set_usage(help)

    parser.add_option(
        '-d',
        '--directory',
        help = 'Data directory',
        dest = 'directory',
        default = '',
        type = 'string',
        action = 'store'
    )

    parser.add_option(
        '-a',
        '--all-data',
        help = 'Whether to process all files in the data directory',
        dest = 'all_data',
        default = False,
        action = 'store'
    )

    parser.add_option(
        '-f',
        '--force',
        help = 'Whether to overwrite the output file',
        dest = 'overwrite',
        default = False,
        action = 'store'
    )

def read_cmd() -> tuple:
    global parser
    (options, arguments) = parser.parse_args()
    try:
        assert len(arguments) == 1
        return (options, arguments)
    except:
        parser.print_help()
        raise

def main():
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(ROOT_DIR, 'data')
    configure_parser()

    try:
        (options, arguments) = read_cmd()
    except:
        return

    filename = arguments[0]
    if not os.path.isfile(filename):
        raise FileNotFoundError(f'{filename} is not a valid file')

    if options.directory != '' and os.path.isdir(options.directory):
        DATA_DIR = options.directory

    s = SeleniumScraper()
    s.process_file(filename, overwrite_output_file=options.overwrite)

    if options.all_data:
        pass

if __name__ == '__main__':
    main()