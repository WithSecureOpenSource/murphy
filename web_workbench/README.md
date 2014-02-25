web_workbench
=============

A web user interface for advanced murphy functionality like exploratory
testing functionality, coverage report, screenshot and model visualization and
much more.

To use it you need to have murphy installed and it's dependencies, then simply
launch web_workbench.py, it embeds a simple web server and can be easily
plugged with multiuser web servers like cherry and others as it is based in
bottle.py

Edit projects.json as appropriate for configuring the models available thru
web.

The directory 'projects' is dynamically populated when the projects configured
in 'projects.json' are accessed thru web, it is not meant to be used for actually
storing your model projects, be mindfull that over time piles up some garbage,
simply delete the directories there and they will be recreated once a user access
a model.

At the moment many things are 'in transition' from the old 'murphy_web' into the
new 'web_workbench.py' so it is quite messy at the moment, not all functionality
is yet ported.
