'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Comparison between models

cases: (node x as a node in the model, compared against the reference model)
    node x changed image
    node x removed
    node x inserted
    node x new edge
    node x removed an edge
    node x moved (got different name, for example from Node 2 is now Node 3)
    
initial version:
    node not found (no attempt for looking renamed or moved)
    different edge definition
    image differs
    edge image differs
'''
import os, sys, base64, uuid, traceback
from murphy.model import Model
from model_extraction.image2 import Image2
from PIL import Image

def read_binary_file(file_name):
    buff = ''
    with open(file_name, "rb") as a_file:
        byte = a_file.read(1)
        while byte != "":
            buff += byte
            byte = a_file.read(1)
    return buff

    
def get_node_image_b64(model, view, reference_image=False):
    if not reference_image:
        view_images = view['self'].HERE.get('snapshots', [])
    else:
        view_images = view['self'].HERE.get('reference snapshots', [])
    image1 = Image2(file_name="%s/%s" % (model.images_dir, view_images[0]))
    image1.image.save("tmp.png")
    return base64.b64encode(read_binary_file("tmp.png"))

    
def get_verb_image_b64(model, verb):
    if type(verb['how']) is dict and len(verb['how']['snapshots']) > 0:
        how = verb['how']['snapshots'][0]
        image1 = Image2(file_name="%s/%s" % (model.images_dir, how))
    else:
        image1 = Image.open(os.path.dirname(__file__) + "/noimageavailable.png")
        image1 = Image2(image=image1)
        
    image1.image.save("tmp.png")
    return base64.b64encode(read_binary_file("tmp.png"))                
    

EDGE_DIFFERENCE_TEMPLATE = '''
    %(title)s<br>
    <table style='text-align:center'>
        <tr>
            <td>
                <img src='data:image/png;base64,%(node_image)s'>
                <br>%(node_name)s
            </td>
            <td nowrap>&rarr;</td>
            <td>
                <img src='data:image/png;base64,%(edge_image)s'>
                <br>%(edge_name)s
            </td>
            <td nowrap>&rarr;</td>
            <td>
                <img src='data:image/png;base64,%(head_image)s'>
                <br>%(head_name)s
            </td>
        </tr>
    </table>
    <br>
