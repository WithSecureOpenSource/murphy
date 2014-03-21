'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

This is still under heavy experimentation, to run it you need a specially configured virtual machine.
You basically need to configure the secure desktop as follow:

Click Start and type gpedit.msc in the search box.
Navigate to Computer Configuration\Windows Settings\Security Settings\Local Policies\SecurityOptions.
Now change User Account Control: Switch to the secure desktop when prompting for elevation to disabled.

Save the virtual machine with that configuration, it will allow the scraper to scrap the uac prompts
'''

from model_extraction import base_extractor, configuration
from model_extraction.ui import hybrid_scraper

def customize_uac_node(extractor, node, world):
    '''
    For the UAC dialog we care only the yes-no button
    '''
    ignorable_areas = []
    edge = node.get_edge("Change when these notifications appear")
    ignorable_areas.append(edge.location)
    node.edges.pop(node.edges.index(edge))

    extractor.graph.node_hints[extractor.graph.nodes.index(node)] = {'ignorable': ignorable_areas}
        
        
if __name__ == '__main__':
    test_files = configuration.get_config()["configurations"]["uac on"]["test files"]
    extractor = base_extractor.BaseExtractor('7zip_uac_on',
                                             '\\utils\\runurl.py ' + test_files + '7z920.exe',
                                             config_name='uac on',
                                             live_transmit=True)

    #style the root node image
    extractor.root_node_image = "../desktop.png"

    extractor.graph.add_post_create_node_hook('User Account Control',
                                              lambda node, world: customize_uac_node(extractor, node, world))
                                              
    #Ignore 'Browse For Folder' dialog as we dont care for windows native dialog
    extractor.add_boundary_node('Browse For Folder')
    
    extractor.scrap_method = hybrid_scraper.scrap
    
    extractor.crawl_application()
    
