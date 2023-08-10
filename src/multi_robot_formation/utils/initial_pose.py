import random
import math
from ..utils.gabreil_graph import get_gabreil_graph_local
def dfs(node, visited, adjacency_matrix, component):
    visited[node] = True
    component.add(node)
    for neighbor, connected in enumerate(adjacency_matrix[node]):
        if connected and not visited[neighbor]:
            dfs(neighbor, visited, adjacency_matrix, component)

def find_weakly_connected_components(adjacency_matrix):
    num_nodes = len(adjacency_matrix)
    visited = [False] * num_nodes
    components = []

    for node in range(num_nodes):
        if not visited[node]:
            component = set()
            dfs(node, visited, adjacency_matrix, component)
            components.append(component)

    return components
def is_graph_balanced(adjacency_matrix):
    num_nodes = len(adjacency_matrix)

    for node in range(num_nodes):
        indegree = sum(adjacency_matrix[i][node] for i in range(num_nodes))
        outdegree = sum(adjacency_matrix[node][i] for i in range(num_nodes))

        if indegree != outdegree:
            return False

    return True
# Example adjacency matrix
adjacency_matrix = [
    [0, 1, 0, 1, 0],
    [0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0]
]

def check_valid_initial_graph(graph):
    valid=True
    connected_component=find_weakly_connected_components(graph)
    if len(connected_component)>1:
        valid=False
    if is_graph_balanced(graph)==False:
        valid=False
    return valid
def initialize_pose(num_robot, initial_max_range=5,initial_min_range=1):
    while True:
        pose_list = []
        for i in range(num_robot):
            while True:
                redo = False
                x = 2 * random.uniform(0, 1) * initial_max_range - initial_max_range
                y = 2 * random.uniform(0, 1) * initial_max_range - initial_max_range
                theta = 2 * math.pi * random.uniform(0, 1) - math.pi
                min_distance = float("inf")
                if i == 0:
                    pose_list.append([x, y, theta])
                    break
                for j in range(len(pose_list)):
                    distance = ((x - pose_list[j][0]) ** 2 + (y - pose_list[j][1]) ** 2) ** 0.5
                    if distance < initial_min_range:
                        redo = True
                        break
                    if min_distance > distance:
                        min_distance = distance
                if redo==True:
                    pose_list.append([x,y,theta])
                    break

        gabriel_graph=get_gabreil_graph_local(pose_list)
        if check_valid_initial_graph(gabriel_graph)==True:
            break
    return pose_list
# if __name__ == "__main__":
#     pose_list=initialize_pose(5)
#     print(pose_list)