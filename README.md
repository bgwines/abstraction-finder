abstraction-finder
==================

abstraction-finder is a program to do static analysis on code to find of abstractable sets of functions.

The main idea is that abstractions work by hiding implementation details -- here, the heuristic provided for abstraction-classification is if all the functions in the encapsulation don't call any functions but each other (except for library functions, here interpreted as functions not defined in the given file). 

The code can handle recursion of arbitrary order, and finds cycles by an algorithm similar to Tarjan's algorithm. It then collapses the cycles before finding abstractable sets of functions. 

Then, the algorithm finds sets of functions that don't call any other non-library functions through DFS. 

Functions that don't call each other and don't have any children of any depth that call each other or the functions in question can also be bundled together; after all, they also fit our criteria. Thus, an exponential number of abstractions is possible (visualise a set where all functions are leaf-functions). 

The point of the program is to execute the algorithm, not to do complicated parsing on the input file, so the parser is rather limited.

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
