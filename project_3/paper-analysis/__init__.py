from inspect import getsourcefile
from os.path import dirname, abspath
import sys
current_dir = dirname(abspath(getsourcefile(lambda:0)))
sys.path.insert(0, dirname(current_dir))
