"""
A robot template
author: Xinchi Huang
"""
# from vrep.robot_executor_vrep import Executor
# from vrep.robot_sensor_vrep import Sensor

# from .realrobot.robot_executor_robomaster import Executor
# from .realrobot.robot_sensor_realsense import Sensor
import os

# from .controller import Controller
import numpy as np
from multi_robot_formation.controller_new import *
from multi_robot_formation.comm_data import ControlData,SceneData,SensorData
from multi_robot_formation.utils.occupancy_map_simulator import MapSimulator
from multi_robot_formation.utils.preprocess import preprocess
import cv2


class Robot:
    """
    A robot template. Used for handling different components and store data for components.
    """

    def __init__(
        self, sensor, executor,controller, platform="vrep",sensor_range=5
    ):
        self.index = None
        self.GNN_model = None
        self.sensor_data = SensorData()
        self.control_data = ControlData()
        self.scene_data = SceneData()

        self.platform = platform
        self.sensor = sensor
        self.executor = executor
        self.controller=controller
        self.sensor_type="real"
        self.sensor_range=sensor_range



    def get_sensor_data(self):

        """
        Read sensor data from sensor in simulator/realworld
        :return: Sensor data
        """
        self.sensor_data = self.sensor.get_sensor_data()
        return self.sensor_data

    def get_control_data(self):
        """
        Get controls
        :return: Control data
        """
        # if self.index==0 or self.index==1:
        #     self.control_data.robot_index = self.index
        #     self.control_data.velocity_x = 0
        #     self.control_data.velocity_y = 0
        #     return self.control_data

        if self.platform=="vrep":
            if not self.scene_data == None and not self.sensor_data == None and not self.scene_data.adjacency_list == None:
                if self.controller.name == "CentralizedController":
                    self.control_data=self.controller.get_control(self.index,self.scene_data.adjacency_list[self.index],self.sensor_data.position)
                elif self.controller.name== "GnnMapBasicControllerSensor":
                    self.control_data=self.controller.get_control(self.index,self.scene_data)
                elif self.controller.name== "GnnMapBasicControllerSynthesise":
                    position_lists_global = self.scene_data.position_list
                    orientation_list = self.scene_data.orientation_list
                    occupancy_map_simulator = MapSimulator(max_x=self.sensor_range,max_y=self.sensor_range,local=True)
                    (
                        position_lists_local,
                        self_orientation,
                    ) = occupancy_map_simulator.global_to_local(
                        np.array(position_lists_global), np.array(orientation_list)
                    )
                    occupancy_map = occupancy_map_simulator.generate_map_one(position_lists_local[self.index])
                    self.sensor_data.occupancy_map = occupancy_map
                    self.control_data=self.controller.get_control(self.index,self.scene_data)
                elif self.controller.name == "GnnMapDecentralizedControllerSensor":
                    self.control_data = self.controller.get_control(self.index, self.scene_data)
                elif self.controller.name == "GnnMapDecentralizedControllerSynthesise":
                        position_lists_global = self.scene_data.position_list
                        orientation_list = self.scene_data.orientation_list
                        occupancy_map_simulator = MapSimulator(max_x=self.sensor_range,max_y=self.sensor_range,local=True)
                        (
                            position_lists_local,
                            self_orientation,
                        ) = occupancy_map_simulator.global_to_local(
                            np.array(position_lists_global), np.array(orientation_list)
                        )
                        occupancy_map = occupancy_map_simulator.generate_map_one(position_lists_local[self.index])
                        self.sensor_data.occupancy_map=occupancy_map
                        self.control_data=self.controller.get_control(self.index,self.sensor_data.occupancy_map)
                elif self.controller.name == "GnnPoseBasicController":
                    self.control_data=self.controller.get_control(self.index,self.scene_data)
                elif self.controller.name == "DummyController":
                    self.control_data = self.controller.get_control(self.index, self.scene_data)
                elif self.controller.name == "VitController":
                    position_lists_global = self.scene_data.position_list
                    orientation_list = self.scene_data.orientation_list
                    # if self.sensor_type=="realn":
                    #     occupancy_map=self.sensor_data.occupancy_map
                    #     # occupancy_map=preprocess(occupancy_map)
                    # else:
                    occupancy_map_simulator = MapSimulator(max_x=self.sensor_range,max_y=self.sensor_range,local=True)
                    (
                        position_lists_local,
                        self_orientation,
                    ) = occupancy_map_simulator.global_to_local(
                        np.array(position_lists_global), np.array(orientation_list)
                    )
                    occupancy_map = occupancy_map_simulator.generate_map_one(position_lists_local[self.index])
                        # occupancy_map = preprocess(occupancy_map)
                    # cv2.imshow("robot view " + str(self.index), np.array(occupancy_map))
                    # cv2.waitKey(1)
                    self.sensor_data.occupancy_map = occupancy_map
                    self.control_data=self.controller.get_control(self.index,self.sensor_data.occupancy_map)
                    # self.control_data.velocity_x=0
                    # self.control_data.velocity_y=0
                elif self.controller.name == "LocalExpertController":
                    position_lists_global = self.scene_data.position_list
                    orientation_list = self.scene_data.orientation_list
                    occupancy_map_simulator = MapSimulator(max_x=self.sensor_range,max_y=self.sensor_range,local=True)
                    (
                        position_lists_local,
                        self_orientation,
                    ) = occupancy_map_simulator.global_to_local(
                        np.array(position_lists_global), np.array(orientation_list)
                    )
                    occupancy_map = occupancy_map_simulator.generate_map_one(position_lists_local[self.index])
                    # cv2.imshow("robot view " + str(self.index) + "(Synthesise)", occupancy_map)
                    # cv2.waitKey(1)
                    self.sensor_data.occupancy_map = occupancy_map
                    self.control_data=self.controller.get_control(position_lists_local[self.index])
                    self.control_data.robot_index=self.index
                    print(self.index,self.control_data.velocity_x,self.control_data.velocity_y,self.control_data.omega)
                elif self.controller.name == "LocalExpertControllerPartial":
                    position_lists_global = self.scene_data.position_list
                    orientation_list = self.scene_data.orientation_list
                    # print(position_lists_global)
                    # print(orientation_list)
                    occupancy_map_simulator = MapSimulator(max_x=self.sensor_range,max_y=self.sensor_range,local=True)
                    (
                        position_lists_local,
                        self_orientation,
                    ) = occupancy_map_simulator.global_to_local(
                        np.array(position_lists_global), np.array(orientation_list)
                    )
                    # print(position_lists_local)
                    occupancy_map = occupancy_map_simulator.generate_map_one(position_lists_local[self.index])
                    cv2.imshow("robot view " + str(self.index) + "(Synthesise)", occupancy_map)
                    cv2.waitKey(1)
                    self.sensor_data.occupancy_map = occupancy_map
                    self.control_data=self.controller.get_control(position_lists_local[self.index])
                    self.control_data.robot_index=self.index
                    print(self.index, self.control_data.velocity_x, self.control_data.velocity_y,
                          self.control_data.omega)

            else:
                self.control_data.robot_index=self.index
                self.control_data.velocity_x=0
                self.control_data.velocity_y=0
        return self.control_data

    def execute_control(self):
        """
        Execute control from controller
        :return:
        """

        if self.platform == "vrep":
            if self.sensor_data==None:
                self.control_data.orientation=[0,0,0]
            else:

                self.control_data.orientation = self.sensor_data.orientation
        self.executor.execute_control(self.control_data)
