import logging
import requests
import os
from .resources import Batch


class BrewDayLoader:
    """Load brew day batches from the Barnweiser data API"""

    def __init__(self):
        self.base_url = os.getenv('BARNWEISER_API',
                                  'https://api-prod.barnweiser.com')
        self.logger = logging.getLogger(__name__)

    def load_day(self, date):
        """Load batches for a day"""
        data = self.fetch_day_data(date)
        batches = []

        for recipe in data:
            batch = Batch()
            batch.name = recipe['F_R_NAME']
            batch.boil_time = recipe['F_R_EQUIPMENT']['F_E_BOIL_TIME']
            batch.batch_size = recipe['F_R_EQUIPMENT']['F_E_BATCH_VOL']
            batch.boil_volume = recipe['F_R_EQUIPMENT']['F_E_BOIL_VOL']
            batch.mash_volume = recipe['F_R_EQUIPMENT']['F_E_MASH_VOL']
            batch.mash_time = self.sum_mash_time(recipe)
            batch.recipe_type = recipe['recipe_type']

            batches.append(batch)

        return batches

    def fetch_day_data(self, date):
        """Get a day's batches from the data API"""
        self.logger.info("Fetching data for %s" % date)
        res = requests.get("%s/brewday/%s" % (self.base_url, date))
        res.raise_for_status()
        return res.json()

    def sum_mash_time(self, recipe):
        """Sum up the total time of all mash steps in a recipe"""
        try:
            # holy deep structure, batman
            steps = recipe['F_R_MASH']['steps']['Data']['MashStep']
            return sum(i['F_MS_STEP_TIME'] for i in steps)
        except KeyError:
            return 0
