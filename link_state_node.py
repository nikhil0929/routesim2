from simulator.node import Node
import json

class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        #we are gonna need to init some things:
        # - since we are building a single node, lets set its sequence number
        self.seq_num = 0
        #self.messages = {}

        self.edges = dict() #can use frozensets to represent key, and the weights as values


        self.nodes = {self.id : 0}
        #self.graph = {} #want to use graph representation

    # if we are using a graph representation, we need helper functions
    # 1. to add the edges to graph
    # 2. to remove edges from graph

    # Return a string
    def __str__(self):
        # called when wants to pring node state for debugging
        # response: sensible node information
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        # called when outgoing connected link has changed properties
        # response: want to update forwarding tables and send message out to neighbors
        # 1. form our message to sent to all neighbors
        # message contents: link source, link destination, seq num, link cost
        #if latency == -1:
            #a link was deleted, what to do?

        #message = {"link_src": self.id, "link_dst": neighbor, "seq_num": self.seq_num, "link_cost": latency}
        #increment seq num
        #self.seq_num += 1
        #update our set of edges
        print("update link")

        node_pair = frozenset([self.id, neighbor])
        #print(node_pair)

        if node_pair in self.edges:
            self.seq_num += 1
        else:
            self.seq_num = 0

        self.build_link(node_pair, latency)
         # edges[1][2] = 3 means that the link btwn Node 1 and 2 has a latency of 3



    #this function simply forms our json message to be sent
    def form_message(self, edge):
        return json.dumps((list(edge), self.edges[edge], self.seq_num))

    # this function will build the edge link between two nodes, and send update messages
    def build_link(self, edge, latency):
        print("build link")
        #set the latency of the link
        self.edges[edge] = latency

        for node in edge:
            # checking both parent nodes of this edge
            if node not in self.nodes:
                # this means one of the nodes is new
                for n_pair in self.edges:
                    # must send update to that node with edge broadcast
                    self.send_to_neighbor(node, self.form_message(n_pair))
            # check if node is self
            if node != self.id:
                #if not set distance to infinity
                self.nodes[node] = float('inf')
            else:
                self.nodes[node] = 0

        # send our message in json format
        self.send_to_neighbors(self.form_message(edge))

    # Fill in this function
    def process_incoming_routing_message(self, m):
        # called when message arrives at node
        # message sent by a neighbor as a string
        # response: 1. send further messages (if condition met)
        #           2. update forwarding tables

        # First check if this message (packet) is in our message list
        # if our message is already there (dup) -> drop message
        # else -> duplicate message, and forward to all neighbors (update routing tables)
        print("imcoming message")
        edge, latency, seq_num = json.loads(m)
        edge = frozenset(edge)
        #print(edge)

        if edge not in self.edges or (self.seq_num < seq_num):
            self.build_link(edge, latency)

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # called when our simulator wants to know our next hop
        # response: consult forwarding table and return correct next node
        # return type: integer
        # How?
        #   - form routing tables from current information (can use graph representation)
        #   - run dijkstras to find shortest path
        #   - return next node in dijkstra path

        #PROBLEM
        # currently the distance vector computation is incorrect
        # we see that from Node 18 to Node 4, our algorithm computes a shortest distance of 12
        # in reality you can go around and the shortest distance is 11
        # PARENT vector for 4 should not be 8
        # its taking the frist one of our parent vector, but we should really check the latencies of the connections.
        dist_vect, parent_vect = self.dijkstra_routing()
        print("===============")
        print("Distance Vector, Parent Vector")
        print(dist_vect)
        print(parent_vect)
        print(destination)
        print("===============")


        path = self.find_path(parent_vect, destination, [])
        print(path)
        print("===============")
        if len(path) < 2:
            return -1
        else:
            #return next node which corresponds to second index in path
            return path[1]


    # functions to implement Djikstras Algorithm (GRAPH REPRESENTATION)
    # adapted from https://www.geeksforgeeks.org/printing-paths-dijkstras-shortest-path-algorithm/
    # START OF REFERENCE
    def minDist(self, distance_vector, queue):
        #will find node with shortest path value and return index
        min_val = float("Inf")
        min_index = -1

        for i in range(len(distance_vector)):
            if distance_vector[i] < min_val and i in queue:
                min_val = distance_vector[i]
                min_index = i

        return min_index

    def dijkstra_routing(self):
        #not sure format we are gonna use yet, but this is quite simple
        # take in our network and the starting node?
        # return shortest paths between src and all nodes
        print("========================")
        print("dijkstras running")
        print(self.edges)
        print(self.nodes)
        print("========================")

        parent = {}
        distance_vector = {}

        #print(distance_vector)
        for ind in self.nodes:
            parent[ind] = -1
            distance_vector[ind] = float("Inf")

        distance_vector[self.id] = 0
        #print(parent)
        #create queue to add all vertices too, order matters
        queue = []
        for node_id in self.nodes:
            queue.append(node_id)

        #print(queue)

        while queue:
            #find vertex with min distance in our queue
            min_index = self.minDist(distance_vector, queue)
            queue.remove(min_index)

            #must update our distances and parent values
            for next_index in self.nodes:
                #check if link has wieght and node is in queue
                #print(min_index)
                #print(next_index)
                #checks to make sure its not looping itself
                if min_index != next_index:
                    ind = frozenset([min_index, next_index])
                    #print(ind)
                    #print(self.edges[ind])
                    if ind in self.edges and next_index in queue:
                        new_dist = distance_vector[min_index] + self.edges[ind]
                        if new_dist < distance_vector[next_index]:
                            #this means that we have found a shorter path, so we update our neighbor
                            distance_vector[next_index] = new_dist
                            parent[next_index] = min_index

        #return our distance vector and parent vector
        return distance_vector, parent


    #function to find shortest path from our dictionaries
    def find_path(self, parent, dst, path):
        #returns shortest path from source to destination

        #no parent?
        #print("=============")
        #print("Find Path")
        #print(parent)
        #print(dst)
       # print("=============")

        if parent[dst] == -1:
            path.insert(0,dst)
        else:
            path.insert(0,dst)
            self.find_path(parent, parent[dst], path)

        return path
    #END OF REFERENCE
    #source: https://www.geeksforgeeks.org/printing-paths-dijkstras-shortest-path-algorithm/