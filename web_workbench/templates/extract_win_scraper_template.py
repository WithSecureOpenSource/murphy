'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
'''
from model_extraction import base_extractor, configuration
from model_extraction.ui import window_scrap
from model_extraction.correlator import Correlator
    
def ignore_comboboxes(extractor, node, world):
    '''
    Not all builds have lang selection...
    '''
    for edge in node.edges:
        if ("window" in edge.custom and
          edge.custom['window'].get("class", '') == "ComboBox"):
            node_index = node.graph.nodes.index(node)
            edge_index = node.edges.index(edge)             
            extractor.crawler.ignorable_edges.append((node_index,
                                                           edge_index))
    
if __name__ == '__main__':
    test_files = configuration.get_default_config()["test files"]
    project_name = "##PROJECT_NAME##"
    file_name = "##FILENAME##"
    extractor = base_extractor.BaseExtractor(project_name,
                                             '\\utils\\runurl.py %s%s' % (test_files, file_name),
                                             live_transmit=True)

    #style the root node image
    extractor.root_node_image = "../desktop.png"
    
    #Ignore 'Browse For Folder' dialog as we dont care for windows native dialogs
    extractor.add_boundary_node('Browse For Folder')
    
    extractor.scrap_method = lambda node, world, scraper_hints, node_hints: window_scrap.custom_scraper(node, world)

    #dropdown / comboboxes not yet supported during crawling, ignore them for now
    extractor.graph.add_post_create_node_hook(-1, lambda node, world: ignore_comboboxes(extractor, node, world))
    
    extractor.crawl_application()
    #Following lines will associate the events collected with the performed user actions (edge executions)
    correlator = Correlator(extractor.world, extractor.crawler.timeline)
    correlator.correlate_events()
    extractor.project.graph.save_nodes()
