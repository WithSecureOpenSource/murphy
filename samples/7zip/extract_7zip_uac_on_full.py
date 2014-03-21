'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

NOT WORKING AT THE MOMENT
'''

from model_extraction import base_extractor, configuration
from model_extraction.ui import hybrid_scraper


def customize_uac_node_2(crawler, node, world):
    node_index = node.graph.nodes.index(node)
    crawler.ignorable_edges.append((node_index, 2))

def customize_uac_node_3(crawler, node, world):
    node_index = node.graph.nodes.index(node)
    crawler.ignorable_edges.append((node_index, 0))

def customize_uac_node_4(crawler, node, world):
    node_index = node.graph.nodes.index(node)
    crawler.ignorable_edges.append((node_index, 3))

    
if __name__ == '__main__':
    test_files = configuration.get_config()["configurations"]["uac on"]["test files"]
    extractor = base_extractor.BaseExtractor('7zip_uac_on_full',
                                             '\\utils\\runurl.py ' + test_files + '7z920.exe')

    # speedy launch doesnt work well with elevated processes
    extractor.use_fast_run_command = False
                                             
    #Ignore 'Browse For Folder' dialog as we dont care for windows native dialog
    extractor.add_boundary_node('Browse For Folder')

    crawler = extractor.crawler
    extractor.graph.add_post_create_node_hook('User Access Control_2',
                                              lambda node, world: customize_uac_node_2(crawler, node, world))
    
    extractor.graph.add_post_create_node_hook('User Access Control_3',
                                              lambda node, world: customize_uac_node_3(crawler, node, world))

    extractor.graph.add_post_create_node_hook('User Access Control_4',
                                              lambda node, world: customize_uac_node_4(crawler, node, world))
    
    extractor.scrap_method = hybrid_scraper.scrap
    
    extractor.crawl_application()
    