'''
    
    
class ModelComparison(object):

    def __init__(self, model_file_name, reference_model_file_name):
        self.model = Model(model_file_name)
        self.reference_model = Model(reference_model_file_name)


    def _get_ordered_views(self, model):
        namespace = model.model['namespace']
        ordered_views = []
        for name in model.model['modules']:
            module = sys.modules['%s.%s' % (namespace, name)]
            ordered_views.append(module.HERE['desc'])
        return ordered_views
        
        
    def compare_view(self, view, reference_view):
        return ''

    def compare_edges(self, view, reference_view, reference_translation):
        result = ''
        for name, verb in view['verbs'].items():
            if not name in reference_view['verbs']:
                result += "Edge '%s' does not exists in reference model (new?)<br>\n" % name
            else:
                reference_verb = reference_view['verbs'][name]
                dest = verb.get('goes to', '')
                reference_dest = reference_verb.get('goes to', '')
                #print "dest %s, reference dest %s translation %s" % (dest, reference_dest, str(reference_translation))
                #fixme translate something when drawing???
                #fixme search edge by screenshot if available, by name if it is not
                if not dest in reference_translation:
                    head = self.model.new_worker().get_views()[verb['goes to']]
                    result += EDGE_DIFFERENCE_TEMPLATE % {'title': 'New edge?',
                                      'node_image': get_node_image_b64(self.model, view, True),
                                      'node_name': view['self'].HERE['desc'],
                                      'edge_image': get_verb_image_b64(self.model, verb),
                                      'edge_name': name,
                                      'head_image': get_node_image_b64(self.model, head, True),
                                      'head_name': head['self'].HERE['desc']}
                elif reference_translation[dest] != reference_dest:
                    #result += "Edge '%s' goes to '%s' in model but goes to '%s' in reference model<br>\n" % (name, dest, reference_dest)
                    id1 = str(uuid.uuid1())
                    id2 = str(uuid.uuid1())
                    result += "<input type='checkbox' onchange='javascript:change_visibility(\"" + id1 + "\", \"" + id2 + "\");'>"
                    result += "Show parametrized images<br>"
                    for i in range(2):
                        if i == 0:
                            result += "<div id='%s' style='display: none'>" % id1
                        else:
                            result += "<div id='%s'>" % id2
                        reference = (i != 0)
                        head = self.model.new_worker().get_views()[verb['goes to']]
                        result += EDGE_DIFFERENCE_TEMPLATE % {'title': 'Now:',
                                          'node_image': get_node_image_b64(self.model, view, reference),
                                          'node_name': view['self'].HERE['desc'],
                                          'edge_image': get_verb_image_b64(self.model, verb),
                                          'edge_name': name,
                                          'head_image': get_node_image_b64(self.model, head, reference),
                                          'head_name': head['self'].HERE['desc']}
                        head = self.reference_model.new_worker().get_views()[reference_verb['goes to']]
                        result += EDGE_DIFFERENCE_TEMPLATE % {'title': 'Before:',
                                          'node_image': get_node_image_b64(self.reference_model, reference_view, reference),
                                          'node_name': reference_view['self'].HERE['desc'],
                                          'edge_image': get_verb_image_b64(self.reference_model, reference_verb),
                                          'edge_name': name,
                                          'head_image': get_node_image_b64(self.reference_model, head, reference),
                                          'head_name': head['self'].HERE['desc']}
                        result += '</div>'
                        
                    
        for name, verb in reference_view['verbs'].items():
            #FIXME: translation missing
            if not name in view['verbs']:
                #FIXME: add image
                result += "Edge '%s' does not exists in model (removed?)<br>\n" % name

        if result != '':
            result = "Edges in node '%s' differs from the reference model.<br>\n%s" % (view['self'].HERE['desc'], result)
            
        return result

    
    def find_node_by_image(self, model, view, reference_model, reference_views):
        ordered_views = self._get_ordered_views(reference_model)
        for view_name in ordered_views:
            result = self.compare_view_images(model,
                                              view,
                                              reference_model,
                                              reference_views[view_name])
            if result == '':
                return reference_views[view_name]
        return None
    
        
    def compare_view_images(self, model, view, reference_model, reference_view):
        #we compare parametrized images, otherwise dates and times will not match
        view_images = view['self'].HERE.get('snapshots', [])
        reference_view_images = reference_view['self'].HERE.get('snapshots', [])

        if len(view_images) != len(reference_view_images):
            return 'Node "%s" has %s snapshots but the reference node has %s' % (view['self'].HERE['desc'],
                                                                                 len(view_images),
                                                                                 len(reference_view_images))

        result = ''
        for index in range(len(view_images)):
            image1 = Image2(file_name="%s/%s" % (model.images_dir,
                                                 view_images[index]))
            image2 = Image2(file_name="%s/%s" % (reference_model.images_dir,
                                                 reference_view_images[index]),
                            tolerance=0.9999)
            if image1 != image2:
                result += 'Node "%s", image "%s" differs from reference node "%s"<br>\n' % (view['self'].HERE['desc'],
                                                                                          view_images[index],
                                                                                          reference_view_images[index])
                image1.image.save("tmp.png")
                encoded1 = base64.b64encode(read_binary_file("tmp.png"))
                image2.image.save("tmp.png")
                encoded2 = base64.b64encode(read_binary_file("tmp.png"))
                id1 = str(uuid.uuid1())
                id2 = str(uuid.uuid1())
                result += "<table>\n\t<tr>\n\t\t<td><img id='%s' title='model' src='data:image/png;base64,%s'></td>\n" % (id1, encoded1)
                result += "\t\t<td><input style='font-family:\"Courier New\", Courier, monospace;' type=button id='button-%s' value='<-    New      \n   Reference ->' onclick='swap(\"%s\", \"%s\")'></td>\n" % (id1, id1, id2)
                result += "\t\t<td><img id='%s' title='reference' src='data:image/png;base64,%s'></td>\n\t</tr>\n</table><br>\n" % (id2, encoded2)
                
        return result


    def compare(self):
        views = self.model.new_worker().get_views()
        reference_views = self.reference_model.new_worker().get_views()

        matching_views = []
        candidate_for_moved = []
        moved_views = []
        candidate_for_new = []
        changed_views = []
        new_views = []
        reference_views_used = []

        #dictionary of moved nodes, key is model view nam, value is reference view name
        reference_translation = {}
        reference_translation[''] = ''
        result = ''
        ordered_views = self._get_ordered_views(self.model)
        for view_name in ordered_views:
            view = views[view_name]
            if view_name in reference_views:
                reference_view = reference_views[view_name]
                comparison = self.compare_view_images(self.model, view, self.reference_model, reference_view)
                if comparison == '':
                    matching_views.append(view)
                    reference_views_used.append(reference_view)
                    reference_translation[view_name] = view_name
                else:
                    candidate_for_moved.append(view)
            else:
                candidate_for_moved.append(view)

                        
        for view in candidate_for_moved:
            candidate = self.find_node_by_image(self.model, view, self.reference_model, reference_views)
            if candidate and not candidate in reference_views_used:
                moved_views.append({'view': view, 'reference view': candidate})
                reference_views_used.append(candidate)
                reference_translation[view['self'].HERE['desc']] = candidate['self'].HERE['desc']
            else:
                candidate_for_new.append(view)
                
        for view in candidate_for_new:
            view_name = view['self'].HERE['desc']
            if view_name in reference_views and not reference_views[view_name] in reference_views_used:
                #can this still be wrong?
                changed_views.append(view)
                reference_views_used.append(reference_views[view_name])
                reference_translation[view_name] = view_name
            else:
                new_views.append(view)
            
        #print "Translation table: %s" % str(reference_translation)
        
        for view in matching_views:
            reference_view = reference_views[view['self'].HERE['desc']]
            result += self.compare_edges(view, reference_view, reference_translation)

        for movement in moved_views:
            result += "Node '%s' is in reference model as %s<br>\n" % (movement['view']['self'].HERE['desc'],
                                                                   movement['reference view']['self'].HERE['desc'])
            result += self.compare_edges(movement['view'], movement['reference view'], reference_translation)
    
        for view in changed_views:
            result += self.compare_view_images(self.model,
                                                view,
                                                self.reference_model,
                                                reference_views[view['self'].HERE['desc']])
    
        for view in new_views:
            result += "Node '%s' is new, does not seems to exist in the reference model<br>\n" % (view['self'].HERE['desc'])
            view_images = view['self'].HERE.get('snapshots', [])
            if len(view_images) > 0:
                image = Image2(file_name="%s/%s" % (self.model.images_dir, view_images[0]))
                image.image.save("tmp.png")
                encoded = base64.b64encode(read_binary_file("tmp.png"))
                result += "<img src='data:image/png;base64,%s' title='model'><br>\n" % encoded

        for view in reference_views.values():
            if not view in reference_views_used:
                result += "Reference node '%s' does not seem to exists in the model (was removed?)<br>\n" % (view['self'].HERE['desc'])
                view_images = view['self'].HERE.get('snapshots', [])
                if len(view_images) > 0:
                    image = Image2(file_name="%s/%s" % (self.reference_model.images_dir, view_images[0]))
                    image.image.save("tmp.png")
                    encoded = base64.b64encode(read_binary_file("tmp.png"))
                    result += "<img src='data:image/png;base64,%s' title='model'><br>\n" % encoded

        return result

        
def compare(model, reference):
    text = "<html>\n<body>"
    #include swap js
    text += '''
    <script>
    function swap(id1, id2) {
        img1 = document.getElementById(id1);
        src1 = img1.src;
        title1 = img1.title;
        img2 = document.getElementById(id2);
        img1.src = img2.src;
        img1.title = img2.title;
        img2.src = src1;
        img2.title = title1;
        button = document.getElementById('button-' + id1);
        if (button.value.indexOf('<-') === 0) {
            button.value = '      New    ->\\n<- Reference   ';
        } else {
            button.value = '<-    New      \\n   Reference ->';
        }
    }
    function change_visibility(id1, id2) {
        var elem1 = document.getElementById(id1);
        var elem2 = document.getElementById(id2);
        if (elem1.style.display === 'none') {
            elem1.style.display = 'inline';
            elem2.style.display = 'none';
        } else {
            elem1.style.display = 'none';
            elem2.style.display = 'inline';
        }
    }
    </script>\n\n'''
    text += "Comparing %s against %s<br><br>\n" % (model, reference)
    comparer = ModelComparison(model, reference)
    result = comparer.compare()
    if result != '':
        text += result
    else:
        text += "No differences found.<br>"
    text += "\n</body>\n</html>"
    if result != '':
        return (2222, text)
    else:
        return (0, text)

        
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Use model_comparison.py model, reference_model"
        sys.exit(1)
        
    if not os.path.exists(sys.argv[1]):
        print "Model %s does not exists" % sys.argv[1]
        sys.exit(1)
    if not os.path.exists(sys.argv[2]):
        print "Model %s does not exists" % sys.argv[2]
        sys.exit(1)

    try:
        ret_code, ret_text = compare(sys.argv[1], sys.argv[2])
        print ret_text
    except Exception, ex:
        traceback.print_exc(file=sys.stdout)
        print "Wopsy, %s" % str(ex)

    
    sys.exit(ret_code)
