murphy
======

core murphy

works with python 2.7.3+ 32 bits, not tested on python 64 bits (may or may
not work, there's a custom dll that's 32 bits and may prevent it)

before using, set PYTHONPATH to the parent dir where murphy is, for example if
murphy is in C:\git_projs\murphy:
    set PYTHONPATH=C:\git_projs

Dependencies:
Murphy strives for minimum dependencies on external libraries, but some are
really unavoidable at the moment.

Core murphy (execution)
    python PIL (be sure to use python 32 bits with corresponding PIL 32 bits)
    if using vnc for remote execution (prefered way) you'll need Twisted
    (http://twistedmatrix.com/) which uses a reactor for networking
    (Twisted-12.3.0.win32-py2.7.msi)
    Twisted needs zope:
        install setuptools (setuptools-0.6c11.win32-py2.7.exe)
        install zope:
            \python27\scripts\easy_install zope.interface-4.0.3-py2.7-win32.egg
    
    
UI dependencies:
    you'll need graphviz installed (http://www.graphviz.org/) for generating the
    graphs

    
    
TODO:
A lot, but initially consolidate the model python object and fix the model
loading thingy, removing legacy stuff
Take into use a componentized version of UserAutomation done in the crawler

Important notice:

This software is *extremelly experimental* and in alpha quality, it's not ready
for production usage if you're not able to fix or develop further, there is
no long term commitment to future development, documentation is really minimal
and you'll need to look at the source code to figure out how to do many things.
No support is provided, but we hope to create a vibrant community to help
supporting it.
The framework uses test automation techniques, local web servers, virtual
machines and many 'moving parts', using it in a secure way is entirely your
responsibility, as a minimum we recommend to pay attention to firewall settings
on the ports the tool uses and the use of a reputable antivirus whenever the
tool is being used.
The tool has been used quite extensively in house and had produced valuable
results not only in test automation but also for our localization,
customization and marketing teams, that being said it is yet quite far from a
production quality tool.
All disclaimers aside, we hope you enjoy hacking around it.

More quick docs can be found in murphy/docs, overview.html is a good place to
get a crash intro into some of the things that can be done.

