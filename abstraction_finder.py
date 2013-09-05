
import sys
import re
import fileinput
import os
import os.path
import pdb

class Parser():
	def _open_file(self, filename):
		if len(filename) <= 2:
			return False

		if re.match("/.*", filename):
			filename = filename[1:]

		return open(filename, "r")

	def set_language(self, file_name):
		extension = file_name[file_name.find('.'):]
		extension_map = {
			'.py'   : 'Python'
		}
		self.language = extension_map[extension]

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
					if self._starts_function(curr_function[0]):
						functions.append(curr_function)
					curr_function = []
			curr_function.append(line)
		#fencepost
		if curr_function != []:
			if self._starts_function(curr_function[0]):
				functions.append(curr_function)
		return functions

	def get_function_name(self, function):
		return function[0][
			str.find(function[0], ' ') + 1
			:
			str.find(function[0], ')') - 1
		]

	def _is_function_name(self, name):
		return (
			name != 'if' and
			name != 'while' and
			name != 'for'
		)

	def _walk_backwards_to_delimeter(self, line, i):
		original_i = i
		DELIMITERS = '{}[]();:\'"\\&|^#$! '

		i -= 1
		while (
		    i >= 0 and
		    (line[i] not in DELIMITERS or
		    i == original_i - 1)
		):
		    i -= 1
		i += 1
    
		return (line[i:original_i]).strip()

	def _flatten(self, l):
		return [
			item
			for sublist in l
			for item in sublist
		]

	def _get_called_function_names_from_line(self, line):
		open_bracket_indices = [
			i for i, ch in enumerate(line)
			if ch == '('
		]
		called_functions = [
			self._walk_backwards_to_delimeter(line, open_bracket_index)
			for open_bracket_index in open_bracket_indices
		]
		
		# we want (f,) because
		# later we'll collapse cycles into 
		# tuples of functions, and want
		# to have type-consistency.
		called_functions = [
			(f,) for f in called_functions
			if self._is_function_name(f)
		]
		return called_functions

	def get_called_function_names_from_function(self, function):
		called_names = []
		for line in function[1:]:
			called_names_from_line =\
				self._get_called_function_names_from_line(line)
			called_names.append(called_names_from_line)
		called_names = self._flatten(called_names)
		return called_names

