from cfg import *
from zkillboard import zKillboardScraper
from util import get_new_session
from worker import *


class Scraper():
    def __init__(self):
        pass

    def run(self):
        # Update zKillboard
        spawn_task(zKillboardScraper(get_new_session(), zkillboard_id))

        # Wait for tasks to complete
        wait_tasks()
