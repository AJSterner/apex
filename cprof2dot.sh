#!/bin/bash

#
# Usage: gprof2dot.sh pyscript [args]
# Creates a cProfile file called pyscript.prof
# Creates a callgraph called pyscript.prof.png
#
# make sure gprof2dot is installed (pip install gprof2dot)
#

pyscript=$1
args=""
prefix=""
while [ "$2" != "" ]; do
	args="$args$prefix$2"
	prefix=" "
	shift
done

set -x	

python2 -m cProfile -o $pyscript.prof $pyscript $args
gprof2dot -f pstats $pyscript.prof | dot -Tpng -o $pyscript.prof.png
