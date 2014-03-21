'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

Represents a graph of a ui state chart
'''

from model_extraction import graph
from model_extraction.ui.node import Node

import logging
LOGGER = logging.getLogger('root.' + __name__)
    
class UIGraph(graph.Graph):

    def __init__(self, path, name, images_dir, image_tolerance=0.999):
        super(UIGraph, self).__init__()
        self.path = path
        self.name = name
        self.images_dir = images_dir
        self._pre_create_node_hooks = {}
        self._post_create_node_hooks = {}
        self._importable_node = {}
        self._create_node_hooks = {}
        #update notification, method signature is on_update(node)
        self.on_update = None
        self.node_hints = {}
        self.scraper_hints = {}
        #if provided, it will be called after the create node hook and is meant
        #to be used for boundary nodes where it is not desired to explore
        #beyond this node
        self.classify_node = None
        self.scrap_method = None
        self.parametrize_after_creation = True
        self.image_tolerance = image_tolerance
        
    
    def add_pre_create_node_hook(self, node_index, hook):
        '''
        Pre create node hooks are called once the node was created but before
        the scraping, so the node is empty
        '''
        self._pre_create_node_hooks[node_index] = hook
        
        
    def add_post_create_node_hook(self, node_index_or_name, hook):
        '''
        Post create node hooks are called after the node was created to be able
        to do fine tune adjustments
        Either the node index or the node name can be used to install this
        hook
        '''
        self._post_create_node_hooks[node_index_or_name] = hook
        
        
    def add_importable_node(self, node_index, template, images_dir):
        '''
        Adds a node that will be imported instead of scraped
        '''
        self._importable_node[node_index] = {'file': template,
                                             'images dir': images_dir}
        
        
    def add_create_node_hook(self, node_index, hook):
        '''
        Create node hooks are used for importing nodes instead of scraping
        them, they are called with the new empty node
        '''
        self._create_node_hooks[node_index] = hook

        
    def scrap_state(self, node, world):
        '''
        Scraps the ui into the given node for the given world state
        '''
        node_index = node.graph.nodes.index(node)
        
        scraper_hints = self.scraper_hints.get(node_index, {})
        scraper_hints.update(self.scraper_hints.get(-1, {}))
        
        node_hints = self.node_hints.get(node_index, {})
        
        if self.scrap_method is None:
            raise Exception("Scrap method must be provided before crawling")
        
        self.scrap_method(node, world, scraper_hints, node_hints)
        
            
    def create_node(self, name, world=None):
        '''
        Creates a node object, name must be unique and is derived from world
        At this moment, the name itself is ignored but there to comply with the
        graph interface
        '''
        name = 'nothing'
        node = Node(name, self.path + '/' + self.name, self.images_dir)
        node.graph = self
        node_index = len(self.nodes)
        self.nodes.append(node)
        
        if node_index in self._create_node_hooks:
            self._create_node_hooks[node_index](node, world)
            return node

        if self.classify_node:
            should_continue = self.classify_node(self, # pylint: disable=E1102
                                                 node,
                                                 world) 
            if should_continue == False:
                return node
                
        if -1 in self._pre_create_node_hooks:
            should_continue = self._pre_create_node_hooks[-1](node, world)
            if should_continue == False:
                return node

        if node_index in self._pre_create_node_hooks:
            should_continue = self._pre_create_node_hooks[node_index](node,
                                                                      world)
            if should_continue == False:
                return node
            
        if node_index in self._importable_node:
            template = self._importable_node[node_index]['file']
            images_dir = self._importable_node[node_index]['images dir']
            node.import_from_file(template, images_dir)
            #FIXME: as sanity check it should validate it recognizes
        else:
            self.scrap_state(node, world)
            
        if node_index in self._post_create_node_hooks:
            self._post_create_node_hooks[node_index](node, world)
        elif node.name in self._post_create_node_hooks:
            self._post_create_node_hooks[node.name](node, world)
                
            
        if -1 in self._post_create_node_hooks:
            self._post_create_node_hooks[-1](node, world)

        if self.parametrize_after_creation:
            # Ignorable areas are relative to the node, not absolute to the
            # screen
            ignorable_areas = self.node_hints.get(node_index,
                                                  {}).get('ignorable', [])
            node.parametrize(ignorable_areas)
        return node
    
            
    def save_nodes(self):
        for node in self.nodes:
            node.save()
            node.save_as_python()
    
