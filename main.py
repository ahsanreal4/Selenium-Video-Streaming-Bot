from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import threading
from random import randint
import atexit

# Variables to control bots
URL = "https://www.polygame.io"
NUMBER_OF_BOTS = 4000
BOTS_LIST = []
AVAILABLE_PROXY_IPS = ["146.19.81.205:65432", "146.19.81.220:65432", "146.19.81.222:65432", "146.19.81.237:65432", "146.19.81.252:65432", "146.19.81.192:65432", "146.19.81.193:65432", "146.19.81.194:65432", "146.19.81.195:65432", "146.19.81.196:65432", "146.19.81.197:65432", "146.19.81.198:65432", "146.19.81.199:65432", "146.19.81.200:65432", "146.19.81.201:65432", "146.19.81.203:65432", "146.19.81.206:65432", "146.19.81.207:65432", "146.19.81.208:65432", "146.19.81.209:65432", "146.19.81.210:65432", "146.19.81.211:65432", "146.19.81.212:65432", "146.19.81.214:65432", "146.19.81.215:65432",
                       "146.19.81.216:65432", "146.19.81.218:65432", "146.19.81.223:65432", "146.19.81.224:65432", "146.19.81.225:65432", "146.19.81.226:65432", "146.19.81.227:65432", "146.19.81.229:65432", "146.19.81.230:65432", "146.19.81.231:65432", "146.19.81.233:65432", "146.19.81.235:65432", "146.19.81.238:65432", "146.19.81.239:65432", "146.19.81.240:65432", "146.19.81.241:65432", "146.19.81.242:65432", "146.19.81.243:65432", "146.19.81.244:65432", "146.19.81.246:65432", "146.19.81.247:65432", "146.19.81.248:65432", "146.19.81.250:65432", "146.19.81.254:65432", "146.19.81.255:65432"]
IN_USE_PROXY_IPS = []

# Variable to tell us how many bots worked correctly
SUCCESS_BOTS = 0

# Variable to tell us how many bots raised errors
ERROR_BOTS = 0

# Variables to manage maximum number of bots working paralelly
THREADS_POOL_COUNT = 0
MAX_THREADS = 5

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
            return True
        except Exception:
            print(f"Bot {bot_id} - Error while opening website.")
            browser.quit()
            return False

    @staticmethod
    # Find element by id and prints error if not found
    def find_element_by_id(browser, id):
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
    def create_browser(proxy_ip):
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument("--mute-audio")

        # Lines for headless
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        # ===================

        proxy_server_url = proxy_ip
        options.add_argument(f'--proxy-server={proxy_server_url}')

        options.page_load_strategy = 'eager'
        browser = webdriver.Chrome(service=Service(
            "chromedriver.exe"), options=options)
        return browser

    @staticmethod
    def delay(seconds):
        time.sleep(seconds)

    @staticmethod
    def remove_ip_from_list(ip, curr_list):
        new_list = []
        for i in range(0, len(curr_list)):
            curr_ip = curr_list[i]
            if ip != curr_ip:
                new_list.append(curr_ip)
        return new_list

    @staticmethod
    def create_bot(proxy_ip):
        global AVAILABLE_PROXY_IPS, IN_USE_PROXY_IPS
        AVAILABLE_PROXY_IPS = Utils.remove_ip_from_list(
            proxy_ip, AVAILABLE_PROXY_IPS)
        IN_USE_PROXY_IPS.append(proxy_ip)
        watch_time = Utils.generate_random_number(
            BOT_MIN_TIME_IN_MINUTES, BOT_MAX_TIME_IN_MINUTES)
        browser = Utils.create_browser(proxy_ip)
        return Bot(browser, watch_time, proxy_ip)


