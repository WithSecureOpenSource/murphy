'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

NOT WORKING AT THE MOMENT
'''

from model_extraction import base_extractor, configuration
from model_extraction.ui import hybrid_scraper

def customize_uac_node(extractor, node, world):
    '''
    For the UAC dialog we care only the yes-no button
    '''
    ignorable_areas = []
    
    ignorable_areas.append(node.edges[0].location)
    node.edges.pop(0) # change when these notifs...
    
    node.edges[0].name = "Show details"
    node.edges[1].name = "Yes"
    node.edges[2].name = "No"

    extractor.graph.node_hints[extractor.graph.nodes.index(node)] = {'ignorable': ignorable_areas}

    
def customize_uac_node_2(extractor, node, world):
    '''
    For the UAC dialog we care only the yes-no button
    '''
    node.edges[0].name = "Hide details"
    node.edges[1].name = "Yes"
    node.edges[2].name = "No"

    ignorable_areas = []
    
    ignorable_areas.append(node.edges[3].location)
    node.edges.pop(3) # change when these notifs...

    extractor.graph.node_hints[extractor.graph.nodes.index(node)] = {'ignorable': ignorable_areas}

    
def activate_app(node, world):
    screen = world.machine.automation.grab_screen()
    world.machine.automation.mouse.click(screen.size[0] / 2, screen.size[1] / 2)
    return True

if __name__ == '__main__':
    test_files = configuration.get_config()["configurations"]["uac on"]["test files"]
    extractor = base_extractor.BaseExtractor('7zip_uac_on_2',
                                             '\\utils\\runurl.py ' + test_files + '7z920.exe')

    # speedy launch doesnt work well with elevated processes
    extractor.use_fast_run_command = False

    extractor.graph.add_post_create_node_hook('User Access Control',
                                              lambda node, world: customize_uac_node(extractor, node, world))
                                              
    extractor.graph.add_post_create_node_hook('User Access Control_2',
                                              lambda node, world: customize_uac_node_2(extractor, node, world))

    extractor.graph.add_pre_create_node_hook(3, activate_app)
                                              
    #Ignore 'Browse For Folder' dialog as we dont care for windows native dialog
    extractor.add_boundary_node('Browse For Folder')
    
    extractor.scrap_method = hybrid_scraper.scrap
    
    extractor.crawl_application()
    
