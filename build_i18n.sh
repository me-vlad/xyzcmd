#!/bin/sh

PATH="/usr/bin:/usr/sbin:/bin:/sbin:/usr/local/bin:$HOME/bin"

find . -name \*.py -or -name \*.xyz | xargs pygettext.py -o ./locale/xyzcmd.pot

cd ./locale

for po in `find . -mindepth 1 -maxdepth 1 -type d`; do
    b=`basename $po`

    msgfmt.py -o $b/LC_MESSAGES/xyzcmd.mo \
	./$b/LC_MESSAGES/xyzcmd.po;
done
