"""
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
"""

import os, sys, traceback
import wget

if __name__ == '__main__':
    if len(sys.argv) < 2:
        wget.report_error("Use runurl.py url")

    url = sys.argv[1]
    wget.wget(url)
    try:
        filename = url.split('/')[-1].split('#')[0].split('?')[0]
        os.system("start " + filename)
    except Exception, ex:
        msg = "Error while running url %s\n\n%s\n\n%s" % (str(url), str(ex), traceback.format_exc())
        wget.report_error(msg)
    