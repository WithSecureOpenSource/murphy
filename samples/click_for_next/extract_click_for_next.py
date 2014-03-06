'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
'''

from model_extraction import base_extractor, configuration, image2
from model_extraction.ui import hybrid_scraper

if __name__ == '__main__':
    test_files = configuration.get_default_config()["test files"]
    extractor = base_extractor.BaseExtractor('click_for_next',
                                             '\\utils\\runurl.py ' + test_files + 'click_for_next.exe')

    #Customize look of desktop node for small icon
    extractor.scrap_method = hybrid_scraper.scrap
    #style the root node image
    extractor.root_node_image = "../desktop.png"
    
    extractor.crawl_application()
    
    # By default one path will be taken after selecting minimal install
    # but we want also to explore what happens when the user selects full
    # install, which we know it goes somewhere else.
    # So we clone the next edge, start a crawl session, navigate specific
    # steps in specific order and then let the crawler discover the rest
        
    select_installation_2 = extractor.graph.get_node("Please Select Type Of Installation_2")
    next_2 = select_installation_2.get_edge("Next").clone()
    next_2.name = "Next_2"
    extractor.update_project(select_installation_2)

    extractor.world.reset() #get a machine in clean state
    extractor.graph.get_node("Node 0").get_edge("Launch application").perform(extractor.world)
    extractor.graph.get_node("Please Select Type Of Installation").get_edge("Full the product will install all its components").perform(extractor.world)
    #now next_2 is an unexplored edge, so the crawler will map what it happens there
    extractor.continue_crawl()
