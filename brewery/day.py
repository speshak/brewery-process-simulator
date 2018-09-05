import logging
import requests
from .resources import Batch


class BrewDayLoader:
    def __init__(self):
        self.base_url = 'https://api-prod.barnweiser.com'
        self.logger = logging.getLogger(__name__)

    def load_day(self, date):
        data = self.fetch_day_data(date)
        batches = []

        for recipe in data:
            batch = Batch()
            batch.name = recipe['F_R_NAME']
            batch.boil_time = recipe['F_R_EQUIPMENT']['F_E_BOIL_TIME']
            batch.batch_size = recipe['F_R_EQUIPMENT']['F_E_BATCH_VOL']
            batch.boil_volume = recipe['F_R_EQUIPMENT']['F_E_BOIL_VOL']
            batch.mash_volume = recipe['F_R_EQUIPMENT']['F_E_MASH_VOL']

            batches.append(batch)

        return batches

    def fetch_day_data(self, date):
        self.logger.info("Fetching data for %s" % date)
        res = requests.get("%s/brewday/%s" % (self.base_url, date))
        res.raise_for_status()
        return res.json()
