"""
A sensor template. Get information from simulator/real-world
author: Xinchi Huang
"""
import math
import numpy
import numpy as np

import time
import occupancy_map_simulator
import pyrealsense2 as rs
import cv2

# def get_frame():
#     """
#     OpenCV and Numpy Point cloud Software Renderer
#     This sample is mostly for demonstration and educational purposes.
#     It really doesn't offer the quality or performance that can be
#     achieved with hardware acceleration.
#     Usage:
#     ------
#     Mouse:
#         Drag with left button to rotate around pivot (thick small axes),
#         with right button to translate and the wheel to zoom.
#     Keyboard:
#         [p]     Pause
#         [r]     Reset View
#         [d]     Cycle through decimation values
#         [z]     Toggle point scaling
#         [c]     Toggle color source
#         [s]     Save PNG (./out.png)
#         [e]     Export points to ply (./out.ply)
#         [q\ESC] Quit
#     """
#
#     class AppState:
#
#         def __init__(self, *args, **kwargs):
#             self.WIN_NAME = 'RealSense'
#             self.pitch, self.yaw = math.radians(-10), math.radians(-15)
#             self.translation = np.array([0, 0, -1], dtype=np.float32)
#             self.distance = 2
#             self.prev_mouse = 0, 0
#             self.mouse_btns = [False, False, False]
#             self.paused = False
#             self.decimate = 1
#             self.scale = True
#             self.color = True
#
#         def reset(self):
#             self.pitch, self.yaw, self.distance = 0, 0, 2
#             self.translation[:] = 0, 0, -1
#
#         @property
#         def rotation(self):
#             Rx, _ = cv2.Rodrigues((self.pitch, 0, 0))
#             Ry, _ = cv2.Rodrigues((0, self.yaw, 0))
#             return np.dot(Ry, Rx).astype(np.float32)
#
#         @property
#         def pivot(self):
#             return self.translation + np.array((0, 0, self.distance), dtype=np.float32)
#
#     state = AppState()
#
#     # Configure depth and color streams
#     pipeline = rs.pipeline()
#     config = rs.config()
#
#     pipeline_wrapper = rs.pipeline_wrapper(pipeline)
#     pipeline_profile = config.resolve(pipeline_wrapper)
#     device = pipeline_profile.get_device()
#
#     found_rgb = False
#     for s in device.sensors:
#         if s.get_info(rs.camera_info.name) == 'RGB Camera':
#             found_rgb = True
#             break
#     if not found_rgb:
#         print("The demo requires Depth camera with Color sensor")
#         exit(0)
#
#     config.enable_stream(rs.stream.depth, rs.format.z16, 30)
#     config.enable_stream(rs.stream.color, rs.format.bgr8, 30)
#
#     # Start streaming
#     pipeline.start(config)
#
#     # Get stream profile and camera intrinsics
#     profile = pipeline.get_active_profile()
#     depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
#     depth_intrinsics = depth_profile.get_intrinsics()
#     w, h = depth_intrinsics.width, depth_intrinsics.height
#
#     # Processing blocks
#     pc = rs.pointcloud()
#     decimate = rs.decimation_filter()
#     decimate.set_option(rs.option.filter_magnitude, 2 ** state.decimate)
#     colorizer = rs.colorizer()
#
#     def mouse_cb(event, x, y, flags, param):
#
#         if event == cv2.EVENT_LBUTTONDOWN:
#             state.mouse_btns[0] = True
#
#         if event == cv2.EVENT_LBUTTONUP:
#             state.mouse_btns[0] = False
#
#         if event == cv2.EVENT_RBUTTONDOWN:
#             state.mouse_btns[1] = True
#
#         if event == cv2.EVENT_RBUTTONUP:
#             state.mouse_btns[1] = False
#
#         if event == cv2.EVENT_MBUTTONDOWN:
#             state.mouse_btns[2] = True
#
#         if event == cv2.EVENT_MBUTTONUP:
#             state.mouse_btns[2] = False
#
#         if event == cv2.EVENT_MOUSEMOVE:
#
#             h, w = out.shape[:2]
#             dx, dy = x - state.prev_mouse[0], y - state.prev_mouse[1]
#
#             if state.mouse_btns[0]:
#                 state.yaw += float(dx) / w * 2
#                 state.pitch -= float(dy) / h * 2
#
#             elif state.mouse_btns[1]:
#                 dp = np.array((dx / w, dy / h, 0), dtype=np.float32)
#                 state.translation -= np.dot(state.rotation, dp)
#
#             elif state.mouse_btns[2]:
#                 dz = math.sqrt(dx ** 2 + dy ** 2) * math.copysign(0.01, -dy)
#                 state.translation[2] += dz
#                 state.distance -= dz
#
#         if event == cv2.EVENT_MOUSEWHEEL:
#             dz = math.copysign(0.1, flags)
#             state.translation[2] += dz
#             state.distance -= dz
#
#         state.prev_mouse = (x, y)
#
#     cv2.namedWindow(state.WIN_NAME, cv2.WINDOW_AUTOSIZE)
#     cv2.resizeWindow(state.WIN_NAME, w, h)
#     cv2.setMouseCallback(state.WIN_NAME, mouse_cb)
#
#     def project(v):
#         """project 3d vector array to 2d"""
#         h, w = out.shape[:2]
#         view_aspect = float(h) / w
#
#         # ignore divide by zero for invalid depth
#         with np.errstate(divide='ignore', invalid='ignore'):
#             proj = v[:, :-1] / v[:, -1, np.newaxis] * \
#                    (w * view_aspect, h) + (w / 2.0, h / 2.0)
#
#         # near clipping
#         znear = 0.03
#         proj[v[:, 2] < znear] = np.nan
#         return proj
#
#     def view(v):
#         """apply view transformation on vector array"""
#         return np.dot(v - state.pivot, state.rotation) + state.pivot - state.translation
#
#     def line3d(out, pt1, pt2, color=(0x80, 0x80, 0x80), thickness=1):
#         """draw a 3d line from pt1 to pt2"""
#         p0 = project(pt1.reshape(-1, 3))[0]
#         p1 = project(pt2.reshape(-1, 3))[0]
#         if np.isnan(p0).any() or np.isnan(p1).any():
#             return
#         p0 = tuple(p0.astype(int))
#         p1 = tuple(p1.astype(int))
#         rect = (0, 0, out.shape[1], out.shape[0])
#         inside, p0, p1 = cv2.clipLine(rect, p0, p1)
#         if inside:
#             cv2.line(out, p0, p1, color, thickness, cv2.LINE_AA)
#
#     def grid(out, pos, rotation=np.eye(3), size=1, n=10, color=(0x80, 0x80, 0x80)):
#         """draw a grid on xz plane"""
#         pos = np.array(pos)
#         s = size / float(n)
#         s2 = 0.5 * size
#         for i in range(0, n + 1):
#             x = -s2 + i * s
#             line3d(out, view(pos + np.dot((x, 0, -s2), rotation)),
#                    view(pos + np.dot((x, 0, s2), rotation)), color)
#         for i in range(0, n + 1):
#             z = -s2 + i * s
#             line3d(out, view(pos + np.dot((-s2, 0, z), rotation)),
#                    view(pos + np.dot((s2, 0, z), rotation)), color)
#
#     def axes(out, pos, rotation=np.eye(3), size=0.075, thickness=2):
#         """draw 3d axes"""
#         line3d(out, pos, pos +
#                np.dot((0, 0, size), rotation), (0xff, 0, 0), thickness)
#         line3d(out, pos, pos +
#                np.dot((0, size, 0), rotation), (0, 0xff, 0), thickness)
#         line3d(out, pos, pos +
#                np.dot((size, 0, 0), rotation), (0, 0, 0xff), thickness)
#
#     def frustum(out, intrinsics, color=(0x40, 0x40, 0x40)):
#         """draw camera's frustum"""
#         orig = view([0, 0, 0])
#         w, h = intrinsics.width, intrinsics.height
#
#         for d in range(1, 6, 2):
#             def get_point(x, y):
#                 p = rs.rs2_deproject_pixel_to_point(intrinsics, [x, y], d)
#                 line3d(out, orig, view(p), color)
#                 return p
#
#             top_left = get_point(0, 0)
#             top_right = get_point(w, 0)
#             bottom_right = get_point(w, h)
#             bottom_left = get_point(0, h)
#
#             line3d(out, view(top_left), view(top_right), color)
#             line3d(out, view(top_right), view(bottom_right), color)
#             line3d(out, view(bottom_right), view(bottom_left), color)
#             line3d(out, view(bottom_left), view(top_left), color)
#
#     def pointcloud(out, verts, texcoords, color, painter=True):
#         """draw point cloud with optional painter's algorithm"""
#         if painter:
#             # Painter's algo, sort points from back to front
#
#             # get reverse sorted indices by z (in view-space)
#             # https://gist.github.com/stevenvo/e3dad127598842459b68
#             v = view(verts)
#             s = v[:, 2].argsort()[::-1]
#             proj = project(v[s])
#         else:
#             proj = project(view(verts))
#
#         if state.scale:
#             proj *= 0.5 ** state.decimate
#
#         h, w = out.shape[:2]
#
#         # proj now contains 2d image coordinates
#         j, i = proj.astype(np.uint32).T
#
#         # create a mask to ignore out-of-bound indices
#         im = (i >= 0) & (i < h)
#         jm = (j >= 0) & (j < w)
#         m = im & jm
#
#         cw, ch = color.shape[:2][::-1]
#         if painter:
#             # sort texcoord with same indices as above
#             # texcoords are [0..1] and relative to top-left pixel corner,
#             # multiply by size and add 0.5 to center
#             v, u = (texcoords[s] * (cw, ch) + 0.5).astype(np.uint32).T
#         else:
#             v, u = (texcoords * (cw, ch) + 0.5).astype(np.uint32).T
#         # clip texcoords to image
#         np.clip(u, 0, ch - 1, out=u)
#         np.clip(v, 0, cw - 1, out=v)
#
#         # perform uv-mapping
#         out[i[m], j[m]] = color[u[m], v[m]]
#
#     out = np.empty((h, w, 3), dtype=np.uint8)
#
#     while True:
#         # Grab camera data
#         if not state.paused:
#             # Wait for a coherent pair of frames: depth and color
#             frames = pipeline.wait_for_frames()
#
#             depth_frame = frames.get_depth_frame()
#             color_frame = frames.get_color_frame()
#
#             depth_frame = decimate.process(depth_frame)
#
#             # Grab new intrinsics (may be changed by decimation)
#             depth_intrinsics = rs.video_stream_profile(
#                 depth_frame.profile).get_intrinsics()
#             w, h = depth_intrinsics.width, depth_intrinsics.height
#             print(w,h)
#             depth_image = np.asanyarray(depth_frame.get_data())
#             color_image = np.asanyarray(color_frame.get_data())
#
#             depth_colormap = np.asanyarray(
#                 colorizer.colorize(depth_frame).get_data())
#
#             if state.color:
#                 mapped_frame, color_source = color_frame, color_image
#             else:
#                 mapped_frame, color_source = depth_frame, depth_colormap
#
#             points = pc.calculate(depth_frame)
#             pc.map_to(mapped_frame)
#
#             # Pointcloud data to arrays
#             v, t = points.get_vertices(), points.get_texture_coordinates()
#             verts = np.asanyarray(v).view(np.float32).reshape(-1, 3)  # xyz
#             for p in range(len(verts)):
#                 if verts[p][1]<-0.5 or verts[p][1]>0.5 or verts[p][0]<-1 or verts[p][0]>1 or verts[p][2]<-0 or verts[p][2]>2:
#
#                     verts[p][0] = 0
#                     verts[p][1] = 0
#                     verts[p][2] = 0
#
#
#             texcoords = np.asanyarray(t).view(np.float32).reshape(-1, 2)  # uv
#
#         # Render
#         now = time.time()
#
#         out.fill(0)
#
#         grid(out, (0, 0.5, 1), size=1, n=10)
#         frustum(out, depth_intrinsics)
#         axes(out, view([0, 0, 0]), state.rotation, size=0.1, thickness=1)
#
#         if not state.scale or out.shape[:2] == (h, w):
#             pointcloud(out, verts, texcoords, color_source)
#         else:
#             tmp = np.zeros((h, w, 3), dtype=np.uint8)
#             pointcloud(tmp, verts, texcoords, color_source)
#             tmp = cv2.resize(
#                 tmp, out.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)
#             np.putmask(out, tmp > 0, tmp)
#
#         if any(state.mouse_btns):
#             axes(out, view(state.pivot), state.rotation, thickness=4)
#
#         dt = time.time() - now
#
#         cv2.setWindowTitle(
#             state.WIN_NAME, "RealSense (%dx%d) %dFPS (%.2fms) %s" %
#                             (w, h, 1.0 / dt, dt * 1000, "PAUSED" if state.paused else ""))
#
#         cv2.imshow(state.WIN_NAME, out)
#         key = cv2.waitKey(1)
#
#         if key == ord("r"):
#             state.reset()
#
#         if key == ord("p"):
#             state.paused ^= True
#
#         if key == ord("d"):
#             state.decimate = (state.decimate + 1) % 3
#             decimate.set_option(rs.option.filter_magnitude, 2 ** state.decimate)
#
#         if key == ord("z"):
#             state.scale ^= True
#
#         if key == ord("c"):
#             state.color ^= True
#
#         if key == ord("s"):
#             cv2.imwrite('./out.png', out)
#
#         if key == ord("e"):
#             points.export_to_ply('./out.ply', mapped_frame)
#
#         if key in (27, ord("q")) or cv2.getWindowProperty(state.WIN_NAME, cv2.WND_PROP_AUTOSIZE) < 0:
#             break
#
#     # Stop streaming
#     pipeline.stop()
class SensorData:
    """
    A class for record sensor data
    """

    def __init__(self):
        self.robot_index = None
        self.position = None
        self.orientation = None
        self.linear_velocity = None
        self.angular_velocity = None
        self.occupancy_map = None