class AbstractionFinder():
	def __init__(self):
		pass

	def _create_map_of_calls(self, parser, functions):
		calls = {}
		for function in functions:
			called_functions =\
				parser.get_called_function_names_from_function(function)
			f_name = parser.get_function_name(function)
			f_name = (f_name,)
			calls[f_name] = \
				called_functions

			for f in called_functions:
				f = (f[0],)#
				if f not in calls.iterkeys():
					#to account for library functions -- will be overriden later by function definition, if exists (later in iteration)
					#TODO: `if f not in defined_functions` 
					calls[f] = []
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

	def _is_independent(self, curr_node, so_far, self_contained_sets_const):
		for already_neighbored_node in so_far:
			if curr_node in self_contained_sets_const[already_neighbored_node]:
				return False
		return True

	def _identify_independent_unions2(self, self_contained_sets):
		unions = self._identify_independent_unions2_rec(self_contained_sets, self_contained_sets.copy())
		self_contained_sets.update(unions)

	def _identify_independent_unions2_rec(self, self_contained_sets_const, self_contained_sets, so_far = [], unions = {}):
		if len(self_contained_sets) == 0:
			nodes = tuple()
			union = set()
			for node in so_far:
				nodes += node
				union.add(node)
			if len(so_far) != 0:
				unions[nodes] = union
			return

		curr_node = self_contained_sets.popitem()[0]
		before_recursion = self_contained_sets.copy()
		self._identify_independent_unions2_rec(self_contained_sets_const, self_contained_sets, so_far, unions)
		self_contained_sets = before_recursion

		if self._is_independent(curr_node, so_far, self_contained_sets_const):
			so_far_copy = so_far[:] + [curr_node]
			self._identify_independent_unions2_rec(self_contained_sets_const, self_contained_sets, so_far_copy, unions)

		return unions


	def _identify_independent_unions(self, self_contained_sets):
		unions = {}
		seen_unions = set()
		for s1 in self_contained_sets.iterkeys():
			for s2 in self_contained_sets.iterkeys():
				if (s2 not in self_contained_sets[s1] and \
					s1 not in self_contained_sets[s2]
				):
					union = frozenset([s1, s2]) #still using this?
					if union not in seen_unions:
						seen_unions.add(union)
						unions[s1 + s2] = list(
							set.union(
								self_contained_sets[s1],
								self_contained_sets[s2]
							)
						)
		self_contained_sets.update(unions)

	# finds from node and all its siblings
	# TODO: edge_function should be an ivar
	def _identify_self_contained_sets_from_node(
		self,
		node,
		edge_function,
		self_contained_sets,
		seen_nodes
	):
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

	def _remove_functions_in_cycle_from_list(
		self,
		called_functions_from_cycle,
		cycle
	):
		filtered_functions = []
		for outward_edge in called_functions_from_cycle:
			if outward_edge not in cycle:
				filtered_functions.append(outward_edge)
		return filtered_functions

	def _get_functions_called_from_cycle(self, edge_function, cycle):
		called_functions_from_cycle = [
			edge_function[pack_key(function_in_cycle)]
			for function_in_cycle in cycle
		]

		called_functions_from_cycle = flatten(called_functions_from_cycle) # Is there a better way? Shouldn't have to manually do this...
		cycle = [pack_key(e) for e in cycle]
		called_functions_from_cycle =\
			self._remove_functions_in_cycle_from_list(
				called_functions_from_cycle,
				cycle
			)
		return called_functions_from_cycle

	#too long
	def _collapse_cycle(self, edge_function, cycle):
		called_functions_from_cycle =\
			self._get_functions_called_from_cycle(edge_function, cycle)

		if len(cycle) == 1:
			edge_function[tuple(cycle)] = [] #otherwise[()]
		else:
			edge_function[tuple(cycle)] = called_functions_from_cycle

		cycle_as_set = set(cycle) #TODO: in params

		#TODO: faster? With a parent map...
		for node in edge_function.iterkeys():
			#remap nodes with edges to nodes in cycle
			neighbors = edge_function[node]
			modified_neighbors = []
			has_edge_to_cycle = False
			for neighbor in neighbors:
				neighbor = unpack_value(neighbor)
				if neighbor not in cycle:
					modified_neighbors.append(neighbor)
				else:
					has_edge_to_cycle = True
			#^ a parentmap eliminates this forloop and nodes that fail this step.

			if has_edge_to_cycle:
				valid_neighbors = []
				for neighbor in neighbors:
					if unpack_value(neighbor) not in cycle_as_set:
						valid_neighbors.append(neighbor)
				valid_neighbors.append(tuple(cycle))
				edge_function[node] = valid_neighbors			

	def _identify_cycles_from_node(
		self,
		node,
		edge_function,
		cycles = [],
		seen_nodes = []
	):
		if (type(node) == tuple and len(node) == 1):
			node = unpack_key(node)

		if node in seen_nodes: #TODO: can have parallel set?
			cycle_start_index = seen_nodes.index(node)
			cycle = seen_nodes[cycle_start_index:]
			cycles.append(cycle)
			return
		seen_nodes.append(node)

		if (type(node) == list):
			#HACK -- instead change domaintype to [tuple], not [[]]
			node = tuple(node)
		else:
			if not (type(node) == tuple and len(node) != 1):
				node = pack_key(node)
	
		for adjacent_node in edge_function[node]:
			adjacent_node = unpack_value(adjacent_node)
			seen_copy = seen_nodes[:]
			self._identify_cycles_from_node(
				adjacent_node,
				edge_function,
				cycles,
				seen_copy
			)

		return cycles

	def _all_neighbors_seen(self, seen, node, edge_function):
		# Is there a more 'Python' way to do this?
		all_neighbors_seen = True
		for neighbor in edge_function[node]:
			neighbor = neighbor[0]#unpack
			if neighbor not in seen:
				all_neighbors_seen = False
		return all_neighbors_seen


	def _identify_cycles_to_collapse(self, edge_function):
		seen = set()
		cycles_to_collapse = []
		seen_cycles = set()
		for node in edge_function.iterkeys():
			if (node in seen or 
				self._all_neighbors_seen(seen, node, edge_function)
			):
				continue

			cycles_from_node =\
			self._identify_cycles_from_node(
				node,
				edge_function,
				[],
				[] #TODO: why do we need this? Should be auto-initialized...
			)
			if len(cycles_from_node) != 0:
				seen.add(node)#not one line above? Optimization?
				for cycle_from_node in cycles_from_node:
					if frozenset(cycle_from_node) not in seen_cycles:
						seen_cycles.add(frozenset(cycle_from_node))
						cycles_to_collapse.append(cycle_from_node)
						for node_in_cycle_from_node in cycle_from_node:
							seen.add(node_in_cycle_from_node)

		return cycles_to_collapse

	def _identify_nodes_to_clean_up(
		self,
		cycles
	):
		#TODO: deduping
		nodes_to_clean_up = set()
		for cycle in cycles:
			if len(cycle) != 1: #1-cycles don't change in the map
				for node in cycle:
					nodes_to_clean_up.add(pack_key(node))
		return nodes_to_clean_up

	def _clean_up_nodes(self, edge_function, cycles):
		#Cycles should be a set?
		nodes_to_clean_up = self._identify_nodes_to_clean_up(
			cycles
		)
		for node in nodes_to_clean_up:
			del edge_function[node]

	def _collapse_cycles(self, edge_function):
		collapsing_occurred = True
		while (collapsing_occurred):
			collapsing_occurred = self._collapse_cycles_one_iteration(
				edge_function
			)

	def _collapse_cycles_one_iteration(self, edge_function):
		cycles_to_collapse = self._identify_cycles_to_collapse(edge_function)
		for cycle_to_collapse in cycles_to_collapse:
			self._collapse_cycle(edge_function, cycle_to_collapse)

		self._clean_up_nodes(edge_function, cycles_to_collapse)

		return len(cycles_to_collapse) != 0

	def _remove_mappings_with_range_of_size_1(self, mapping):
		todel = []
		for e in mapping.iterkeys():
			if len(mapping[e]) == 1:
				todel.append(e)
		for e in todel:
			del mapping[e]

	def _identify_self_contained_sets(self, edge_function):
		self._collapse_cycles(edge_function)

		#TODO: decomp
		self_contained_sets = {}
		seen_nodes = set()
		for node in edge_function.iterkeys():
			if node not in seen_nodes: # i.e. node is not a nth-degree child of a previous key //works?
				self_contained_sets_from_node =\
					self._identify_self_contained_sets_from_node(
						node,
						edge_function,
						self_contained_sets,
						seen_nodes
					)
					# doesn't look like it's going to keep old parts (clarity)
					# TODO: only abstract those that call others?

		self._identify_independent_unions2(self_contained_sets)

		self._remove_mappings_with_range_of_size_1(self_contained_sets)
		return self_contained_sets

	def _print_self_contained_sets(self, self_contained_sets):
		for self_contained_set in self_contained_sets:
			print "rooted at <",
			print self_contained_set,
			print ">: ",#\n\t\t\t",
			print list(self_contained_sets[self_contained_set])


	def find_abstractions(self, file_name):
		parser = Parser()
		parser.set_language(file_name)
		functions = parser.identify_functions(file_name)

		edge_function = self._create_map_of_calls(parser, functions)

		self_contained_sets = self._identify_self_contained_sets(edge_function)

		self._print_self_contained_sets(self_contained_sets)

def printmap(map):
	for k in map:
		print '\t\tmap[', k, '] : ', map[k]
	print ''

#utils?
def flatten_rec(l, to_fill):
	if (type(l) != list):
		to_fill.append(l)
		return
	
	for e in l:
		flatten_rec(e, to_fill)

def flatten(l):
	flattened = []
	flatten_rec(l, flattened)
	return flattened

#TODO: abstractify all these below into a map wrapper class
#assumption: tuple with one element
def unpack_key(key):
	return key[0]

#assumption: tuple with one element
def pack_key(key):
	return (key,)

#assumption: list with one element
def unpack_value(value):
	if len(value) == 1:
		return value[0]
	else:
		return value

#assumption: list with one element
def pack_value(value):
	return [value]

def __main__():
	if len(sys.argv) != 2:
		print "Pass exactly one argument (the file-name), please."
		return
	file_name = sys.argv[1]

	abstraction_finder = AbstractionFinder()
	abstraction_finder.find_abstractions(file_name)

__main__()