import argparse
from offerup.scanner.selenium_bot import SeleniumBot
from offerup.scanner.http_bot import GraphQLBot

def main():
    parser = argparse.ArgumentParser(description='OfferUp Scanner')
    parser.add_argument('--bot', choices=['selenium', 'graphql'], default='graphql',
                        help='Choose the bot type: selenium or graphql (default: selenium)')
    parser.add_argument('--browser', default='chrome',
                        help='Browser to use with Selenium (default: chrome)')
    args = parser.parse_args()

    if args.bot == 'selenium':
        bot = SeleniumBot(args.browser)
    else:
        bot = GraphQLBot()

    try:
        bot.scan()
    finally:
        if args.bot == 'selenium':
            bot.driver.close()

if __name__ == '__main__':
    main()