'''
  @ Date: 2021-01-17 21:38:19
  @ Author: Qing Shuai
  @ LastEditors: Qing Shuai
  @ LastEditTime: 2021-08-24 16:42:22
  @ FilePath: /EasyMocap/easymocap/visualize/skelmodel.py
'''
import numpy as np
import cv2
from os.path import join
import os
from ..dataset.config import CONFIG

def calTransformation(v_i, v_j, r, adaptr=False, ratio=10):
    """ from to vertices to T
    
    Arguments:
        v_i {} -- [description]
        v_j {[type]} -- [description]
    """
    xaxis = np.array([1, 0, 0])
    v = (v_i + v_j)/2
    direc = (v_i - v_j)
    length = np.linalg.norm(direc)
    direc = direc/length
    rotdir = np.cross(xaxis, direc)
    if np.linalg.norm(rotdir) > 1e-3:
        rotdir = rotdir/np.linalg.norm(rotdir)
        rotdir = rotdir * np.arccos(np.dot(direc, xaxis))
        rotmat, _ = cv2.Rodrigues(rotdir)
    else:
        rotmat = np.eye(3)
    # set the minimal radius for the finger and face
    shrink = min(max(length/ratio, 0.005), 0.05)
    eigval = np.array([[length/2/r, 0, 0], [0, shrink, 0], [0, 0, shrink]])
    T = np.eye(4)
    T[:3,:3] = rotmat @ eigval @ rotmat.T
    T[:3, 3] = v
    return T, r, length

class SkelModel:
    def __init__(self, nJoints=None, kintree=None, body_type=None, joint_radius=0.02, res=20, **kwargs) -> None:
        if nJoints is not None:
            self.nJoints = nJoints
            self.kintree = kintree
        else:
            config = CONFIG[body_type]
            self.nJoints = config['nJoints']
            self.kintree = config['kintree']
        self.body_type = body_type
        self.device = 'none'
        cur_dir = os.path.dirname(__file__)
        faces = np.loadtxt(join(cur_dir, 'assets', 'sphere_faces_{}.txt'.format(res)), dtype=int)
        self.vertices = np.loadtxt(join(cur_dir, 'assets', 'sphere_vertices_{}.txt'.format(res)))
        # compose faces
        faces_all = []
        for nj in range(self.nJoints):
            faces_all.append(faces + nj*self.vertices.shape[0])
        for nk in range(len(self.kintree)):
            faces_all.append(faces + self.nJoints*self.vertices.shape[0] + nk*self.vertices.shape[0])
        self.faces = np.vstack(faces_all)
        self.color = None
        self.nVertices = self.vertices.shape[0] * self.nJoints + self.vertices.shape[0] * len(self.kintree)
        self.joint_radius = joint_radius

    def __call__(self, keypoints3d, id=0, return_verts=True, return_tensor=False, **kwargs):
        if len(keypoints3d.shape) == 2:
            keypoints3d = keypoints3d[None]
        if not return_verts:
            return keypoints3d
        if keypoints3d.shape[-1] == 3: # add confidence
            keypoints3d = np.dstack((keypoints3d, np.ones((keypoints3d.shape[0], keypoints3d.shape[1], 1))))
        r = self.joint_radius
        # joints 
        min_conf = 0.1
        verts_final = []
        for nper in range(keypoints3d.shape[0]):
            vertices_all = []
            kpts3d = keypoints3d[nper]
            # kpts3d = np.concatenate(([[0,0,0,0], [0,0,0,0]], kpts3d))
            # limb
            closet_joints = []
            for nk, (i, j) in enumerate(self.kintree):
                if kpts3d[i][-1] < min_conf or kpts3d[j][-1] < min_conf:
                    vertices_all.append(self.vertices*0.001)
                    continue
                T, _, length = calTransformation(kpts3d[i, :3], kpts3d[j, :3], r=1)
                if length > 2: # large than 2 meter
                    vertices_all.append(self.vertices*0.001)
                    continue
                if length < self.joint_radius * 5:
                    closet_joints.append(i)
                    closet_joints.append(j)
                vertices = self.vertices @ T[:3, :3].T + T[:3, 3:].T
                vertices_all.append(vertices)
            for nj in range(self.nJoints):
                if self.body_type in ['bodyhand', 'bodyhandface'] and nj > 25:
                    r_ = r / 2
                else:
                    r_ = r
                if kpts3d[nj, -1] < min_conf:
                    vertices_all.append(self.vertices*0.001)
                    continue
                vertices_all.append(self.vertices*r_ + kpts3d[nj:nj+1, :3])
            vertices = np.vstack(vertices_all)
            verts_final.append(vertices)
        verts_final = np.stack(verts_final)
        return verts_final
    
    def to(self, none):
        pass
    
    def merge_params(self, params, share_shape=False):
        keypoints = np.stack([param['keypoints3d'] for param in params])
        face_landmarks = np.stack([param['face3d'] for param in params])
        hand_left = np.stack([param['handl3d'] for param in params])
        hand_right = np.stack([param['handr3d'] for param in params])
        return {'keypoints3d': keypoints, 'id': [0], 'face3d': face_landmarks, 'handl3d': hand_left, 'handr3d': hand_right}

    def init_params(self, nFrames):
        return {'keypoints3d': np.zeros((self.nJoints, 4))}

