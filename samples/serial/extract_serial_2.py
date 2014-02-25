'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
'''

from model_extraction import base_extractor, configuration
from model_extraction.ui import window_scrap

INSTALL_APP_TEMPLATE = '''
def press_ok():
    \'\'\'
    Simplest way, press enter...
    \'\'\'        
    WORKER.input.keyboard.enters('{enter}')
'''

def enter_valid_serial(world):
    world.machine.automation.keyboard.enters("full{enter}")

def enter_demo_serial(world):
    world.machine.automation.keyboard.enters("demo{enter}")
    
def add_input_values(node, world, extractor):
    '''
    ok_edge = None
    
    for edge in node.edges:
        if edge.ui_type == 'text':
            ok_edge = edge
            # edge.custom['test value'] = [{'name': 'valid', 'value': '{+ctrl}a{-ctrl}demo'}]
            break
    '''
    ok_edge = [edge for edge in node.edges if edge.ui_type == 'text'][0]
    
    valid_edge = extractor.inject_edge(node, ok_edge.location, 'Valid serial', 'normal') # ok_edge.location or None, to get the text...
    valid_edge.method = enter_valid_serial
    valid_edge.method_source_code = ('press_ok', INSTALL_APP_TEMPLATE)
    
    demo_edge = extractor.inject_edge(node, ok_edge.location, 'Demo serial', 'normal')
    demo_edge.method = enter_demo_serial
    demo_edge.method_source_code = ('press_ok', INSTALL_APP_TEMPLATE)
    
        
if __name__ == '__main__':
    test_files = configuration.get_default_config()["test files"]
    extractor = base_extractor.BaseExtractor('serial_2',
                                             '\\utils\\runurl.py ' + test_files + 'installwserial.exe')

    extractor.scrap_method = lambda node, world, scraper_hints, node_hints: window_scrap.custom_scraper(node, world)

    extractor.graph.add_post_create_node_hook('Please Type In Your Installation Key And Click Ok',
                                              lambda node, world: add_input_values(node, world, extractor))
    
    extractor.crawl_application()
    
