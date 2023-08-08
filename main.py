from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException, TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
from random import randint
import atexit

StartTime = time.time()

# Locations 
INDONESIA_COORDINATES = [(106.8275,-6.1750), (112.7378, -7.2458), (98.6739, 3.5894), (112.6200, -7.9800), (103.59932, -1.61775)]
PAKISTAN_COORDINATES = [(33.738045, 73.084488), (31.582045, 74.329376), (24.860966, 66.990501), (24.946218, 67.005615), (34.025917, 71.560135), (24.852768, 67.074760)]

# Variables to control bots
URL = "https://www.polygame.io"
NUMBER_OF_BOTS = 100
BOTS_LIST = []

# Variable to tell us how many bots worked correctly
SUCCESS_BOTS = 0

# Variables to manage maximum number of bots working paralelly
THREADS_POOL_COUNT = 0
MAX_THREADS = 10

# Range of time for bot to use the website
# TODO: Change values to 8 and 35
BOT_MIN_TIME_IN_MINUTES = 1
BOT_MAX_TIME_IN_MINUTES = 1
    
class Utils:
    # Connecting the browser driver to the url
    @staticmethod
    def connect(browser, url, bot_id):
        try:
            print(f'Bot {bot_id} - Trying to connect!')
            page_load_timeout = 5000
            browser.set_page_load_timeout(page_load_timeout)
            browser.get(url)
        except InvalidArgumentException:
            print(f"Bot {bot_id} - Error while opening website.")
            browser.quit()        

    @staticmethod
    # Find element by id and prints error if not found
    def find_element_by_id(browser,id):
        try:
            element = browser.find_element(By.ID, id)
            return element
        except NoSuchElementException as e:
            print(f"Element not found.") 
            
    @staticmethod
    # Find element by id and prints error if not found
    def find_element_by(browser, by, value):
        try:
            element = browser.find_element(by, value)
            return element
        except NoSuchElementException as e:
            print(f"Element not found.") 
            
    @staticmethod
    # Generate random number between min and max
    def generate_random_number(min, max):
        result = randint(min, max)
        return result

    @staticmethod            
    # Creating driver
    def create_browser(location=None):
        options=webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--mute-audio")
        
        # Lines for headless
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        #===================
        
        options.page_load_strategy='eager'
        browser = webdriver.Chrome(service=Service("chromedriver.exe"), options=options)
        
        if location != None:        
            (longitude, latitude) = location
            accuracy = 100
            browser.execute_cdp_cmd("Emulation.setGeolocationOverride", {
                "latitude": latitude,
                "longitude": longitude,
                "accuracy": accuracy
            })
        return browser
    
    @staticmethod            
    def delay(seconds):
        time.sleep(seconds)
        
    @staticmethod            
    def get_random_coordinates(coordinates_list):
        random_number = Utils.generate_random_number(0, len(coordinates_list) - 1)
        return coordinates_list[random_number]
        
    @staticmethod            
    def get_location(name):
        if name == 'Indonesia':
            return Utils.get_random_coordinates(INDONESIA_COORDINATES)
        elif name == 'Pakistan':
            return Utils.get_random_coordinates(PAKISTAN_COORDINATES)
        
    @staticmethod           
    def create_bot():
        watch_time = Utils.generate_random_number(BOT_MIN_TIME_IN_MINUTES, BOT_MAX_TIME_IN_MINUTES)
        browser = Utils.create_browser(Utils.get_location('Indonesia'))
        return Bot(browser, watch_time)