class HandModel_left:
    def __init__(self, nJoints=None, kintree=None, body_type=None, joint_radius=0.02, res=20, **kwargs) -> None:
        if nJoints is not None:
            self.nJoints = nJoints
            self.kintree = kintree
        else:
            config = CONFIG[body_type]
            self.nJoints = config['nJoints']
            self.kintree = config['kintree']
        self.body_type = body_type
        self.device = 'none'
        cur_dir = os.path.dirname(__file__)
        faces = np.loadtxt(join(cur_dir, 'assets', 'sphere_faces_{}.txt'.format(res)), dtype=int)
        self.vertices = np.loadtxt(join(cur_dir, 'assets', 'sphere_vertices_{}.txt'.format(res)))
        # compose faces
        faces_all = []
        for nj in range(self.nJoints):
            faces_all.append(faces + nj*self.vertices.shape[0])
        for nk in range(len(self.kintree)):
            faces_all.append(faces + self.nJoints*self.vertices.shape[0] + nk*self.vertices.shape[0])
        self.faces = np.vstack(faces_all)
        self.color = None
        self.nVertices = self.vertices.shape[0] * self.nJoints + self.vertices.shape[0] * len(self.kintree)
        self.joint_radius = joint_radius

    def __call__(self, handl3d, id=0, return_verts=True, return_tensor=False, **kwargs):
        if len(handl3d.shape) == 2:
            handl3d = handl3d[None]
        if not return_verts:
            return handl3d
        if handl3d.shape[-1] == 3: # add confidence
            handl3d = np.dstack((handl3d, np.ones((handl3d.shape[0], handl3d.shape[1], 1))))
        r = self.joint_radius
        # joints 
        min_conf = 0.1
        verts_final = []
        for nper in range(handl3d.shape[0]):
            vertices_all = []
            kpts3d = handl3d[nper]
            # kpts3d = np.concatenate(([[0,0,0,0], [0,0,0,0]], kpts3d))
            # limb
            closet_joints = []
            for nk, (i, j) in enumerate(self.kintree):
                if kpts3d[i][-1] < min_conf or kpts3d[j][-1] < min_conf:
                    vertices_all.append(self.vertices*0.001)
                    continue
                T, _, length = calTransformation(kpts3d[i, :3], kpts3d[j, :3], r=1)
                if length > 2: # large than 2 meter
                    vertices_all.append(self.vertices*0.001)
                    continue
                if length < self.joint_radius * 5:
                    closet_joints.append(i)
                    closet_joints.append(j)
                vertices = self.vertices @ T[:3, :3].T + T[:3, 3:].T
                vertices_all.append(vertices)
            for nj in range(self.nJoints):
                if self.body_type in ['bodyhand', 'bodyhandface'] and nj > 25:
                    r_ = r / 2
                else:
                    r_ = r
                if kpts3d[nj, -1] < min_conf:
                    vertices_all.append(self.vertices*0.001)
                    continue
                vertices_all.append(self.vertices*r_ + kpts3d[nj:nj+1, :3])
            vertices = np.vstack(vertices_all)
            verts_final.append(vertices)
        verts_final = np.stack(verts_final)
        return verts_final

    def init_params(self, nFrames):
        return {'handl3d': np.zeros((self.nJoints, 4))}

