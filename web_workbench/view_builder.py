'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
'''

from multiprocessing import Process

def _build_dot_with_screenshots(dot, worker, directory, images_dir):
    import os, shutil
    from PIL import Image
    from murphy import utils, graphviz
    
    shutil.copyfile('static/turtle.gif', '%s/turtle.gif' % directory)
    
    dot_lines = dot.split("\n")
    new_dot_lines = dot_lines[:]
    simplified_dot_lines = dot_lines[:]
    nodes = worker.get_views()
    edge_image = '<<TABLE BORDER="0"><TR><TD WIDTH="%dpx" HEIGHT="%dpx"><IMG SRC="%s" SCALE="FALSE"/></TD></TR></TABLE>>'
    destination_count = {}
    end_of_definitions_index = 0
    is_definition = False
    for i in range(len(dot_lines)):
        line = dot_lines[i].strip()
        parts = line.split('"')
        if len(parts) == 5: #node def
            is_definition = True
            if parts[1] in nodes:
                node = nodes[parts[1]]
                reference_image = None
                
                if ('reference snapshots' in node['self'].HERE and
                  len(node['self'].HERE['reference snapshots']) > 0):
                    reference_image = node['self'].HERE['reference snapshots'][-1]
                
                if (reference_image is None and
                  'snapshots' in node['self'].HERE and
                  len(node['self'].HERE['snapshots']) > 0):
                    reference_image = node['self'].HERE['snapshots'][0]
                    
                if reference_image:
                    if reference_image[-4:] == '.svg':
                        img_file_name = directory + "/" + reference_image
                        shutil.copyfile('%s/%s' % (images_dir, reference_image), img_file_name)
                        line = line[:-2] + ' shape=none margin=0 label=%s];' % (edge_image % (164, 124, img_file_name)).replace('SCALE="FALSE"','')
                    else:
                        img_file_name = directory + "/" + reference_image[:-4] + '.png'
                        img = Image.open('%s/%s' % (images_dir, reference_image))
                        img.save(img_file_name)
                        line = line[:-2] + ' shape=none margin=0 label=%s];' % (edge_image % (img.size[0], img.size[1], img_file_name))
                    new_dot_lines[i] = "\t" + line
                    simplified_dot_lines[i] = new_dot_lines[i]
        elif len(parts) == 7: #??? node
            if is_definition:
                end_of_definition_index = i
            is_definition = False
            new_dot_lines[i] = new_dot_lines[i][:-2] + ' shape=circle image="%s/turtle.gif"];' % directory
            new_dot_lines[i] = new_dot_lines[i].replace('label="???"', 'label=""')
            simplified_dot_lines[i] = new_dot_lines[i]
        elif len(parts) == 9: # ->
            if is_definition:
                end_of_definition_index = i
            is_definition = False
            if parts[1] in nodes:
                node = nodes[parts[1]]
                verb = node['verbs'][parts[5]]
                if 'how' in verb:
                    how = verb['how']
                    if type(how) is dict and 'snapshots' in how and len(how['snapshots']) > 0:
                        img = Image.open(images_dir + "/" + how['snapshots'][0])
                        img_name = directory + "/" + how['snapshots'][0][:-4] + '.png'
                        if 'logs' in verb and verb['logs'] != "":
                            #reserve space for all icons so it wont overlap
                            new_width = img.size[0] + 3 + 16 + 3 + 8 + 3 + 16
                            new_height = img.size[1] + 18 
                            collage = Image.new("RGB", (new_width, new_height), "white")
                            collage.paste(img, (0, new_height - img.size[1]))
                            img = collage
                        img.save(img_name)
                        new_dot_lines[i] = '\t' + line.replace('label="%s"' % parts[5], 'label=%s' % (edge_image % (img.size[0], img.size[1], img_name)))
                    
                
                if parts[1] == parts[3]:
                    simplified_dot_lines[i] = ''
                else:
                    simplified_dot_lines[i] = new_dot_lines[i]
                    destination = parts[3]
                    if not destination in destination_count:
                        destination_count[destination] = 1
                    else:
                        destination_count[destination] += 1
                
    max_references = 0
    max_referenced = None
    for node, count in destination_count.items():
        if count > max_references:
            max_references = count
            max_referenced = node
            
    if max_references > 4:
        '''
        Now we must add max_references definitions of max_referenced node
        new definitions needs label with old name
        Each new reference to max_referenced must use a different cloned definition
        '''
        extra_definitions_added = 0
        original_definition = -1
        for i in range(len(dot_lines)):
            line = dot_lines[i].strip()
            parts = line.split('"')
            if len(parts) == 5: #node def
                if parts[1] == max_referenced:
                    original_definition = i
            elif len(parts) == 9:
                if parts[1] in nodes:
                    node = nodes[parts[1]]
                    verb = node['verbs'][parts[5]]
                    destination = parts[3]
                    if destination == max_referenced and simplified_dot_lines[i] != '':
                        if extra_definitions_added > 0:
                            simplified_dot_lines[i] = simplified_dot_lines[i].replace('-> "%s"' % destination, '-> "%s.%s"' % (destination, extra_definitions_added))
                        extra_definitions_added += 1
        
        for i in range(extra_definitions_added - 1):
            new_definition = simplified_dot_lines[original_definition]
            new_definition = new_definition.replace('"%s" [' % max_referenced, '"%s.%s" [' % (max_referenced, i + 1))
            simplified_dot_lines.insert(end_of_definition_index, new_definition)
    
    dot = "\n".join(new_dot_lines)
    while simplified_dot_lines.count('') > 0:
        simplified_dot_lines.remove('')
        
    simplified_dot = "\n".join(simplified_dot_lines)
    temp_file = '%s/flow-images.dot' % directory
    simple_temp_file = '%s/simple-flow-images.dot' % directory
    target_file = '%s/flow-images.xml' % directory
    simple_target_file = '%s/simple-flow-images.xml' % directory
    #FIXME: do silent_remove with proper exception handling...
    if os.path.isfile(temp_file):
        os.remove(temp_file)
    if os.path.isfile(target_file):
        os.remove(target_file)
    if os.path.isfile(simple_temp_file):
        os.remove(simple_temp_file)
    if os.path.isfile(simple_target_file):
        os.remove(simple_target_file)
    
    utils.save_file(dot, temp_file)
    graphviz.generate_svg(temp_file)
    os.rename('%s.svg' % temp_file, target_file)
    os.remove(temp_file)
    utils.save_file(simplified_dot, simple_temp_file)
    graphviz.generate_svg(simple_temp_file)
    os.rename('%s.svg' % simple_temp_file, simple_target_file)
    #os.remove(simple_temp_file)


def _build_view(model_file_name, view_name, view_type, output_dir):
    '''
    Builds the given view
    '''
    import sys, os
    from murphy.model import Model
    from murphy import utils, graphviz
    #FIXME: this is needed in order to import the module, but may be better to
    #do it in the model object before importing?
    base_path = os.path.dirname(os.path.dirname(model_file_name))
    base_path = os.path.abspath(os.path.dirname(base_path))
    sys.path.append(base_path)
    
    model = Model(model_file_name)
    worker = model.new_worker()
    start_node = model.get_starting_node(view_name)
    dot = worker.graphs.generate_from_spider(start_node, {})
    temp_file = '%s/temp.dot' % output_dir
    target_file = '%s/flow.xml' % output_dir
    #FIXME: do silent_remove with proper exception handling...
    if os.path.isfile(temp_file):
        os.remove(temp_file)
    if os.path.isfile(target_file):
        os.remove(target_file)
        
    utils.save_file(dot, temp_file)
    graphviz.generate_svg(temp_file)
    os.rename('%s.svg' % temp_file, target_file)
    #os.remove(temp_file)

    #svg_content = utils.load_text_file(target_file)
    import zipfile
    zip = zipfile.ZipFile('%s.zip' % target_file, 'w')
    zip.write(target_file, 'flow.xml')
    zip.close()
    
    _build_dot_with_screenshots(dot, worker, output_dir, model.images_dir)
    
    svg_content = utils.load_text_file('%s/simple-flow-images.xml' % output_dir)
    svg_content = svg_content.replace('xlink:href="%s/' % output_dir, 'xlink:href="')
    utils.save_file(svg_content, '%s/local-simple-flow-images.xml' % output_dir)
    
    downloadable_name = os.path.basename(model_file_name)
    if downloadable_name.find(".") != -1:
        downloadable_name = downloadable_name.split(".")[0]
    downloadable_name = '%s-%s-simple.zip' % (downloadable_name, view_name)
    
    zip = zipfile.ZipFile('%s/%s' % (output_dir, downloadable_name), 'w')
    zip.write('%s/local-simple-flow-images.xml' % output_dir, 'flow.xml')
    for file_name in os.listdir(output_dir):
        if file_name.endswith(".png") or file_name.endswith(".gif"):
            zip.write('%s/%s' % (output_dir, file_name), file_name)
    zip.close()

    
def build_view(model_file_name, view_name, view_type, output_dir):
    proc = Process(target=_build_view, args=(model_file_name, view_name, view_type, output_dir,))
    proc.start()
    proc.join()
    if proc.exitcode != 0:
        raise Exception("Failed to create the graph file for %s, %s %s" % (output_dir, model_file_name, view_name))
