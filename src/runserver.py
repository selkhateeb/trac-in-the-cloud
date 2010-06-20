#!/usr/bin/env python
# To change this template, choose Tools | Templates
# and open the template in the editor.

from google.appengine.tools.dev_appserver_main import main
import os
import sys

if __name__ == '__main__':
    arg = [os.curdir, "."]
    sys.exit(main(arg))
