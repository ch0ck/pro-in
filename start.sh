#!/bin/sh
python ~/sqlmap/sqlmapapi.py -s &
python web.py &
python proxy.py &
