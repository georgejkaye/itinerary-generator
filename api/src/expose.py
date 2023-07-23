import sys

from database.expose import expose_all

expose_all(sys.argv[1])
