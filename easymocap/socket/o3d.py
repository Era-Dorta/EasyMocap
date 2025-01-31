'''
  @ Date: 2021-05-25 11:15:53
  @ Author: Qing Shuai
  @ LastEditors: Qing Shuai
  @ LastEditTime: 2021-06-28 19:36:58
  @ FilePath: /EasyMocapRelease/easymocap/socket/o3d.py
'''
import open3d as o3d
from ..config import load_object
from ..visualize.o3dwrapper import Vector3dVector, create_mesh, load_mesh
from ..mytools import Timer
from ..mytools.vis_base import get_rgb_01
from .base import BaseSocket, log
import json
import numpy as np
from os.path import join
import os
from ..assignment.criterion import CritRange
import copy

rotate = False
def o3d_callback_rotate(vis=None):
    global rotate
    rotate = not rotate
    return False

class VisOpen3DSocket(BaseSocket):
    def __init__(self, host, port, cfg) -> None:
        # output
        self.write = cfg.write
        self.out = cfg.out
        self.cfg = cfg
        if self.write:
            print('[Info] capture the screen to {}'.format(self.out))
            os.makedirs(self.out, exist_ok=True)
        # scene
        vis = o3d.visualization.VisualizerWithKeyCallback()
        vis.register_key_callback(ord('A'), o3d_callback_rotate)
        if cfg.rotate:
            o3d_callback_rotate()
        vis.create_window(window_name='Visualizer', width=cfg.width, height=cfg.height)
        self.vis = vis
        # load the scene
        for key, mesh_args in cfg.scene.items():
            mesh = load_object(key, mesh_args)
            self.vis.add_geometry(mesh)
        for key, val in cfg.extra.items():
            mesh = load_mesh(val["path"])
            trans = np.array(val['transform']).reshape(4, 4)
            mesh.transform(trans)
            self.vis.add_geometry(mesh)
        # create vis => update => super() init
        super().__init__(host, port, debug=cfg.debug)
        self.block = cfg.block
        if os.path.exists(cfg.body_model_template):
            body_template = o3d.io.read_triangle_mesh(cfg.body_model_template)
            self.body_template = body_template
        else:
            self.body_template = None
        self.body_model = load_object(cfg.body_model.module, cfg.body_model.args)
        self.face_model = load_object(cfg.face_model.module, cfg.face_model.args)
        self.left_hand_model = load_object(cfg.left_hand_model.module, cfg.left_hand_model.args)
        self.right_hand_model = load_object(cfg.right_hand_model.module, cfg.right_hand_model.args)
        zero_params_body = self.body_model.init_params(1)
        zero_params_face = self.face_model.init_params(1)
        zero_params_left_hand = self.left_hand_model.init_params(1)
        zero_params_right_hand = self.right_hand_model.init_params(1)
        self.max_human = cfg.max_human
        self.track = cfg.track
        self.filter = cfg.filter
        self.camera_pose = cfg.camera.camera_pose
        self.init_camera(cfg.camera.camera_pose)
        self.zero_vertices_body = Vector3dVector(np.zeros((self.body_model.nVertices, 3)))
        self.zero_vertices_face = Vector3dVector(np.zeros((self.face_model.nVertices, 3)))
        self.zero_vertices_left_hand = Vector3dVector(np.zeros((self.left_hand_model.nVertices, 3)))
        self.zero_vertices_right_hand = Vector3dVector(np.zeros((self.right_hand_model.nVertices, 3)))

        self.vertices, self.meshes = [], []
        for i in range(self.max_human):
            self.add_human(zero_params_body, zero_params_face, zero_params_left_hand, zero_params_right_hand)

        self.count = 0
        self.previous = {}
        self.critrange = CritRange(**cfg.range)
        self.new_frames  = cfg.new_frames
    
    def add_human(self, zero_params_body, zero_params_face, zero_params_left_hand, zero_params_right_hand):
        vertices = self.body_model(return_verts=True, return_tensor=False, **zero_params_body)[0]
        vertices_face = self.face_model(return_verts=True, return_tensor=False, **zero_params_face)[0]
        vertices_left_hand = self.left_hand_model(return_verts=True, return_tensor=False, **zero_params_left_hand)[0]
        vertices_right_hand = self.right_hand_model(return_verts=True, return_tensor=False, **zero_params_right_hand)[0]
        vertices_whole_body = {'body': vertices, 'face': vertices_face, 'left_hand': vertices_left_hand, 'right_hand': vertices_right_hand}
        self.vertices.append(vertices_whole_body)
        if self.body_template is None: # create template
            mesh = create_mesh(vertices=vertices, faces=self.body_model.faces, colors=self.body_model.color)
            mesh_face = create_mesh(vertices=vertices_face, faces=self.face_model.faces, colors=self.face_model.color)
            mesh_left_hand = create_mesh(vertices=vertices_left_hand, faces=self.left_hand_model.faces, colors=self.left_hand_model.color)
            mesh_right_hand = create_mesh(vertices=vertices_right_hand, faces=self.right_hand_model.faces, colors=self.right_hand_model.color)
        else:
            mesh = copy.deepcopy(self.body_template)
        mesh_whole_body = {'body': mesh, 'face': mesh_face, 'left_hand': mesh_left_hand, 'right_hand': mesh_right_hand}
        self.meshes.append(mesh_whole_body)
        self.vis.add_geometry(mesh)
        self.vis.add_geometry(mesh_face)
        self.vis.add_geometry(mesh_left_hand)
        self.vis.add_geometry(mesh_right_hand)
        self.init_camera(self.camera_pose)

    @staticmethod
    def set_camera(cfg, camera_pose):
        theta, phi = np.deg2rad(-(cfg.camera.theta + 90)), np.deg2rad(cfg.camera.phi)
        theta = theta + np.pi
        st, ct = np.sin(theta), np.cos(theta)
        sp, cp = np.sin(phi), np.cos(phi)
        rot_x = np.array([
            [1., 0., 0.],
            [0., ct, -st],
            [0, st, ct]
        ])
        rot_z = np.array([
            [cp, -sp, 0],
            [sp, cp, 0.],
            [0., 0., 1.]
        ])
        camera_pose[:3, :3] = rot_x @ rot_z
        return camera_pose

    def init_camera(self, camera_pose):
        ctr = self.vis.get_view_control()
        init_param = ctr.convert_to_pinhole_camera_parameters()
        # init_param.intrinsic.set_intrinsics(init_param.intrinsic.width, init_param.intrinsic.height, fx, fy, cx, cy)
        init_param.extrinsic = np.array(camera_pose)
        ctr.convert_from_pinhole_camera_parameters(init_param) 

    def get_camera(self):
        ctr = self.vis.get_view_control()
        init_param = ctr.convert_to_pinhole_camera_parameters()
        return np.array(init_param.extrinsic)

    def filter_human(self, datas):
        datas_new = []
        for data in datas:
            kpts3d = np.array(data['keypoints3d'])
            data['keypoints3d'] = kpts3d
            flm3d = np.array(data['face3d'])
            data['face3d'] = flm3d
            hdls = np.array(data['handl3d'])
            data['handl3d'] = hdls
            hdrs = np.array(data['handr3d'])
            data['handr3d'] = hdrs
            pid = data['id']
            if pid not in self.previous.keys():
                if not self.critrange(kpts3d):
                    continue
                self.previous[pid] = 0
            self.previous[pid] += 1
            if self.previous[pid] > self.new_frames:
                datas_new.append(data)
        return datas_new

    def main(self, datas):
        if self.debug:log('[Info] Load data {}'.format(self.count))
        if isinstance(datas, str):
            datas = json.loads(datas)
        for data in datas:
            for key in data.keys():
                if key == 'id':
                    continue
                data[key] = np.array(data[key])
            if 'keypoints3d' not in data.keys() and self.filter:
                data['keypoints3d'] = self.body_model(return_verts=False, return_tensor=False, **data)[0]
        if self.filter:
            datas = self.filter_human(datas)
        with Timer('forward'):
            params = []
            for i, data in enumerate(datas):
                if i >= len(self.meshes):
                    print('[Error] the number of human exceeds!')
                    self.add_human(data)
                if 'vertices' in data.keys():
                    vertices = data['vertices']
                    self.vertices[i] = Vector3dVector(vertices)
                else:
                    params.append(data)
            if len(params) > 0:
                params = self.body_model.merge_params(params, share_shape=False)
                vertices = self.body_model(return_verts=True, return_tensor=False, **params)
                face_vertices = self.face_model(return_verts=True, return_tensor=False, **params)
                left_hand_vertices = self.left_hand_model(return_verts=True, return_tensor=False, **params)
                right_hand_vertices = self.right_hand_model(return_verts=True, return_tensor=False, **params)
                for i in range(vertices.shape[0]):
                    self.vertices[i]['body'] = Vector3dVector(vertices[i])
                    self.vertices[i]['face'] = Vector3dVector(face_vertices[i])
                    self.vertices[i]['left_hand'] = Vector3dVector(left_hand_vertices[i])
                    self.vertices[i]['right_hand'] = Vector3dVector(right_hand_vertices[i])
            for i in range(len(datas), len(self.meshes)):
                self.vertices[i]['body'] = self.zero_vertices_body
                self.vertices[i]['face'] = self.zero_vertices_face
                self.vertices[i]['left_hand'] = self.zero_vertices_left_hand
                self.vertices[i]['right_hand'] = self.zero_vertices_right_hand
        # Open3D will lock the thread here
        with Timer('set vertices'):
            for i in range(len(self.vertices)):
                self.meshes[i]['body'].vertices = self.vertices[i]['body']
                self.meshes[i]['face'].vertices = self.vertices[i]['face']
                self.meshes[i]['left_hand'].vertices = self.vertices[i]['left_hand']
                self.meshes[i]['right_hand'].vertices = self.vertices[i]['right_hand']
                if i < len(datas) and self.track:
                    # col = get_rgb_01(datas[i]['id'])
                    # self.meshes[i]['body'].paint_uniform_color(col)
                    # self.meshes[i]['face'].paint_uniform_color(col)
                    # self.meshes[i]['left_hand'].paint_uniform_color(col)
                    # self.meshes[i]['right_hand'].paint_uniform_color(col)
                    col = get_rgb_01(datas[0]['id'])
                    self.meshes[i]['body'].paint_uniform_color(col)
                    self.meshes[i]['face'].paint_uniform_color(col)
                    self.meshes[i]['left_hand'].paint_uniform_color(col)
                    self.meshes[i]['right_hand'].paint_uniform_color(col)

    def o3dcallback(self):
        if rotate:
            self.cfg.camera.phi += np.pi/10
            camera_pose = self.set_camera(self.cfg, self.get_camera())
            self.init_camera(camera_pose)

    def update(self):
        if self.disconnect and not self.block:
            self.previous.clear()
        if not self.queue.empty():
            if self.debug:log('Update' + str(self.queue.qsize()))
            datas = self.queue.get()
            if not self.block:
                while self.queue.qsize() > 0:
                    datas = self.queue.get()
            self.main(datas)
            with Timer('update geometry'):
                for mesh in self.meshes:
                    mesh['body'].compute_triangle_normals()
                    self.vis.update_geometry(mesh['body'])
                    mesh['face'].compute_triangle_normals()
                    self.vis.update_geometry(mesh['face'])
                    mesh['left_hand'].compute_triangle_normals()
                    self.vis.update_geometry(mesh['left_hand'])
                    mesh['right_hand'].compute_triangle_normals()
                    self.vis.update_geometry(mesh['right_hand'])
                self.o3dcallback()
                self.vis.poll_events()
                self.vis.update_renderer()
            if self.write:
                outname = join(self.out, '{:06d}.jpg'.format(self.count))
                with Timer('capture'):
                    self.vis.capture_screen_image(outname)
            self.count += 1
        else:
            with Timer('update renderer', True):
                self.o3dcallback()
                self.vis.poll_events()
                self.vis.update_renderer()