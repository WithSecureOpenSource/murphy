'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
'''

from model_extraction import base_extractor, configuration
from model_extraction.ui import hybrid_scraper

def customize_uac_node(extractor, node, world):
    '''
    For the UAC dialog we care only the yes-no button
    '''
    ignorable_areas = []
    if len(node.edges) > 0 and node.edges[0].name == "Element 0": # change when these notifs...
        ignorable_areas.append(node.edges[0].location)
        node.edges.pop(0)

    if len(node.edges) > 0 and node.edges[0].name == "Element 1": # show details
        ignorable_areas.append(node.edges[0].location)
        node.edges.pop(0)
    extractor.graph.node_hints[extractor.graph.nodes.index(node)] = {'ignorable': ignorable_areas}
    
        
if __name__ == '__main__':
    test_files = configuration.get_config()["configurations"]["uac on"]["test files"]
    extractor = base_extractor.BaseExtractor('7zip_uac_on',
                                             '\\utils\\runurl.py ' + test_files + '7z920.exe')

    # speedy launch doesnt work well with elevated processes
    extractor.use_fast_run_command = False
    
    extractor.graph.add_post_create_node_hook('User Access Control',
                                              lambda node, world: customize_uac_node(extractor, node, world))
                                              
    #Ignore 'Browse For Folder' dialog as we dont care for windows native dialog
    extractor.add_boundary_node('Browse For Folder')
    
    extractor.scrap_method = hybrid_scraper.scrap
    
    extractor.crawl_application()
    
