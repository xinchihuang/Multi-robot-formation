"""
A controller template
"""
import math

class ControlData:
    """
    A data structure for passing control signals to executor
    """

    def __init__(self):
        self.omega_left = 0
        self.omega_right = 0


class Controller:
    def __init__(self):
        self.desired_distance=2
        self.centralized_k=1
        self.max_velocity = 1.2
        self.wheel_adjustment=10.25

    def centralized_control(self,index, sensor_data,network_data):

        out_put = ControlData()
        if network_data==None:
            out_put.omega_left=0
            out_put.omega_right=0
            return out_put
        self_position=sensor_data.position
        self_orientation=sensor_data.orientation
        self_x = self_position[0]
        self_y = self_position[1]
        neighbors=network_data[index]

        velocity_sum_x=0
        velocity_sum_y=0
        print("neighbor")
        print(index,self_x,self_y,neighbors)
        for neighbor in neighbors:
            rate=(neighbor[3]-self.desired_distance)/neighbor[3]
            velocity_x=rate*(self_x-neighbor[1])
            velocity_y=rate*(self_y-neighbor[2])
            velocity_sum_x-=velocity_x
            velocity_sum_y-=velocity_y
        print(velocity_sum_x,velocity_sum_y,self_position[2])
        # print("speed")
        # print(velocity_sum_x,velocity_sum_y)
        # transform speed to wheels speed
        kk = self.centralized_k
        theta = self_orientation[2]
        M11 = kk * math.sin(theta) + math.cos(theta)
        M12 = -kk * math.cos(theta) + math.sin(theta)
        M21 = -kk * math.sin(theta) + math.cos(theta)
        M22 = kk * math.cos(theta) + math.sin(theta)

        wheel_velocity_left = M11 * velocity_sum_x + M12 * velocity_sum_y
        wheel_velocity_right = M21 * velocity_sum_x + M22 * velocity_sum_y

        # print(wheel_velocity_left,wheel_velocity_right)


        if math.fabs(wheel_velocity_right) >= math.fabs(wheel_velocity_left) and math.fabs(wheel_velocity_right) > self.max_velocity:
            alpha = self.max_velocity / math.fabs(wheel_velocity_right)
        elif math.fabs(wheel_velocity_right) < math.fabs(wheel_velocity_left) and math.fabs(wheel_velocity_left) > self.max_velocity:
            alpha = self.max_velocity / math.fabs(wheel_velocity_left)
        else:
            alpha = 1

        wheel_velocity_left=alpha*wheel_velocity_left
        wheel_velocity_right=alpha*wheel_velocity_right


        out_put.omega_left=wheel_velocity_left*self.wheel_adjustment
        out_put.omega_right=wheel_velocity_right*self.wheel_adjustment
        return out_put

    def decentralized_control(self, sensor_data):
        pass
