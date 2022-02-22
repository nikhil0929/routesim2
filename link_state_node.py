from simulator.node import Node
import json

class Link_State_Node(Node):
    def __init__(self, id, src, dst, cost):
        super().__init__(id)
        #we are gonna need to init some things:
        # - since we are building a single node, lets set its sequence number
        self.seq_num = 0

        self.edges = dict() #can use frozensets to represent key, and the weights as values
        self.nodes = {self.id: 0}
        self.graph = {} #want to use graph representation

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
        message = {}
        pass

    # Fill in this function
    def process_incoming_routing_message(self, m):
        # called when message arrives at node
        # message sent by a neighbor as a string
        # response: 1. send further messages (if condition met)
        #           2. update forwarding tables

        pass

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # called when our simulator wants to know our next hop
        # response: consult forwarding table and return correct next node
        # return type: integer
        # How?
        #   - form routing tables from current information (can use graph representation)
        #   - run dijkstras to find shortest path
        #   - return next node in dijkstra path
        dist_vect, parent_vect = self.dijkstra((self.graph, self.id))
        path = self.find_path(parent_vect, destination, [])
        if len(path) < 2:
            return -1
        else:
            #return next node which corresponds to second index in path
            return path[1]


    #function to implement Djikstras Algorithm
    # adapted from https://www.geeksforgeeks.org/printing-paths-dijkstras-shortest-path-algorithm/
    def minDist(self, distance_vector, queue):
        #will find node with shortest path value and return index
        min_val = float("Inf")
        min_index = -1

        for i in range(len(distance_vector)):
            if distance_vector[i] < min_val and i in queue:
                min_val = distance_vector[i]
                min_index = i

        return min_index

    def dijkstra(self, graph, src):
        #not sure format we are gonna use yet, but this is quite simple
        # take in our network and the starting node?
        # return shortest paths between src and all nodes
        distance_vector = {}
        parent = {}
        max_val = float("Inf")

        for node_id in self.nodes:
            distance_vector[node_id] = max_val

        distance_vector[src] = 0

        #create queue to add all vertices too, order matters
        queue = []
        for node_id in self.nodes:
            queue.append(node_id)

        while queue:
            #find vertex with min distance in our queue
            min_index = self.minDist(distance_vector, queue)
            queue.remove(min_index)

            #must update our distances and parent values
            for next_index in self.nodes:
                #check if link has wieght and node is in queue
                if graph[min_index][next_index][1] != 0 and next_index in queue:
                    new_dist = distance_vector[min_index] + graph[min_index][next_index][1]
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
        if parent[dst] == -1:
            path.insert(0,dst)
        else:
            path.insert(0,dst)
            self.find_path(parent, parent[dst], path)

        return path