class Bot:
    
    bot_id = 0
    def __init__(self, browser, watch_time):
        Bot.bot_id += 1
        self.browser = browser
        self.watch_time = watch_time * 60
        self.id = Bot.bot_id
        
    def click_icon(self):
        popup_icon_id = "popup-close-icon-bot"
        max_tries = 30
        tries = 0
        while True:
            try:    
                Utils.delay(5)
                if tries >= max_tries:
                    print(f"Bot {self.id} - Couldn't click icon! Stopping the bot and creating new bot")
                    self.create_and_start_new_bot()
                    return False
                tries += 1 
                self.browser.execute_script(f"document.getElementById('{popup_icon_id}')?.click()")
                break
            except Exception:
                print(f"Bot {self.id} - Couldn't click icon")
                
        print(f"Bot {self.id} - Icon clicked")
        return True
        
    def find_video_elements_length(self):
        video_elements = self.browser.find_elements(By.TAG_NAME, "video")
        return len(video_elements)
        
    def click_video(self, video_elements_length):
        max_tries = video_elements_length * 10
        tries = 0
        curr_id = 0
        max_id = video_elements_length - 1
        while True:
            try:      
                Utils.delay(5)
                if tries >= max_tries:
                    print(f"Bot {self.id} - Couldn't open video! Stopping the bot.")
                    return
                tries += 1 
                video_id = f"video-carousel-{curr_id}_html5_api"
                # print(f"Bot {self.id} - {video_id}")
                curr_id += 1
                if curr_id > max_id:
                    curr_id = 0
                self.browser.execute_script(f"document.getElementById('{video_id}')?.click()")
                break
            except Exception as e:
                print(f"Bot {self.id} - Couldn't click video")
                
        print(f"Bot {self.id} - Video clicked")
        
    def create_and_start_new_bot(self):
            self.stop_bot()
            global THREADS_POOL_COUNT
            THREADS_POOL_COUNT += 1
            bot = Utils.create_bot()
            print(f'Bot {bot.id} created.')
            bot.go_to_streaming_page()
        
    def wait_for_page_to_load(self):
        waiting_time = 5 * 60
        try:
            WebDriverWait(self.browser, waiting_time).until(EC.presence_of_element_located((By.TAG_NAME, 'video')))
            return True
        except TimeoutException:
            print(f"Bot {self.id} - Page not loaded correctly! Closing the bot and creating a new bot.")
            self.create_and_start_new_bot()
            return False
        except WebDriverException:
            print(f"Bot {self.id} - Page not loaded correctly! Closing the bot and creating a new bot.")
            self.create_and_start_new_bot()
            return False
        
    def connect_bot(self):
        try:
            Utils.connect(self.browser, URL, self.id)
            print(f"Bot {self.id} - Connected!")
            return True
        except TimeoutException:
            print(f'Bot {self.id} - Timeout Exception caught! Closing the bot and creating a new bot.')
            self.create_and_start_new_bot()
            return False
        
    def watch_and_close(self):
        global SUCCESS_BOTS
        Utils.delay(self.watch_time)
        print(f"Bot {self.id} - Task completed. Stopping")
        SUCCESS_BOTS += 1
        print(f"Total: {NUMBER_OF_BOTS}, Success: {SUCCESS_BOTS}")
        self.stop_bot()
        
    def go_to_streaming_page(self):
        if not self.connect_bot():
            return
        if not self.wait_for_page_to_load():
            return
        if not self.click_icon():
            return
        video_elements_length = self.find_video_elements_length()
        if video_elements_length == 0:
            print(f"Bot {self.id} - No live streams found! Stopping the bot")
            self.stop_bot()
            return
        self.click_video(video_elements_length)
        self.watch_and_close()
    
    def stop_bot(self):
        global THREADS_POOL_COUNT
        THREADS_POOL_COUNT -= 1
        self.browser.quit()
  
            
# Driver function that controls main flow of the program
def main():
    global THREADS_POOL_COUNT, MAX_THREADS, NUMBER_OF_BOTS
    # NUMBER_OF_BOTS = Utils.generate_random_number(10000, 17000)
    wait_time = 5
    while True:
        if THREADS_POOL_COUNT < MAX_THREADS:
            bot = Utils.create_bot()
            BOTS_LIST.append(bot)
            thread=threading.Thread(target=bot.go_to_streaming_page)
            thread.start()        
            THREADS_POOL_COUNT += 1
        else:
            Utils.delay(wait_time)
        if len(BOTS_LIST) >= NUMBER_OF_BOTS:
            break
            
def exit_handler():
    if THREADS_POOL_COUNT == 0:
        return
    print("Stopping all bots!")
    for bot in BOTS_LIST:
        bot.stop_bot()

atexit.register(exit_handler)

main()

