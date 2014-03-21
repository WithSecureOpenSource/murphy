'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Demo of how to collect events information like harddisk, network and/or registry activity
Note, this is still an early release of this functionality and will surely change a lot in the future

To run this example you need a virtual machine configured specifically for it.

In the virtual machine (NOT where you run the workbench!):
    add a folder \utils\procmon
    in it, copy procmon.exe from sysinternals (http://technet.microsoft.com/en-us/sysinternals/bb896645.aspx)
    run it once and accept the license terms
    close it
    click on the desktop, so the focus is out of the taskbar or any strange place
    save a snapshot of the virtual machine, call it for example 'instrumented machine'
    
    add a configuration entry in model_extraction\default_config.json (or model_extraction\custom_config.json)
    
        "instrumented machine": {
            "module": "rules_vbox.py",
            "setup files": "http://192.168.56.1:8901/",
            "test files": "http://192.168.56.1:8901/files/",
            "image name": "MurphyWin7Ult",
            "snapshot": "prepared",
            "already prepared": true,
            "prepare command": "\\utils\\runurl.py http://192.168.56.1:8901/prepare_for_scrap.bat",
            "remote logs": "\\utils\\procmon\\activity_log.pml"
        },

    in the same file, change the line for the default config, for example:
        "default configuration": "instrumented machine"
        
Then you're ready to run this example
'''

from model_extraction import base_extractor, configuration
from model_extraction.ui import window_scrap
from model_extraction.correlator import Correlator

if __name__ == '__main__':
    test_files = configuration.get_default_config()["test files"]
    extractor = base_extractor.BaseExtractor('instrumentation',
                                             '\\utils\\runurl.py ' + test_files + 'instrumentation.exe',
                                             config_name='instrumented and prepared')

    extractor.scrap_method = lambda node, world, scraper_hints, node_hints: window_scrap.custom_scraper(node, world)
    
    #style the root node image
    extractor.root_node_image = "../desktop.png"
    
    extractor.crawl_application()
    #Following lines will associate the events collected with the performed user actions (edge executions)
    correlator = Correlator(extractor.world, extractor.crawler.timeline)
    correlator.correlate_events()
    extractor.project.graph.save_nodes()
