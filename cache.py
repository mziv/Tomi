import discord
from discord.ext import commands
import os
import json
import logging
import datetime
import re

DATE_FORMAT = '%a, %d %b %Y %H:%M:%S UTC'
def custom_parser(dct):
    for k, v in dct.items():
        if type(v) == str and re.search("\ UTC", v):
            try:
                dct[k] = datetime.datetime.strptime(v, DATE_FORMAT)
            except Exception as e:
                print("e: ", e) # TODO - remove debug statement
    return dct
        
# subclass JSONEncoder
class DateTimeEncoder(json.JSONEncoder):
    #Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.strftime(DATE_FORMAT)

class Cache:
    def __init__(self, is_production_mode):
        self.cache_dir = "prod_cache" if is_production_mode else "test_cache"

        # Create the cache directory if not yet present.
        if not os.path.isdir(self.cache_dir):
            os.mkdir(self.cache_dir)
        
    def save_data(self, cog_name, **kwargs):
        # Cache the data.
        with open(os.path.join(self.cache_dir, cog_name), 'w') as f:
            data = {key:val for key, val in kwargs.items() if val}
            json.dump(data, f, cls=DateTimeEncoder)

    def get_data(self, cog_name):
        cache_file = os.path.join(self.cache_dir, cog_name)
        if os.path.isfile(cache_file):
            with open(cache_file, 'r') as f:
                try:
                    data = json.load(f, object_hook=custom_parser)
                except json.JSONDecodeError as e:
                    logging.error('Error in %s', 'cache', exc_info=e)
                    print(f"'{cog_name}' had a decoding error so the cached data is being skipped. To recover the data, rename and modify the file before Tomi closes (otherwise the file will be overwritten with new cache data).")
                else:
                    if len(data) != 0:
                        print(f"'{cog_name}' has the following cached data: ", data)
                        ans = input(f"Load data for '{cog_name}' module from cache? (y/n): ")
                        if ans.strip().lower() == 'y':
                            print(f"Data successfully loaded into '{cog_name}'!")
                            return data
        return {}
