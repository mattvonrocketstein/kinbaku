# http://code.activestate.com/recipes/577506-dijkstra-shortest-path-algorithm/
# Dijkstra Shortest Path Algorithm
# http://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
# FB - 201012201
class node:
    label = ''
    # adjacency list of the node
    neighbors = [] # list of nodes
    distances = [] # distances to neighbors
    # for Dijkstra
    prevNode = None
    totalDistance = 0
    # constructor
    def __init__(self, label):
        self.label = label
        self.neighbors = []
        self.distances = []
        self.prevNode = None
        self.totalDistance = 0

# find the shortest paths to all nodes recursively
def dijkstra(node):
    # visit all neighbors and update them if necessary
    while len(node.neighbors) > 0:
        n = node.neighbors.pop(0)
        d = node.distances.pop(0)
        if n.prevNode == None or n.totalDistance > d + node.totalDistance:
            n.prevNode = node
            n.totalDistance = d + node.totalDistance
        dijkstra(n)

# get the shortest path to the given node
def route(endNode):
    node = endNode
    labels = [endNode.label]
    # distances = []
    while node.label != node.prevNode.label:
        # distances.append(node.totalDistance - node.prevNode.totalDistance)
        node = node.prevNode
        labels.append(node.label)
    labels.reverse()
    return labels
    # distances.reverse()
    # return (labels, distances)

# create a graph
a = node('a')
b = node('b')
c = node('c')
d = node('d')
e = node('e')
f = node('f')
graph = (a, b, c, d, e, f)

# create bidirectional edges of the graph
edges = []
edges.append((a, b, 14))
edges.append((a, c, 9))
edges.append((a, d, 7))
edges.append((b, c, 2))
edges.append((b, f, 9))
edges.append((c, d, 10))
edges.append((c, e, 11))
edges.append((d, e, 15))
edges.append((f, e, 6))

# create adjaceny list of neighbors for each node
for edge in edges:
    edge[0].neighbors.append(edge[1])
    edge[0].distances.append(edge[2])
    edge[1].neighbors.append(edge[0])
    edge[1].distances.append(edge[2])

# print the graph
print 'The graph:'
print
for n in graph:
    print 'Node: ', n.label
    print 'Neighbors:'
    for i in range(len(n.neighbors)):
        print n.neighbors[i].label, n.distances[i]
    print

# find the shortest paths to all neighbors starting w/ the given node
startNode = a
print 'Route start node:', startNode.label
startNode.prevNode = startNode
dijkstra(startNode)

##print
##print 'The graph after Dijkstra:'
##print
##for n in graph:
##    print 'Node:', n.label
##    print 'totalDistance:', n.totalDistance
##    print 'prevNode:', n.prevNode.label
##    print

# print the shortest path to the given node
endNode = f
print 'Route end node:', endNode.label
print 'Route:', route(endNode)
print 'Total distance:', endNode.totalDistance
