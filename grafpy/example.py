from grafpy import DAG, Node
import pickle

# Create a graph
d = DAG()

# Create some nodes
jobA = Node()
jobB = Node()
jobC = Node()
cmd1 = Node()
cmd2 = Node()
cmd3 = Node()
cmd4 = Node()
cmd5 = Node()
cmd6 = Node()
cmd7 = Node()

# Add the nodes to the graph (upcomming feature will allow us to combine the creation and adding)
d.add_node(jobA, 'Job A')
d.add_node(jobB, 'Job B')
d.add_node(jobC, 'Job C')
d.add_node(cmd1, 'Command 1')
d.add_node(cmd2, 'Command 2')
d.add_node(cmd3, 'Command 3')
d.add_node(cmd4, 'Command 4')
d.add_node(cmd5, 'Command 5')
d.add_node(cmd6, 'Command 6')
d.add_node(cmd7, 'Command 7')

# Describe the edges of the graph
d.add_edge("Job A", "Command 1")
d.add_edge("Command 1", "Command 4")
d.add_edge("Command 4", "Command 5")
d.add_edge("Command 5", "Command 7")
d.add_edge("Command 4", "Command 7")
d.add_edge("Job A", "Command 2")
d.add_edge("Command 2", "Job C")
d.add_edge("Job B", "Command 3")
d.add_edge("Command 3", "Job C")
d.add_edge("Job B", "Job C")
d.add_edge("Job C", "Command 6")


# Set some arbitrary data on our nodes.
jobA['foo'] = 'foo'
cmd2['foo'] = 'bar'
cmd3['foo'] = 'baz'

# With this line commented out, the graph will fail, as two nodes fight to set the value for key 'foo'
# This node explictitly overwrites foo, so no need to inherit its value
#jobC['foo'] = 'bif'


# Evaluate the DAG, and see if there are any errors
d.evaluate_dag()

printError = True
for node in sorted(d.errors.keys()):
	errors = d.errors[node]
	if len(errors) >= 1:
		if printError != False:
			print "Errors:"
			printError = False
		for error in errors:
			print "\t%s" % error


# Get the computed dictionary of data for each node
#d.evaluate_node("Job A")
#d.evaluate_node("Command 2")
#d.evaluate_node(cmd3)
#d.evaluate_node("Job C")


# Draw the graph using the graphviz library
d.show()

# Write our graph out to a file, then read it back
fp = 'example.dag'
d.write(fp)

fh = open(fp,'r')
D2 = pickle.load(fh)
fh.close()

for node in D2.get_nodes():
	print D2.get_label_from_node(node)
