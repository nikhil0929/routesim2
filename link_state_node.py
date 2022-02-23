from simulator.node import Node
import json

class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        #we are gonna need to init some things:
        # - since we are building a single node, lets set its sequence number

        self.edges = dict() #can use frozensets to represent key, and the weights as values
        self.nodes = {self.id: 0}


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

        #update our set of edges
        node_pair = frozenset([self.id, neighbor])
        if node_pair in self.edges:
            sequence_num = self.edges[node_pair]['sequence num'] + 1
        else:
            sequence_num = 0

        #if node_pair not in self.edges:
        self.build_link(node_pair, latency, sequence_num)
         # edges[1][2] = 3 means that the link btwn Node 1 and 2 has a latency of 3

    #this function simply forms our json message to be sent
    def form_message(self, edge):
        return json.dumps((list(edge), self.edges[edge]['latency'], self.edges[edge]['sequence num']))

    # this function will build the edge link between two nodes, and send update messages
    def build_link(self, node_pair, latency, sequence_num):

        #if node_pair not in self.edges:
        self.create_edge(node_pair, latency, sequence_num)

        for node in node_pair:
            # checking both parent nodes of this edge
            if node not in self.nodes:
                # this means one of the nodes is new
                for n_pair in self.edges.keys():
                    # must send update to that node with edge broadcast
                    self.send_to_neighbor(node, self.form_message(n_pair))
            # check if node is self
            if node != self.id:
                #if not set distance to infinity
                self.nodes[node] = float('inf')
            else:
                self.nodes[node] = 0

        # send our message in json format
        self.send_to_neighbors(self.form_message(node_pair))

    #function to create a new edge with given latency and sequence num
    def create_edge(self, node_pair, latency, seq_num):
        #print("creating edge between " + str(node_pair) + "with latency " + str(latency))
        self.edges[node_pair] = {"latency" : latency, "sequence num" : seq_num}

    # Fill in this function
    def process_incoming_routing_message(self, m):
        # called when message arrives at node
        # message sent by a neighbor as a string
        # response: 1. send further messages (if condition met)
        #           2. update forwarding tables

        # First check if this message (packet) is in our message list
        # if our message is already there (dup) -> drop message
        # else -> duplicate message, and forward to all neighbors (update routing tables)

        edge, latency, seq_num = json.loads(m)
        edge = frozenset(edge)


        if edge not in self.edges or (self.edges[edge]['sequence num'] < seq_num):
            self.build_link(edge, latency, seq_num)

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # called when our simulator wants to know our next hop
        # response: consult forwarding table and return correct next node
        # return type: integer
        # How?
        #   - form routing tables from current information (can use graph representation)
        #   - run dijkstras to find shortest path
        #   - return next node in dijkstra path

        #PROBLEM (SOLVED)
        # currently the distance vector computation is incorrect
        # we see that from Node 18 to Node 4, our algorithm computes a shortest distance of 12
        # in reality you can go around and the shortest distance is 11
        # PARENT vector for 4 should not be 8
        # its taking the frist one of our parent vector, but we should really check the latencies of the connections.
        dist_vect, parent_vect = self.dijkstra_routing()
        #print("===============")
        #print("Distance Vector, Parent Vector")
        #print(dist_vect)
        #print(parent_vect)
        #print(destination)
        #print("===============")


        path = self.find_path(parent_vect, destination, [])
        print(path)
        print("===============")
        if len(path) < 2:
            return -1
        else:
            #return next node which corresponds to second index in path
            return path[1]


    # functions to implement Djikstras Algorithm (GRAPH REPRESENTATION)
    # adapted from Pseudocode on in Lecture 10 Slide 29
    # START OF REFERENCE

    def dijkstra_routing(self):
        #not sure format we are gonna use yet, but this is quite simple
        # take in our network and the starting node?
        # return shortest paths between src and all nodes

        parent = {}
        distance_vector = {}

        for ind in self.nodes:
            parent[ind] = -1
            distance_vector[ind] = float("Inf")

        distance_vector[self.id] = 0

        #create queue to add all vertices too
        queue = []
        for node_id in self.nodes:
            queue.append(node_id)

        while queue:
            #find vertex with min distance in our queue
            min_index = None
            for node in queue:
                if min_index is None:
                    min_index = node
                elif distance_vector[node] < distance_vector[min_index]:
                    min_index = node

            #remove this index so we dont check a link between a single vertex
            queue.remove(min_index)

            #now we go through the neighbors
            for next_index in self.nodes:
                #check if link has wieght and node is in queue

                #find index for our edges dictionary
                ind = frozenset([min_index, next_index])

                if ind in self.edges:
                    alt_latency = self.edges[ind]['latency']
                    alt = distance_vector[min_index] + alt_latency
                    #if we find it to be smaller, update or original values
                    if alt < distance_vector[next_index]:
                        distance_vector[next_index] = alt
                        parent[next_index] = min_index

        #return our distance vector and parent vector
        return distance_vector, parent


    #function to find shortest path from our dictionaries
    def find_path(self, parent, dst, path):
        #returns shortest path from source to destination

        if parent[dst] == -1:
            path.insert(0,dst)
        else:
            path.insert(0,dst)
            self.find_path(parent, parent[dst], path)

        return path
    #END OF REFERENCE
    #source: Lecture 12 Slide 29