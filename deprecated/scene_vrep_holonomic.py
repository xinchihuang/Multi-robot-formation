"""
A scene template
author: Xinchi Huang
"""
import copy
import random
import sys
sys.path.append("/home/xinchi/catkin_ws/src/multi_robot_formation/src")
sys.path.append("/home/xinchi/catkin_ws/src/multi_robot_formation/src/multi_robot_formation")
print(sys.path)
from collections import defaultdict

from vrep import vrep_interface_holonomic as vrep_interface

from utils.gabreil_graph import get_gabreil_graph

from comm_data import SceneData
from recorder import Recorder
from controller_new import *


def get_vector_angle(v1,v2):
    theta=v1[2]
    v1=v1[:2]
    v2=v2[:2]
    vector1 = np.subtract(v2, v1)
    vector2=np.array([math.cos(theta),math.sin(theta)])

    dot_product = np.dot(vector1, vector2)
    magnitude_product = np.linalg.norm(vector1) * np.linalg.norm(vector2)
    inner_angle_rad = np.arccos(dot_product / magnitude_product)
    inner_angle_deg = np.degrees(inner_angle_rad)

    return inner_angle_deg

class SceneHolonomic:
    """
    Scene for multiple robots
    """

    def __init__(self,num_robot=5,desired_distance=2.0,initial_max_range=5,initial_min_range=1,max_sep_range=4,controller_type="ViT"):
        """
        robot_list: A list contains all robot in the scene
        []

        adjacency_list: A dict records robots' neighbor position and
        relative distance in gabreil graph
        {robot index:[(neighbor index, neighbor x, neighbor y,relative distance)..]..}

        client_id: A unique Id for the simulation environment
        """
        self.robot_list = []
        self.adjacency_list = defaultdict(list)
        self.position_list = None
        self.orientation_list = None
        self.client_id = vrep_interface.init_vrep()
        self.num_robot=num_robot
        self.desired_distance=desired_distance
        self.initial_max_range=initial_max_range
        self.initial_min_range=initial_min_range
        self.max_sep_range=max_sep_range
        # self.robot_platform = "vrep"
        # self.model_path="/home/xinchi/catkin_ws/src/multi_robot_formation/src/multi_robot_formation/saved_model/vit1.0.pth"
        # # self.model_path="/home/xinchi/saved_model_5.28/vit1.0.pth"
        # if controller_type=="ViT":
        #     self.controller = VitController(model_path=self.model_path,desired_distance=self.desired_distance)
        # elif controller_type=="Expert":
        #     self.controller = LocalExpertController(desired_distance=self.desired_distance)
        # for i in range(self.num_robot):
        #     self.add_robot_vrep(i,controller=self.controller)
        # self.reset_pose(self.initial_max_range, self.initial_min_range)


    def add_robot_vrep(self, robot_index,new_robot):
        """
        Add a robot in the scene
        :param robot_index: The robot index
        :return:
        """
        print(new_robot.controller.name)
        new_robot.index = robot_index
        new_robot.executor.initialize(robot_index, self.client_id)
        new_robot.sensor.client_id = self.client_id
        new_robot.sensor.robot_index = robot_index
        new_robot.sensor.robot_handle = new_robot.executor.robot_handle
        new_robot.sensor.get_sensor_data()
        self.robot_list.append(new_robot)
    def update_scene_data(self):
        """
        Update the adjacency list(Gabriel Graph) of the scene. Record relative distance

        """
        # print("Distance")
        node_num = len(self.robot_list)
        # collect robots' position in th scene
        position_list = []
        index_list = []
        orientation_list = []
        for i in range(node_num):
            index_list.append(self.robot_list[i].index)
            position = self.robot_list[i].sensor_data.position
            orientation = self.robot_list[i].sensor_data.orientation[-1]
            orientation_list.append(orientation)
            position_list.append(position)
        position_array = np.array(position_list)

        # Get Gabreil Graph
        gabriel_graph = get_gabreil_graph(position_array)

        # Create adjacency list
        new_adj_list = defaultdict(list)
        for i in range(node_num):
            for j in range(node_num):
                if gabriel_graph[i][j] == 1 and not i == j:
                    distance = (
                        (position_array[i][0] - position_array[j][0]) ** 2
                        + (position_array[i][1] - position_array[j][1]) ** 2
                    ) ** 0.5
                    new_adj_list[index_list[i]].append(
                        (
                            index_list[j],
                            position_array[j][0],
                            position_array[j][1],
                            distance,
                        )
                    )
        self.adjacency_list = new_adj_list
        self.position_list = position_list
        self.orientation_list = orientation_list
        # print("DISTANCE")
        # for r in self.adjacency_list:
        #     for n in self.adjacency_list[r]:
        #         print("edge:", r, n[0], "distance:", n[epoch5])
    def broadcast_all(self):
        """
        Send observations to all robots for GNN control
        Observations: (All robots' observation, adjacency_list)
        :return: None
        """
        output = SceneData()
        observation_list = []
        for robot in self.robot_list:
            # if robot.sensor_data==None:
            #     print("None")
            #     robot.get_sensor_data()
            observation = robot.sensor_data
            observation_list.append(observation)
        self.update_scene_data()

        output.observation_list = observation_list
        output.adjacency_list = self.adjacency_list
        output.position_list = self.position_list
        output.orientation_list = self.orientation_list
        for robot in self.robot_list:
            robot.scene_data = output
    def reset_pose(self,pose_list=None):
        """
        Reset all robot poses in a circle
        pose_list:[[pos_x,pos_y,theta],[pos_x,pos_y,theta]]
        height: A default parameter for specific robot and simulator.
        Make sure the robot is not stuck in the ground
        """
        if pose_list==None:

            while True:
                pose_list = []
                regenerate = False
                for i in range(self.num_robot):
                    while True:
                        redo = False
                        x = 2 * random.uniform(0,1) * self.initial_max_range - self.initial_max_range
                        y = 2 * random.uniform(0,1) * self.initial_max_range - self.initial_max_range
                        theta=2*math.pi*random.uniform(0,1)-math.pi
                        min_distance=float("inf")
                        if i==0:
                            pose_list.append([x, y, theta])
                            break
                        for j in range(len(pose_list)):
                            distance=((x-pose_list[j][0])**2+(y-pose_list[j][1])**2)**0.5
                            if distance<self.initial_min_range:
                                redo=True
                                break
                            if min_distance>distance:
                                min_distance=distance
                        if min_distance>self.max_sep_range:
                            redo=True
                            continue
                        temp_pose_list=copy.deepcopy(pose_list)
                        temp_pose_list.append([x,y,theta])
                        temp_gabreil=get_gabreil_graph(temp_pose_list)
                        for neighbor in range(len(temp_gabreil[i])):
                            if neighbor==i:
                                continue
                            if temp_gabreil[i][neighbor]==1:
                                vector1 = np.array([pose_list[neighbor][0]-x,pose_list[neighbor][1]-y])
                                vector2 = np.array([math.cos(theta), math.sin(theta)])
                                dot_product = np.dot(vector1, vector2)
                                magnitude_product = np.linalg.norm(vector1) * np.linalg.norm(vector2)
                                inner_angle_rad = np.arccos(dot_product / magnitude_product)
                                inner_angle_deg = np.degrees(inner_angle_rad)
                                if inner_angle_deg<60 or np.linalg.norm(vector1)>self.robot_list[0].sensor_range:
                                    redo = True
                                    break
                        if i>=2 and sum(temp_gabreil[i])<=2:
                            redo = True
                            continue
                        if redo==False:
                            pose_list.append([x,y,theta])
                            break
                gabreil_graph=get_gabreil_graph(pose_list)
                for i in range(len(gabreil_graph)):
                    if sum(gabreil_graph[i])<=2:
                        regenerate=True
                        break
                    # neighbor_list=[]
                    # print(gabreil_graph)
                    # for j in range(len(gabreil_graph)):
                    #     if i==j:
                    #         continue
                    #     if gabreil_graph[i][j]==1:
                    #         neighbor_list.append(pose_list[j])
                    #         gabreil_graph[i][j]=0
                    #         gabreil_graph[j][i]=0
                    #     if len(neighbor_list)==0:
                    #         theta = math.atan2(pose_list[i][1], pose_list[i][0])
                    #         pose_list[i][2] = theta
                    #
                    #     elif len(neighbor_list)==1:
                    #         v1x = neighbor_list[0][0] - pose_list[i][0]
                    #         v1y = neighbor_list[0][1] - pose_list[i][1]
                    #         theta = math.atan2(v1y, v1x)
                    #         pose_list[i][2] = theta
                    #
                    #     elif len(neighbor_list)>=2:
                    #         v1x = neighbor_list[0][0] - pose_list[i][0]
                    #         v1y = neighbor_list[0][1] - pose_list[i][1]
                    #         v2x = neighbor_list[1][0] - pose_list[i][0]
                    #         v2y = neighbor_list[1][1] - pose_list[i][1]
                    #         theta=(math.atan2(v1y,v1x)+math.atan2(v2y,v2x))/2
                    #         pose_list[i][2]=theta
                    #         break
                #final check
                for i in range(len(gabreil_graph)):
                    for j in range(len(gabreil_graph)):
                        if i==j:
                            continue
                        if gabreil_graph[i][j]==1:

                            edge1 = np.array([pose_list[j][0] - pose_list[i][0], pose_list[j][1] - pose_list[i][1]])
                            if np.linalg.norm(edge1)>self.robot_list[0].sensor_range:
                                regenerate = True
                                break
                            obsever1 = np.array([math.cos(pose_list[i][2]), math.sin(pose_list[i][2])])
                            dot_product = np.dot(edge1, obsever1)
                            magnitude_product = np.linalg.norm(edge1) * np.linalg.norm(obsever1)
                            inner_angle_rad = np.arccos(dot_product / magnitude_product)
                            inner_angle_deg_1 = np.degrees(inner_angle_rad)
                            edge2 = np.array([pose_list[i][0] - pose_list[j][0], pose_list[i][1] - pose_list[j][1]])
                            obsever2 = np.array([math.cos(pose_list[j][2]), math.sin(pose_list[j][2])])
                            dot_product = np.dot(edge2, obsever2)
                            magnitude_product = np.linalg.norm(edge2) * np.linalg.norm(obsever2)
                            inner_angle_rad = np.arccos(dot_product / magnitude_product)
                            inner_angle_deg_2 = np.degrees(inner_angle_rad)
                            if inner_angle_deg_1>60 and inner_angle_deg_2>60:
                                regenerate=True
                                break
                            print(i,j,inner_angle_deg_1,inner_angle_deg_2,np.linalg.norm(edge1),self.robot_list[0].sensor_range,regenerate)
                    if regenerate==True:
                        break
                print(regenerate)
                if regenerate==False:
                    break
        print(len(pose_list))
        # pose_list = [[-3, -3, 0],
        #              # [-3, 3, 0],
        #              # [3, 3, 0],
        #              # [3, -3, 0],
        #              [0, 0, 0],
        #              [-5, 0, 0],
        #              # [0, 5, 0],
        #              [5, 0, 0],
        #              [0, -2, 0]]
        num_robot = len(self.robot_list)

        for i in range(num_robot):
            pos_height = 0.4
            position = [pose_list[i][0], pose_list[i][1], pos_height]
            orientation = [0, 0, pose_list[i][2]]

            robot_handle = self.robot_list[i].executor.robot_handle
            print(robot_handle)
            vrep_interface.post_robot_pose(
                self.client_id, robot_handle, position, orientation
            )
        return pose_list
    ### sumilation related
    def simulate(self,max_simulation_time,time_step=0.05,test_case="model"):
        simulation_time = 0
        data_recorder = Recorder()
        data_recorder.root_dir = "saved_data_test"

        while True:

            if simulation_time > max_simulation_time:
                break
            simulation_time += time_step
            print("robot control at time")
            print(simulation_time)

            for robot in self.robot_list:
                sensor_data = robot.get_sensor_data()
                control_data = robot.get_control_data()
                robot.execute_control()
                # record data
                data_recorder.record_sensor_data(sensor_data)
                data_recorder.record_robot_trace(sensor_data)
                data_recorder.record_controller_output(control_data)

            self.check_stop_condition()
            self.broadcast_all()
            vrep_interface.synchronize(self.client_id)
        data_recorder.save_to_file(test_case)
        # for robot in self.robot_list:
        #     map = robot.sensor_data.occupancy_map
        #     cv2.imwrite(str(robot.index)+".jpg",map)
        vrep_interface.stop(self.client_id)
        return 1
    def check_stop_condition(self):
        """
        :return:
        """
        if self.adjacency_list == None:

            return False
        else:
            for key, value in self.adjacency_list.items():
                for r in value:
                    print(
                        "distance between {r1:d} and {r2:d} is {r3:f}".format(
                            r1=key, r2=r[0], r3=r[3]
                        )
                    )
    def stop(self):
        vrep_interface.stop(self.client_id)
if __name__ == "__main__":
    get_vector_angle([0,1,1],[1,0,0])
