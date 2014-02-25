'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

Scraper that actually uses multiple simple scrapers combined
'''
from model_extraction.ui import window_scrap, scraper
from model_extraction.ui.window_scrap import suggest_node_name, \
    suggest_node_file_name

def scrap(node, world, scraper_hints=None, node_hints=None):
    '''
    Scrap either using windows API or the graphic analysis
    '''
    active_window_rect = world.machine.helper.get_active_window_rect()
    
    if active_window_rect is None:
        scraper.scrap_state(node, world, scraper_hints, node_hints)
        node.name = suggest_node_name('User Access Control', node)
        #node.file_name = suggest_node_file_name(node)
    else:
        window_scrap.custom_scraper(node, world)
