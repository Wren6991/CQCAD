#!/bin/bash

# Invoke python on a script every time it changes. Need to install inotify-tools
# (on Ubuntu). I also recommend installing fstl as an excellent STL viewer that
# can auto-watch files for updates.

while true; do
	clear
	echo "Watching $1 for changes. ^C to exit"
	echo "Running..."
	python3 $1 && echo "OK" || echo -n $'\a'
	inotifywait -qq -e close_write $1
done
