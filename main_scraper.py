"""Full process of scraping city names and user info wrapped in one place"""
import scrape_cities
import get_users
import scrape_users
import argparse


def cities(from_scratch=0, scroll_down=60):
    print("Scraping cities...")
    scrape_cities.run(from_scratch, scroll_down)


def users():
    print("Getting all usernames...")
    get_users.run()


def info(magic_link='', code='', from_scratch=0, chunk_size=10):
    print("Scraping user info...")
    scrape_users.run(magic_link, code, from_scratch, chunk_size)


def all():
    cities()
    users()
    info()


def main():
    parser = argparse.ArgumentParser(prog='main_scraper.py',
                                     usage='''
                                       ________________________________________________________
                                     / \                                                       \.
                                    |   |                                                       |.
                                     \_ |   Usage:                                              |.
                                        |                                                       |.
                                        |  Provide arguments about which data you want          |.
                                        |  to collect, and (optional) the way to collect it.    |.
                                        |  The program will return the the requested data       |.
                                        |  and will save it in the same directory.              |.
                                        |                                                       |.
                                        ''',
                                     description='''                                        |                                                       |.
                                        |   Description:                                        |.
                                        |                                                       |.
                                        |  This tool will scrape users info                     |.
                                        |  from the social network NomadList                    |.
                                        |   ____________________________________________________|___
                                        |  /                                                       /.
                                        \_/_______________________________________________________/.
                                     ''',
                                     epilog="Copyrights @Rozanna Royter\n "
                                            "          @Ron Zehavi",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     add_help=True
                                     )
    function_map = {'cities': cities,
                    'users': users,
                    'info': info,
                    'all': all}

    parser.add_argument('--run', '-r', choices=function_map.keys(),
                        help='(optional) Enter query key for:'
                             '"cities" - create or update cities list\n'
                             '"users" - create or update  users list\n'
                             '"info" - create or add users information\n'
                             '"all" - run all 3 options consecutively (also default),'
                             'it also set all other flags to default',
                        default='all')
    parser.add_argument('--login_url', '-l', type=str, help='your login link from NomadList (magic link), if not passed'
                                                           'it will not scrap data that is open to subscribers only, '
                                                           'like social networks accounts (instagram, twitter...)'
                        , default='')
    parser.add_argument('--code', '-cd', type=str, help='Security code for login from NomadList, if not passed'
                                                            'it will not scrap data that is open to subscribers only, '
                                                            'like social networks accounts (instagram, twitter...)'
                        , default='')
    parser.add_argument('--new', '-n', type=bool, help='start scraping data from scratch or adding info to existing db',
                        default=False)
    parser.add_argument('--chunk_size', '-c', type=int, help='program scraps users and saves info by groups of users, '
                                                             'this param control the group size',
                        default=10)
    parser.add_argument('--scroll_down', '-sd', type=int, help='The homepage initially loads with around 20 cities, '
                                                               'to get more cities we need to scroll down.'
                                                               'the scroll_down_loop_count can be set in order to take'
                                                               'just part of the cities (mostly for development).'
                                                               'Each scroll adds apprx 24 cities '
                                                               '(can vary based on screen resolution)',
                        default=60)
    args = parser.parse_args()

    if args.run == 'cities':
        function_map[args.run](args.new, args.scroll_down)
    elif args.run == 'info':
        function_map[args.run](args.login_url, args.code, args.new, args.chunk_size)
    else:
        function_map[args.run]()


if __name__ == '__main__':
    main()