class Bot:

    bot_id = 0

    def __init__(self, browser, watch_time, proxy_ip):
        Bot.bot_id += 1
        self.browser = browser
        self.watch_time = watch_time * 60
        self.id = Bot.bot_id
        self.ip = proxy_ip

    def click_icon(self):
        popup_icon_id = "popup-close-icon-bot"
        max_tries = 5
        tries = 0
        while True:
            try:
                Utils.delay(5)
                if tries >= max_tries:
                    print(
                        f"Bot {self.id} - Couldn't click icon! Stopping the bot and creating new bot")
                    self.create_and_start_new_bot()
                    return False
                tries += 1
                self.browser.execute_script(
                    f"document.getElementById('{popup_icon_id}')?.click()")
                break
            except Exception:
                print(f"Bot {self.id} - Couldn't click icon")

        print(f"Bot {self.id} - Icon clicked")
        return True

    def find_video_elements_length(self):
        video_elements = self.browser.find_elements(By.TAG_NAME, "video")
        return len(video_elements)

    def click_video(self, video_elements_length):
        max_tries = video_elements_length * 2
        tries = 0
        curr_id = 0
        max_id = video_elements_length - 1
        while True:
            try:
                Utils.delay(5)
                if tries >= max_tries:
                    print(
                        f"Bot {self.id} - Couldn't open video! Stopping the bot.")
                    self.create_and_start_new_bot()
                    return False
                tries += 1
                video_id = f"video-carousel-{curr_id}_html5_api"
                # print(f"Bot {self.id} - {video_id}")
                curr_id += 1
                if curr_id > max_id:
                    curr_id = 0
                self.browser.execute_script(
                    f"document.getElementById('{video_id}')?.click()")
                break
            except Exception as e:
                print(f"Bot {self.id} - Couldn't click video")

        print(f"Bot {self.id} - Video clicked")
        return True

    def click_video_on_streaming_page(self):
        video_element = self.browser.find_element(By.TAG_NAME, "video")
        video_id = video_element.get_attribute('id')
        if video_element:
            is_video_paused = self.browser.execute_script(
                f"return document.getElementById('{video_id}')?.paused;")

            # click live video
            if is_video_paused:
                self.browser.execute_script(
                    f"document.getElementById('{video_id}')?.click()")

            is_video_paused = self.browser.execute_script(
                f"return document.getElementById('{video_id}')?.paused;")

            # if video is paused that means it's a recorded video so play recorded video
            if is_video_paused:
                # click recorded video
                # keep checking for recorded videos and clicking it until it starts playing
                tries = 0
                max_tries = 10
                while is_video_paused:
                    if tries >= max_tries:
                        break
                    tries += 1
                    try:
                        video_element.click()
                    except Exception:
                        continue
                    Utils.delay(1)
                    is_video_paused = self.browser.execute_script(
                        f"return document.getElementById('{video_id}')?.paused;")
                    if is_video_paused:
                        recorded_video_load_delay = 5
                        Utils.delay(recorded_video_load_delay)

            print(f"Bot {self.id} - Video clicked on streaming page")

    def create_and_start_new_bot(self):
        self.stop_bot()
        global ERROR_BOTS
        ERROR_BOTS += 1

    def wait_for_page_to_load(self):
        waiting_time = 2 * 60
        try:
            WebDriverWait(self.browser, waiting_time).until(
                EC.presence_of_element_located((By.TAG_NAME, 'video')))
            return True
        except Exception:
            print(
                f"Bot {self.id} - Page not loaded correctly! Closing the bot and creating a new bot.")
            self.create_and_start_new_bot()
            return False

    def connect_bot(self):
        try:
            if Utils.connect(self.browser, URL, self.id):
                print(f"Bot {self.id} - Connected!")
                return True
            else:
                print(
                    f"Bot {self.id} - Page not loaded correctly! Closing the bot and creating a new bot.")
                self.create_and_start_new_bot()
                return False
        except TimeoutException:
            print(
                f'Bot {self.id} - Timeout Exception caught! Closing the bot and creating a new bot.')
            self.create_and_start_new_bot()
            return False
        except Exception:
            print(
                f"Bot {self.id} - Page not loaded correctly! Closing the bot and creating a new bot.")
            self.create_and_start_new_bot()
            return False

    def watch_and_close(self):
        global SUCCESS_BOTS

        start = datetime.now()
        Utils.delay(self.watch_time)
        end = datetime.now()

        difference = end - start
        seconds = difference.total_seconds()
        minutes = seconds / 60
        print(
            f"Bot {self.id} - Task completed. Stopping after watching stream for {int(minutes)} minutes.")

        SUCCESS_BOTS += 1
        print(
            f"Total: {NUMBER_OF_BOTS}, Success: {SUCCESS_BOTS}, Error: {ERROR_BOTS}, Threads count: {THREADS_POOL_COUNT}")
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
            self.create_and_start_new_bot()
            return
        if not self.click_video(video_elements_length):
            return
        if not self.wait_for_page_to_load():
            return
        self.click_video_on_streaming_page()
        self.watch_and_close()

    def stop_bot(self):
        global THREADS_POOL_COUNT, IN_USE_PROXY_IPS, AVAILABLE_PROXY_IPS
        THREADS_POOL_COUNT -= 1
        IN_USE_PROXY_IPS = Utils.remove_ip_from_list(self.ip, IN_USE_PROXY_IPS)
        AVAILABLE_PROXY_IPS.append(self.ip)
        try:
            self.browser.quit()
        except Exception:
            print(f"Bot {self.id} - Error while closing the browser driver")

# Driver function that controls main flow of the program


def main():
    global THREADS_POOL_COUNT, MAX_THREADS, NUMBER_OF_BOTS, SUCCESS_BOTS
    if MAX_THREADS > NUMBER_OF_BOTS:
        MAX_THREADS = NUMBER_OF_BOTS
    # NUMBER_OF_BOTS = Utils.generate_random_number(10000, 17000)
    wait_time = 1
    while True:
        # If required bots run successfully stop the program
        if SUCCESS_BOTS >= NUMBER_OF_BOTS:
            break
        # If threads pool count is not less than max threads create a new bot
        # If threads pool count and success bots is less than total number of bots then create a new bot
        if THREADS_POOL_COUNT < MAX_THREADS and THREADS_POOL_COUNT + SUCCESS_BOTS < NUMBER_OF_BOTS:
            ip_to_use = None
            if len(AVAILABLE_PROXY_IPS) > 0:
                ip_to_use = AVAILABLE_PROXY_IPS[0]
            if ip_to_use == None:
                print("No available IP")
                Utils.delay(wait_time)
                continue
            bot = Utils.create_bot(ip_to_use)
            BOTS_LIST.append(bot)
            thread = threading.Thread(target=bot.go_to_streaming_page)
            thread.start()
            THREADS_POOL_COUNT += 1
        # Just delay the while loop to wait for some seconds to wait for current bots to finish
        else:
            Utils.delay(wait_time)


def exit_handler():
    if THREADS_POOL_COUNT == 0:
        return
    print("Stopping all bots!")
    for bot in BOTS_LIST:
        bot.stop_bot()


atexit.register(exit_handler)

main()