class HandModel_right:
    def __init__(self, nJoints=None, kintree=None, body_type=None, joint_radius=0.02, res=20, **kwargs) -> None:
        if nJoints is not None:
            self.nJoints = nJoints
            self.kintree = kintree
        else:
            config = CONFIG[body_type]
            self.nJoints = config['nJoints']
            self.kintree = config['kintree']
        self.body_type = body_type
        self.device = 'none'
        cur_dir = os.path.dirname(__file__)
        faces = np.loadtxt(join(cur_dir, 'assets', 'sphere_faces_{}.txt'.format(res)), dtype=int)
        self.vertices = np.loadtxt(join(cur_dir, 'assets', 'sphere_vertices_{}.txt'.format(res)))
        # compose faces
        faces_all = []
        for nj in range(self.nJoints):
            faces_all.append(faces + nj*self.vertices.shape[0])
        for nk in range(len(self.kintree)):
            faces_all.append(faces + self.nJoints*self.vertices.shape[0] + nk*self.vertices.shape[0])
        self.faces = np.vstack(faces_all)
        self.color = None
        self.nVertices = self.vertices.shape[0] * self.nJoints + self.vertices.shape[0] * len(self.kintree)
        self.joint_radius = joint_radius

    def __call__(self, handr3d, id=0, return_verts=True, return_tensor=False, **kwargs):
        if len(handr3d.shape) == 2:
            handr3d = handr3d[None]
        if not return_verts:
            return handr3d
        if handr3d.shape[-1] == 3: # add confidence
            handr3d = np.dstack((handr3d, np.ones((handr3d.shape[0], handr3d.shape[1], 1))))
        r = self.joint_radius
        # joints 
        min_conf = 0.1
        verts_final = []
        for nper in range(handr3d.shape[0]):
            vertices_all = []
            kpts3d = handr3d[nper]
            # kpts3d = np.concatenate(([[0,0,0,0], [0,0,0,0]], kpts3d))
            # limb
            closet_joints = []
            for nk, (i, j) in enumerate(self.kintree):
                if kpts3d[i][-1] < min_conf or kpts3d[j][-1] < min_conf:
                    vertices_all.append(self.vertices*0.001)
                    continue
                T, _, length = calTransformation(kpts3d[i, :3], kpts3d[j, :3], r=1)
                if length > 2: # large than 2 meter
                    vertices_all.append(self.vertices*0.001)
                    continue
                if length < self.joint_radius * 5:
                    closet_joints.append(i)
                    closet_joints.append(j)
                vertices = self.vertices @ T[:3, :3].T + T[:3, 3:].T
                vertices_all.append(vertices)
            for nj in range(self.nJoints):
                if self.body_type in ['bodyhand', 'bodyhandface'] and nj > 25:
                    r_ = r / 2
                else:
                    r_ = r
                if kpts3d[nj, -1] < min_conf:
                    vertices_all.append(self.vertices*0.001)
                    continue
                vertices_all.append(self.vertices*r_ + kpts3d[nj:nj+1, :3])
            vertices = np.vstack(vertices_all)
            verts_final.append(vertices)
        verts_final = np.stack(verts_final)
        return verts_final

    def init_params(self, nFrames):
        return {'handr3d': np.zeros((self.nJoints, 4))}