class Sensor:
    """
    Robot sensor
    """

    def __init__(self):
        self.client_id = None
        self.robot_handle = None
        self.robot_index = None

        #### sensor range related settings
        self.max_x = 10
        self.max_y = 10
        self.max_height = 0.3
        self.min_range = 0.2

        #### sensor output settings
        self.occupancy_map_size = 100
    def initial_realsense(self):

        self.pipeline = rs.pipeline()
        config = rs.config()

        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()

        found_rgb = False
        for s in device.sensors:
            if s.get_info(rs.camera_info.name) == 'RGB Camera':
                found_rgb = True
                break
        if not found_rgb:
            print("The demo requires Depth camera with Color sensor")
            exit(0)

        config.enable_stream(rs.stream.depth, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, rs.format.bgr8, 30)

        # Start streaming
        self.pipeline.start(config)

        # Get stream profile and camera intrinsics
        profile = self.pipeline.get_active_profile()
        depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
        depth_intrinsics = depth_profile.get_intrinsics()
        w, h = depth_intrinsics.width, depth_intrinsics.height

        pc = rs.pointcloud()
        decimate = rs.decimation_filter()
        decimate.set_option(rs.option.filter_magnitude, 2 ** 1)
        colorizer = rs.colorizer()


    def filter_data(self, world_point):
        x = world_point[0]
        y = world_point[1]
        z = world_point[2]
        if (
            x > self.max_x
            or x < -self.max_x
            or y > self.max_y
            or y < -self.max_y
            or z < -self.max_height
        ):  #
            return None
        elif (
            x < self.min_range
            and y < self.min_range
            and x > -self.min_range
            and y > -self.min_range
        ):
            return None
        return world_point

    def world_to_map(self, world_point):
        if world_point == None:
            return None
        x_world = world_point[0]
        y_world = world_point[1]
        x_map = int((self.max_x - x_world) / (2 * self.max_x) * self.occupancy_map_size)
        y_map = int((self.max_y - y_world) / (2 * self.max_y) * self.occupancy_map_size)

        return [x_map, y_map]

    def process_raw_data(self, point_cloud):
        sensor_points = point_cloud
        occupancy_map = (
            np.ones((self.occupancy_map_size, self.occupancy_map_size)) * 255
        )
        # print(occupancy_map)

        for i in range(0, len(sensor_points), 3):
            x_world = sensor_points[i + 0]
            y_world = sensor_points[i + 2]
            z_world = sensor_points[i + 1]
            # print("world point of robot", self.robot_index)
            # print([x_world,y_world,z_world])
            # if self.robot_index==2:
            #     print([x_world,y_world,z_world])
            point_world = self.filter_data([x_world, y_world, z_world])
            point_map = self.world_to_map(point_world)
            if point_map == None:
                continue
            # print("world point",self.robot_index)
            # print(x_world,y_world)
            # print("map point of robot", self.robot_index, self.robot_handle)
            # print(point_map)
            occupancy_map[point_map[0]][point_map[1]] = 0
        return occupancy_map
    def process_raw_data_realsense(self, point_cloud):
        sensor_points = point_cloud
        occupancy_map = (
            np.ones((self.occupancy_map_size, self.occupancy_map_size)) * 255
        )
        # print(occupancy_map)

        for i in range(0, len(sensor_points)):
            x_world = sensor_points[i][0]
            y_world = sensor_points[i][2]
            z_world = sensor_points[i][1]
            # print("world point of robot", self.robot_index)
            # print([x_world,y_world,z_world])
            # if self.robot_index==2:
            #     print([x_world,y_world,z_world])
            point_world = self.filter_data([x_world, y_world, z_world])
            point_map = self.world_to_map(point_world)
            if point_map == None:
                continue
            # print("world point",self.robot_index)
            # print(x_world,y_world)
            # print("map point of robot", self.robot_index, self.robot_handle)
            # print(point_map)
            occupancy_map[point_map[0]][point_map[1]] = 0
        return occupancy_map
    def get_sensor_data(self):
        """
        Get sensor readings
        :return: Data from sensor and simulator
        """
        robot_sensor_data = SensorData()

        linear_velocity = 0
        angular_velocity = 0
        position=None
        orientation=None


        # Wait for a coherent pair of frames: depth and color

        pc = rs.pointcloud()
        decimate = rs.decimation_filter()
        frames = self.pipeline.wait_for_frames()
        print(frames)
        depth_frame = frames.get_depth_frame()
        depth_frame = decimate.process(depth_frame)
        # Grab new intrinsics (maybe changed by decimation)
        depth_intrinsics = rs.video_stream_profile(
            depth_frame.profile).get_intrinsics()
        w, h = depth_intrinsics.width, depth_intrinsics.height
        points = pc.calculate(depth_frame)
        pc.map_to(depth_frame)

        # Pointcloud data to arrays
        v, t = points.get_vertices(), points.get_texture_coordinates()
        verts = np.asanyarray(v).view(np.float32).reshape(-1, 3)  # xyz

        occupancy_map=self.process_raw_data_realsense(verts)

        ### fake data

        global_positions = [[-4, -4, 0], [-4, 4, 0], [4, 4, 0], [4, -4, 0], [0, 0, 0]]
        # position_lists_local = occupancy_map_simulator.global_to_local(global_positions)
        # robot_size, max_height, map_size, max_x, max_y = 0.2, 0.3, 100, 10, 10
        # occupancy_map = occupancy_map_simulator.generate_map(
        #     position_lists_local, robot_size, max_height, map_size, max_x, max_y
        # )
        position=global_positions[self.robot_index]
        orientation=global_positions[self.robot_index]


        robot_sensor_data.robot_index = self.robot_index
        robot_sensor_data.position = position
        robot_sensor_data.orientation = orientation
        robot_sensor_data.linear_velocity = linear_velocity
        robot_sensor_data.angular_velocity = angular_velocity
        robot_sensor_data.occupancy_map = occupancy_map[self.robot_index]


        return robot_sensor_data
