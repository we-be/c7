from offerup.scanner.offerbot import OfferBot

# NOTE
# Most object use the `Config` instantiated at the bottom of config.py

if __name__ == '__main__':
    bot = OfferBot('firefox')
    bot.scan()
