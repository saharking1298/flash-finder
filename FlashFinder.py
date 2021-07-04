# For licensing check LICENSE
from bs4 import BeautifulSoup
import subprocess
import traceback
import requests
import random
import os

player_path = os.path.join("Bin", "flashplayer.exe")
games_dir = "Games"
logs_dir = "Logs"
required_dirs = ["Games", "Logs", "Bin"]


def setup():
    """
    This function verifies that FlashFinder has all the needed resources to run.
    """
    for folder in required_dirs:
        if not os.path.isdir(folder):
            os.mkdir(folder)
    if not os.path.isfile(player_path):
        download_link = "https://fpdownload.macromedia.com/pub/flashplayer/updaters/32/flashplayer_32_sa_debug.exe"
        print(f'Bin{os.path.sep}flashplayer.exe is missing.')
        print(f'Downloading it from "{download_link}"...')
        content = requests.get(download_link).content
        with open(player_path, "wb") as f:
            f.write(content)
        print("Finished downloading Adobe Flash Player Debugger.")


class Wrapper:
    def __init__(self, debug=True):
        self.debug = debug
        self.request = None
        self.soup = None

    def log(self, *to_log):
        """
        This function logs a message to the console only if debug mode is on.
        :param to_log: Arguments to the print function.
        :return: None
        """
        if self.debug:
            print(*to_log)

    def game_in_library(self, game_name):
        """
        This function checks if a game is already downloaded to the game library.
        :param game_name: The name of the game file (including .swf extension)
        :type game_name: str
        :return:
        """
        return game_name in os.listdir(games_dir)

    def download_game(self, download_link, game_filename):
        """
        This function downloads an swf file to the game library, using custom file name.
        :param download_link: The download link for the game.
        :param game_filename: The filename to save the game (including .swf extension).
        :type game_filename: str
        :return:
        """
        self.log(f'Found an swf on: "{download_link}". Downloading!')
        game_path = self.get_game_path(game_filename)
        request = requests.get(download_link)
        with open(game_path, "wb") as f:
            f.write(request.content)

    def get_game_path(self, game_name):
        """
        This function returns the full path of a game.
        :param game_name: The name of the game file (including .swf extension)
        :type game_name: str
        :return:
        """
        return os.path.join(games_dir, game_name)

    def launch_game(self, game_name):
        """
        This function launches a game which is downloaded to the library.
        :param game_name: The name of the game file (including .swf extension)
        :type game_name: str
        :return:
        """
        self.log("Launching game!")
        game_path = self.get_game_path(game_name)
        command = f'{player_path} "{game_path}"'
        subprocess.Popen(command, shell=True)

    def parse_url(self, to_url):
        """
        This function takes a string and parse it into URL.
        :param to_url: The string to parse to URL
        :type to_url: str
        :return: The parsed url.
        """
        if to_url.strip() == "":
            return to_url
        url = to_url.replace(" ", "%20")
        if url.startswith("//"):
            url = url[2:]
        if not url.startswith("http"):
            url = "http://" + url
        return url

    def get_response_type(self, response):
        """
        This function gets and http response and returns its type.
        :param response: The requests object
        :return: Request type
        """
        return response.headers['Content-Type'].split(";")[0]

    def look_for_swf(self, html_content):
        """
        This function looks for a direct link to a swf file, and return the download link.
        :param html_content: The HTMl of the page
        :return:
        """
        link_to_swf = ""

        if link_to_swf == "":
            html_parts = html_content.split(".swf")
            if len(html_parts) > 1:
                part1 = html_parts[0].split('"')[-1]
                part2 = html_parts[1].split('"')[0]
                link_to_swf = part1 + ".swf" + part2
                if "<" in link_to_swf or ">" in link_to_swf:
                    part1 = html_parts[0].split("'")[-1]
                    part2 = html_parts[1].split("'")[0]
                    link_to_swf = part1 + ".swf" + part2

        link_to_swf = self.parse_url(link_to_swf).strip()

        link_valid = True
        if link_to_swf == "":
            link_valid = False
        else:
            try:
                response = requests.get(link_to_swf)
                if response.status_code == 200:
                    if self.get_response_type(response) == "text/html":
                        link_valid = False
                else:
                    link_valid = False
            except:
                self.log(f'Error trying to access: {link_to_swf}')
                link_valid = False

        if link_valid:
            return self.parse_url(link_to_swf)

    def start_operation(self, page_url):
        """
        This function gets a page URL and start looking for swf files attached to it.
        :param page_url: The page URL
        :return: None
        """
        page_url = self.parse_url(page_url)
        if "games.yo-yoo.co.il" in page_url:
            yoo_yoo_wrapper = YooYooWrapper()
            yoo_yoo_wrapper.start_operation(page_url)
            return
        self.log(f'Inspecting: {page_url}')
        self.request = requests.get(page_url)
        self.soup = BeautifulSoup(self.request.content, "html.parser")
        html_content = str(self.request.content)
        swf_link = self.look_for_swf(html_content)
        if swf_link is None:
            self.log("Couldn't find any swf file on the page. Skipping!")
        else:
            game_file = swf_link.split("/")[-1].split("?")[0]
            if not self.game_in_library(game_file):
                self.download_game(swf_link, game_file)
            self.launch_game(game_file)


