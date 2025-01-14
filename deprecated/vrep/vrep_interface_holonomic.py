"""
A interface to operate Vrep APIs
author: Xinchi Huang
"""

from vrep import sim as vrep



def init_vrep():
    """
    Initial Vrep, setup connections
    :return: The client id(The scene id)
    """
    print("Program started")
    vrep.simxFinish(-1)  # just in case, close all opened connections
    client_id = vrep.simxStart(
        "127.0.0.1", 19997, True, True, 5000, 5
    )  # Connect to V-REP
    if client_id != -1:
        print("Connected to remote API server", client_id)
        vrep.simxSynchronous(client_id, True)
        vrep.simxStartSimulation(client_id, vrep.simx_opmode_blocking)
    return client_id


def get_vrep_handle(client_id, robot_index):
    """
    Get handles from simulator, which are labels to components of each robot in the scene
    :param client_id:The client id(The scene id)
    :param robot_index:The label to individual robot
    :return:
    robot_handle, motor_left_handle, motor_right_handle, point_cloud_handle
    Handles from simulator
    """
    handle_name_suffix = "#" + str(robot_index - 1)
    if robot_index == 0:
        handle_name_suffix = ""
    _, robot_handle = vrep.simxGetObjectHandle(
        client_id, "Omnirob" + handle_name_suffix, vrep.simx_opmode_oneshot_wait
    )
    _, omniRob_FL_handle = vrep.simxGetObjectHandle(client_id, 'Omnirob_FLwheel_motor'+ handle_name_suffix, vrep.simx_opmode_oneshot_wait)
    _, omniRob_FR_handle = vrep.simxGetObjectHandle(client_id, 'Omnirob_FRwheel_motor'+ handle_name_suffix, vrep.simx_opmode_oneshot_wait)
    _, omniRob_RL_handle = vrep.simxGetObjectHandle(client_id, 'Omnirob_RLwheel_motor'+ handle_name_suffix, vrep.simx_opmode_oneshot_wait)
    _, omniRob_RR_handle = vrep.simxGetObjectHandle(client_id, 'Omnirob_RRwheel_motor'+ handle_name_suffix, vrep.simx_opmode_oneshot_wait)

    # _, point_cloud_handle = vrep.simxGetObjectHandle(
    #     client_id, "velodyneVPL_16" + handle_name_suffix, vrep.simx_opmode_oneshot_wait
    # )

    return robot_handle, omniRob_FL_handle,omniRob_FR_handle,omniRob_RL_handle, omniRob_RR_handle


def get_robot_pose(client_id, robot_handle):
    """
    Get robot's pose from the simulator
    :param client_id: Scene id
    :param robot_handle: Robot label in the scene
    :return:
    pos: Robot position
    ori: Robot orientation

    """
    _, pos = vrep.simxGetObjectPosition(
        client_id, robot_handle, -1, vrep.simx_opmode_blocking
    )
    _, ori = vrep.simxGetObjectOrientation(
        client_id, robot_handle, -1, vrep.simx_opmode_blocking
    )
    return pos, ori


def get_sensor_data(client_id, robot_handle, robot_index):
    """
    Get the sensor data from the simulator
    :param client_id: Scene id
    :param robot_handle: Robot label in the scene
    :param robot_index: Robot index in the scene
    :return:
    vel: Robot linear velocity
    omega: Robot angle velocity
    velodyne_points: Point cloud from robot's Lidar sensor
    """
    handle_name_suffix = "#" + str(robot_index - 1)
    if robot_index == 0:
        handle_name_suffix = ""
    _, vel, omega = vrep.simxGetObjectVelocity(
        client_id, robot_handle, vrep.simx_opmode_blocking
    )
    velodyne_points = vrep.simxCallScriptFunction(
        client_id,
        "velodyneVPL_16" + handle_name_suffix,
        1,
        "getVelodyneData_function",
        [],
        [],
        [],
        "abc",
        vrep.simx_opmode_blocking,
    )
    return vel, omega, velodyne_points


def post_robot_pose(client_id, robot_handle, position, orientation):
    """
    Set robot's pose in the simulator
    :param client_id: Scene id
    :param robot_handle: Robot label in the scene
    :param position: Robot desired position in the scene
    :param orientation: Robot desired orientation in the scene
    """
    vrep.simxSetObjectPosition(
        client_id, robot_handle, -1, position, vrep.simx_opmode_oneshot
    )
    vrep.simxSetObjectOrientation(
        client_id, robot_handle, -1, orientation, vrep.simx_opmode_oneshot
    )


def post_control(
    client_id, omniRob_FL_handle,omniRob_FR_handle,omniRob_RL_handle, omniRob_RR_handle,vfl,vfr,vrl,vrr
):
    """

    :param client_id: Scene id
    :param motor_left_handle: Robot left wheel's label
    :param motor_right_handle: Robot right wheel's label
    :param omega1: Robot left wheel's angle velocity
    :param omega2: Robot right wheel's angle velocity
    """
    print(vfl,vfr,vrl,vrr)
    vrep.simxSetJointTargetVelocity(client_id, omniRob_FL_handle, vfl, vrep.simx_opmode_oneshot)
    vrep.simxSetJointTargetVelocity(client_id, omniRob_FR_handle, vfr, vrep.simx_opmode_oneshot)
    vrep.simxSetJointTargetVelocity(client_id, omniRob_RL_handle, vrl, vrep.simx_opmode_oneshot)
    vrep.simxSetJointTargetVelocity(client_id, omniRob_RR_handle, vrr, vrep.simx_opmode_oneshot)



def synchronize(clinet_id):
    """
    Let the simulator synchronize. In order to get data from the simulator
    :param clinet_id: Scene id
    """
    vrep.simxSynchronousTrigger(clinet_id)


def stop(client_id):
    """
    Stop
    :param client_id: Scene id
    :return:
    """
    vrep.simxStopSimulation(client_id, vrep.simx_opmode_blocking)
    vrep.simxFinish(client_id)

# if __name__ == "__main__":
#     client_id=init_vrep()
#     robot_handle, motor_left_handle, motor_right_handle, point_cloud_handle=get_vrep_handle(client_id,0)
#     print(motor_left_handle,motor_right_handle)
#     post_control(client_id, motor_left_handle, motor_right_handle,10,-10)



