'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
'''

from model_extraction import base_extractor, configuration
from model_extraction.ui import window_scrap
    
if __name__ == '__main__':
    test_files = configuration.get_default_config()["test files"]
    extractor = base_extractor.BaseExtractor('7zipWinScraper',
                                             '\\utils\\runurl.py ' + test_files + '7z920.exe')

    #Ignore 'Browse For Folder' dialog as we dont care for windows native dialog
    extractor.add_boundary_node('Browse For Folder')
    
    extractor.scrap_method = lambda node, world, scraper_hints, node_hints: window_scrap.custom_scraper(node, world)
    
    extractor.crawl_application()
