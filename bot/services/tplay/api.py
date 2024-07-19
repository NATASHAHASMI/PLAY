import re
import json
import requests
from bot.config import tplay_path
from bot.helpers.utils import timestamp_to_datetime
from datetime import datetime, timedelta
from dateutil import parser
import pytz
import random

def within_12_hours(timestamp):
    provided_time = parser.isoparse(timestamp)
    provided_time = provided_time.astimezone(pytz.timezone('Asia/Kolkata'))
    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
    time_difference = current_time - provided_time
    return time_difference < timedelta(hours=1)

class TPLAY_API():
    API_ALL_CHANNELS = "https://kong-tatasky.videoready.tv/content-detail/pub/api/v1/channels?limit=1000"
    FETCHER = "https://tplayapi.code-crafters.app/321codecrafters/fetcher.json"
    HMAC = "https://tplayapi.code-crafters.app/321codecrafters/hmac.json?random={}".format(random.randint(10,99))
    HMAC_v2 = "https://chutiya-maharaj-ab-karlo-chori-ye-toxic-iptv-playlist-hei.vercel.app/411.mpd?random={}".format(random.randint(10,99))

    def __init__(self, channel_slug):
        self.channel_slug = channel_slug
        self.channels = requests.get(self.FETCHER).json()

    def get_hmac_v2(self):
        response = requests.get(self.HMAC).json()['data']
        return response['hmac']['hdnea']['value']

    def get_hmac(self):
        response = requests.get(self.HMAC_v2)
        if response.status_code == 200:
            matches = re.findall(r'\?hdnea=exp=[^"]+', response.text)
            if matches:
                return matches[0].replace("?", "").strip()
            else:
                raise ValueError("No HMAC value found in the response.")
        else:
            response.raise_for_status()

    def get_data(self):
        channels = self.channels.get('data', {}).get('channels', [])
        data = [channel for channel in channels if (channel.get('name', '').replace(" ", "").lower() == self.channel_slug.lower())]
        if data:
            return data[0]
        else:
            raise Exception("Channel slug didn't match any channel in the tplay data. Please check and try again!...")

    def get_channelId(self):
        all_channels = requests.get(self.API_ALL_CHANNELS).json().get('data', {}).get('list', [])
        try:
            data = [channel for channel in all_channels if channel.get('title', '').replace("!" , "").replace("Hindi" , "").replace(" ", "") == self.channel_slug]
            if data:
                return data[0].get('id')
            else:
                raise Exception("Unable to extract channelId from channelSlug")
        except Exception as e:
            raise Exception(f"Error retrieving channel ID: {str(e)}")
            
