'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
'''

import time

from model_extraction.image2 import Image2
from model_extraction.automation_helpers import is_image_in_array

import logging
LOGGER = logging.getLogger('root.' + __name__)

INTERVAL_BETWEEN_SCREENSHOTS = 0.3


def wait_stable_screen(fetch_screen, seconds_of_stability=8):
    '''
    Waits until screen stabilizes, any animation or screen updates should
    finish and there should be no ui activity for a period of time to consider
    it stable
    '''
    LOGGER.info("Waiting for a stable screen")
    screen = Image2(image=fetch_screen())
    last_screens = [screen]
    last_hitlist = []
    consecutive_hits = 0
    first_hit_at = 0
    hits_needed = 5
    loop_count = 0
    images_in_short_memory = 3
    initiated_at = time.time()
    
    while True:
        loop_count += 1
        time.sleep(INTERVAL_BETWEEN_SCREENSHOTS)
        if loop_count % 40 == 0 and (time.time() - initiated_at) > (2 * seconds_of_stability):
            LOGGER.info("Will pause 5 seconds...")
            time.sleep(5)
            consecutive_hits = 0
            last_hitlist = []

        LOGGER.debug("Fetching screen")
        new_screen = Image2(fetch_screen())
        
        LOGGER.debug("Checking if image was recently viewed")
        found_in_cache = is_image_in_array(new_screen, last_screens)

        if found_in_cache == -1:
            LOGGER.debug("Image not found in the recently viewed cache")
            last_screens.append(new_screen)
            #Keep the short memory buffer within the given size
            if len(last_screens) > images_in_short_memory:
                last_screens.pop(0)
            consecutive_hits = 0
            last_hitlist = []
        else:
            consecutive_hits += 1
            if consecutive_hits == 1:
                first_hit_at = time.time()
            last_hitlist.append(found_in_cache)
            stable_for = (time.time() - first_hit_at)
            LOGGER.debug("Image in recents cache, consecutive hits is %d, image stable for %f seconds (needs %d hits and %d seconds of stability)!" % (consecutive_hits, stable_for, hits_needed, seconds_of_stability))
            if consecutive_hits >= hits_needed and (time.time() - first_hit_at) > seconds_of_stability:
                break
        time.sleep(0.1)
        
    screens = []
    matches_added = []
    for i in last_hitlist:
        if not i in matches_added:
            screens.append(last_screens[i])
            matches_added.append(i)
            
    return screens
