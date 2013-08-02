
import sys
import re
import fileinput
import os
import os.path
import pdb

class Graph():
	def __init__(self, call_map):
		self.nodes = call_map.get_keys()

		self.edges = {}
		for node in nodes:
			self.add_edge(node, call_map[node])

	def add_edge(self, u, v):
		self.edges[u] = v

class Parser():
	def _open_file(self, filename):
		if len(filename) <= 2:
			return False;

		if re.match("/.*", filename):
			filename = filename[1:]

		return open(filename, "r")

	def set_language(self, file_name):
		self.language = "C"

	def _starts_function(self, line):
		if len(line) < 3:
			return False
		return line[0:3] == "def"

	def identify_functions(self, file_name):
		file = self._open_file(file_name)
		if file is None:
			return None

		functions = []
		curr_function = []
		for line in file:
			if self._starts_function(line):
				if curr_function != []:
					functions.append(curr_function)
					curr_function = []
			curr_function.append(line)
		functions.append(curr_function)
		return functions

	def get_function_name(self, function):
		return function[0][
			str.find(function[0], ' ') + 1
			:
			str.find(function[0], ')') - 1
		]

	def get_called_names(self, function):
		called_names = []
		for line in function[1:]:
			if str.find(line, '(') != -1:
				called_name = line[
					str.find(line, '(') - 1
					:
					str.find(line, ')') - 1
				]
				called_names.append(called_name)
		return called_names

class AbstractionFinder():
	def __init__(self):
		pass

	def _create_map_of_calls(self, parser, functions):
		calls = {}
		for function in functions:
			calls[parser.get_function_name(function)] = \
				parser.get_called_names(function)
		return calls

	def _gen_powerset(self, src, so_far=[]):
		if src == []:
			return [so_far]

		elem = src[0]
		src = src[1:]

		subsets = []
		subsets += self._gen_powerset(src, so_far.append(elem), all_subsets)
		subsets += self._gen_powerset(src, so_far, all_subsets)
		return subsets

	def _identify_independent_unions(self, self_contained_sets):
		unions = {}
		seen_unions = set()
		for s1 in self_contained_sets.iterkeys():
			for s2 in self_contained_sets.iterkeys():
				if (s2 not in self_contained_sets[s1] and \
					s1 not in self_contained_sets[s2]
				):
					union = frozenset([s1, s2])
					if union not in seen_unions:
						seen_unions.add(union)
						unions[s1 + ',' + s2] = set.union(
							self_contained_sets[s1],
							self_contained_sets[s2]
						)
		self_contained_sets.update(unions)

	# finds from node and all its siblings
	def _identify_self_contained_sets_from_node(self, node, edge_function, self_contained_sets, seen_nodes):
		if len(edge_function[node]) == 0:
			s = set()
			s.add(node)
			self_contained_sets[node] = s
			return s

		self_contained_sets_from_node = set()
		self_contained_sets_from_node.add(node)
		for adjacent_node in edge_function[node]:
			self_contained_sets_from_adjacent_node = \
				self._identify_self_contained_sets_from_node(
					adjacent_node,
					edge_function,
					self_contained_sets,
					seen_nodes
				)
			self_contained_sets_from_node = \
				self_contained_sets_from_node.union(
					self_contained_sets_from_adjacent_node
				)

		self_contained_sets[node] = self_contained_sets_from_node
		return self_contained_sets_from_node

	# NOTE: doesn't find independent ones
	# TODO: preprocess for cycles
	def _identify_self_contained_sets(self, edge_function):
		self_contained_sets = {}
		seen_nodes = set()
		for key in iter(edge_function):
			if key not in seen_nodes: # i.e. key is not a nth-degree child of a previous key
				self_contained_sets_from_node = \
					self._identify_self_contained_sets_from_node(
						key,
						edge_function,
						self_contained_sets,
						seen_nodes
					)
		self._identify_independent_unions(self_contained_sets)
		return self_contained_sets

	def _print_self_contained_sets(self, self_contained_sets):
		for self_contained_set in self_contained_sets:
			print self_contained_set,
			print ":",
			print self_contained_sets[self_contained_set]


	def find_abstractions(self, file_name):
		parser = Parser()
		parser.set_language(file_name)
		functions = parser.identify_functions(file_name)

		edge_function = self._create_map_of_calls(parser, functions)

		self_contained_sets = self._identify_self_contained_sets(edge_function)

		self._print_self_contained_sets(self_contained_sets)

def __main__():
	abstraction_finder = AbstractionFinder()
	abstraction_finder.find_abstractions(file_name="test.py")

__main__()