class FaceModel:
    def __init__(self, nJoints=None, kintree=None, body_type=None, joint_radius=0.02, res=20, **kwargs) -> None:
        if nJoints is not None:
            self.nJoints = nJoints
            self.kintree = kintree
        else:
            config = CONFIG[body_type]
            self.nJoints = config['nJoints']
            self.kintree = config['kintree']
        self.body_type = body_type
        self.device = 'none'
        cur_dir = os.path.dirname(__file__)
        faces = np.loadtxt(join(cur_dir, 'assets', 'sphere_faces_{}.txt'.format(res)), dtype=int)
        self.vertices = np.loadtxt(join(cur_dir, 'assets', 'sphere_vertices_{}.txt'.format(res)))
        # compose faces
        faces_all = []
        for nj in range(self.nJoints):
            faces_all.append(faces + nj*self.vertices.shape[0])
        for nk in range(len(self.kintree)):
            faces_all.append(faces + self.nJoints*self.vertices.shape[0] + nk*self.vertices.shape[0])
        self.faces = np.vstack(faces_all)
        self.color = None
        self.nVertices = self.vertices.shape[0] * self.nJoints + self.vertices.shape[0] * len(self.kintree)
        self.joint_radius = joint_radius

    def __call__(self, face3d, id=0, return_verts=True, return_tensor=False, **kwargs):
        if len(face3d.shape) == 2:
            face3d = face3d[None]
        if not return_verts:
            return face3d
        if face3d.shape[-1] == 3: # add confidence
            face3d = np.dstack((face3d, np.ones((face3d.shape[0], face3d.shape[1], 1))))
        r = self.joint_radius
        # joints 
        min_conf = 0.1
        verts_final = []
        for nper in range(face3d.shape[0]):
            vertices_all = []
            kpts3d = face3d[nper]
            # kpts3d = np.concatenate(([[0,0,0,0], [0,0,0,0]], kpts3d))
            # limb
            closet_joints = []
            for nk, (i, j) in enumerate(self.kintree):
                if kpts3d[i][-1] < min_conf or kpts3d[j][-1] < min_conf:
                    vertices_all.append(self.vertices*0.001)
                    continue
                T, _, length = calTransformation(kpts3d[i, :3], kpts3d[j, :3], r=1)
                if length > 2: # large than 2 meter
                    vertices_all.append(self.vertices*0.001)
                    continue
                if length < self.joint_radius * 5:
                    closet_joints.append(i)
                    closet_joints.append(j)
                vertices = self.vertices @ T[:3, :3].T + T[:3, 3:].T
                vertices_all.append(vertices)
            for nj in range(self.nJoints):
                if self.body_type in ['bodyhand', 'bodyhandface'] and nj > 25:
                    r_ = r / 2
                else:
                    r_ = r
                if kpts3d[nj, -1] < min_conf:
                    vertices_all.append(self.vertices*0.001)
                    continue
                vertices_all.append(self.vertices*r_ + kpts3d[nj:nj+1, :3])
            vertices = np.vstack(vertices_all)
            verts_final.append(vertices)
        verts_final = np.stack(verts_final)
        return verts_final

    def init_params(self, nFrames):
        return {'face3d': np.zeros((self.nJoints, 4))}

class SMPLSKEL:
    def __init__(self, model_type, gender, body_type) -> None:
        from ..smplmodel import load_model
        config = CONFIG[body_type]
        self.smpl_model = load_model(gender, model_type=model_type, skel_type=body_type)
        self.body_model = SkelModel(config['nJoints'], config['kintree'])

    def __call__(self, return_verts=True, **kwargs):
        keypoints3d = self.smpl_model(return_verts=False, return_tensor=False, **kwargs)
        if not return_verts:
            return keypoints3d
        else:
            verts = self.body_model(return_verts=True, return_tensor=False, keypoints3d=keypoints3d[0])
            return verts
    
    def init_params(self, nFrames):
        return np.zeros((self.body_model.nJoints, 4))