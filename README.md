abstraction-finder
==================

Static analysis on code to find of abstractable sets of functions.

logic
=====

One heuristic for when one can decompose a set of functions into a class to hide implementation of helper functions is when the set doesn't contain any outgoing function calls. The program works by visualizing the functions and function calls as a graph: nodes and edges, correspondingly.

Independent sets of functions (that is, functions that don't call each other and don't have any children who call each other) can be bundled together; after all, this also qualifies as a set of nodes which don't have any outgoing edges. As a result, there is an exponetial number of possible abstractible sets.

input format
===========

The purpose of writing this program was for the fun of the cycle-collapsing algorithm (and for having a not-terrible heuristic for when to encapsulate a set of functions), not for the sake of writing a really fantastic parser. As a result, the parsing in this program is pretty limited. It recognizes functions defined as follows:

    def some_function():

and can recognize function calls like the following:

    called_function(some_param, some_other_called_function())

It will get confused with anything else (except for `if`-statements, `while`loops, and `for`loops) that contains the `(` and `)` characters, so any tuples will confuse it. So, for now, no running it on its source code ;)

run instructions
================

`cd` to the folder containing `abstraction-finder.py`. Run the following command:

    python abstraction-finder.py unittests/tests/testcollapse1.py

where `unittests/tests/testcollapse1.py` may be replaced by any file you like.