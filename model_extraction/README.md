model_extraction
================

Extracts an application behaviour and dialogs into a murphy friendly model.

Needs murphy installed along with it's dependencies for it to work.

See the project 7zip_modeller in github for a very basic example of usage


The crawling, ui graph and ui scrap
-----------------------------------

The crawling process is a generic crawler, it will try to visit everything
except for what is told to not to visit, the order itself cannot be altered in
another way for now.

the ui graph is composed by nodes and edges, in general a node will represent
a dialog, window or state of it, but is not limited in any way and can be in
fact represent an internal state without ui representation, we focus on the ui
but anything applies to anything that can be defined and recognized as 'state'

The scraping process:

When a new state (node) is being analized, a new node is created and the whole
process of defining it begins


create_node:

Is called from the crawling process as it moves forward the exploration
Hooks can be attached to it for customizing the behaviour, most hooks are
attached by index (discovery order) with the exception of the classify_node
or when a hook is installed for index -1 (applies to all nodes)

the flow goes as follow:

Node is created with a generic name
create_node hook is called if there's one attached to this node (by index), no further
    processing is done if this hook is used, it is expected that the script will do
    all the work needed
classify_node hook is called if there's one, this is called for all the nodes
    and is meant to be used for generic boundary detections or so, hence the
    name 'classify_node'
    if the hook returns False, no other hook is executed and the scraping ends
    there
pre_create_node_hook is called then, it is normally used for preparing a given
    state, for example pre enter some value to get some control active in the
    window, like user name / password, product code and so.
    If the hook returns False, no other hook is executed and the scraping ends
    there
    if there's a generic pre_create_node_hook (index -1) it is called BEFORE
    the pre_create_node_hook for the given index
    
if this is a node to be imported, then it is imported at this moment
if is not to be imported, then the generic ui scraping is performed at this point
post_create_node_hook is then called
if there's a generic post_create_node_hook (set with index -1) then it is
    called now AFTER calling post_create_node_hook for the current index
the node is 'formally parametrized' then, the area used by the edges in the ui
    is masked and the process of creating the node finishes
    
    
scrap_state: the generic ui scraping

will figure out the outside boundaries
will add a screenshot to reference_images field of the node
will add the bounding box coordinates to last_location field of the node
will then proceed to detect common ui controls and add them to the node as edges

In addition to using hooks to affect the behaviour there are ways to pass extra
information to the process as 'hints', there are scraper hints, node hints, local
and global hints (see the source code).

Why all this?
To be able to fine control the flow, detection and overcome imperfections in
the scraper. Examples:
pre enter a product code during installation of a product
enter user name and password needed for log in to some service
avoid performing a ui action that is currently not working or to direct the
flow of the exploration somewhere


The bads:

Using indexes for the hooks has a bad side effect, if the application changes
in a way that affects the flow the hook will most likely be executed in the
wrong node / state / window.
Alternatives are for example to use the classify_node hook and determine there
what customization to apply, it could for example decide based on the window
title, search if a specific image or text is inside of it, etc.
It is yet under investigation how to combine a 'reference model' with the
scraping process hooks as there's potential there to solve many of this issues


Fine, finer control:

During the scrape process anything can be done, for example a totally new node
can be created that represents an intermediate state, add an icon to the
desktop, customize / tweak an installed product, etc.


Extending the scrape process.

The recommended approach is to use the hooks, in most cases a generic
post_create_node_hook is the right place where you can detect things that went
undetected and also possibly remove faulty detections from the generic scraper.

Example, create a routine that recognizes a custom widget (for example using
a UIElement)
post_create_node_hook[-1] = my_func
In my_func, if the UIElement is detected, add it as an edge, maybe also
remove any edge detected by the scraper that overlaps your discovered widget

Alternatively, code a better and more generic scraper and please do share it!
It is expected that in the long run and thru continuous improvement it will
handle most cases, but the mere fact that it already detects a lot of things
right is already a big time saver.