class YooYooWrapper(Wrapper):
    def __init__(self):
        super().__init__()

    def get_game_title(self):
        """
        This function gets the title of a game in yoo-yoo games site.
        :return: Game's title
        """
        return self.soup.find("h1").text.strip()

    def find_game_source(self):
        """
        This function gets the link to the iframe/ swf file which is displayed in the game container.
        :return: The link for the game's source.
        """
        game_container = self.soup.find(id="game_container")
        iframe = game_container.find("iframe")
        if iframe is not None:
            game_source = {"type": "iframe", "link": iframe["src"]}
        else:
            game_source = {"type": "direct", "link": game_container.find("embed")["src"]}
        return game_source

    def start_operation(self, page_url):
        self.log("Inspecting: " + page_url)
        self.request = requests.get(page_url)
        self.soup = BeautifulSoup(self.request.content, "html.parser")

        game_title = self.get_game_title()
        game_file = game_title + ".swf"
        if self.game_in_library(game_file):
            self.log("Found game in game library. Launching!")
            self.launch_game(game_file)
        else:
            swf_link = self.look_for_swf(str(self.request.content))
            if swf_link is None:
                game_source = self.find_game_source()
                source_type = game_source["type"]
                source_link = self.parse_url(game_source["link"])
                if source_type == "direct":
                    self.download_game(source_link, game_file)
                    self.launch_game(game_file)
                else:
                    html_content = str(requests.get(source_link).content)
                    swf_link = self.look_for_swf(html_content)
                    if swf_link is None:
                        self.log("Couldn't find any swf file on the page. Skipping!")
                    else:
                        self.download_game(swf_link, game_file)
                        self.launch_game(game_file)
            else:
                self.download_game(swf_link, game_file)
                self.launch_game(game_file)


def main():
    while True:
        url = input("Please enter your URL: ").strip()
        if url == "":
            continue
        try:
            wrapper.start_operation(url)
        except Exception as e:
            print("Sorry, we couldn't parse this page.")
            log_file = os.path.join(logs_dir, "LatestLog.txt")
            error = traceback.format_exc()
            with open(log_file, "w") as f:
                f.write(error)
            print("Debug traceback at: " + log_file)


def test():
    """
    This function tests the program on random games from the site "http://games.yo-yoo.co.il/"
    """
    url_template = "http://games.yo-yoo.co.il/games_play.php?game="
    while True:
        user_input = input("Leave blank to test a random game or type anything to continue: ")
        if user_input.strip() != "":
            break
        rand = random.randint(100, 5000)  # Every game has an Id, flash games are estimated up to Id 5000.
        url = url_template + str(rand)
        try:
            wrapper.start_operation(url)
        except Exception as e:
            print("Sorry, we couldn't parse this page.")
            log_file = os.path.join(logs_dir, "LatestLog.txt")
            error = traceback.format_exc()
            with open(log_file, "w") as f:
                f.write(error)
            print("Debug traceback at: " + log_file)


if __name__ == '__main__':
    wrapper = Wrapper()
    setup()
    main()
