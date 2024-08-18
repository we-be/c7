from offerup.scanner.selenium_bot import SeleniumBot

# NOTE
# Most object use the `Config` instantiated at the bottom of config.py

if __name__ == '__main__':
    bot = SeleniumBot('chrome')
    bot.scan()
    bot.driver.close()
