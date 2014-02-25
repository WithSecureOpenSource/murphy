'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
'''

from model_extraction import base_extractor, configuration

if __name__ == '__main__':
    test_files = configuration.get_default_config()["test files"]
    extractor = base_extractor.BaseExtractor('7zip',
                                             '\\utils\\runurl.py ' + test_files + '7z920.exe')

    #Ignore 'Browse For Folder' dialog as we dont care for windows native dialog
    extractor.add_boundary_node('Browse For Folder')

    #Experimental scraper, still under testing
    extractor.graph.scraper_hints[-1] = {'outfocus method': True}

    extractor.crawl_application()
    
