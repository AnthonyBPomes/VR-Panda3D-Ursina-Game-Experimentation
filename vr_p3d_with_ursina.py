#!/usr/bin/env python3

#from direct.showbase.ShowBase import ShowBase
from sys import builtin_module_names
from direct.showbase.PythonUtil import EnumIter
from ursina import *
from panda3d.core import ExecutionEnvironment

from p3dopenvr.p3dopenvr import P3DOpenVR
from p3dopenvr.skeleton import DefaultLeftHandSkeleton, DefaultRightHandSkeleton
from p3dopenvr.hand import LeftHand, RightHand

from physics3d import Debugger, BoxCollider, MeshCollider, character_controller
from panda3d.bullet import BulletWorld

import os
#from direct.task.TaskManagerGlobal import taskMgr

class SkeletonDemo:
    def __init__(self, ovr):
        self.ovr = ovr

        # Setup the application manifest, it will identify and configure the app
        # We force it in case it has changed.
        main_dir = ExecutionEnvironment.getEnvironmentVariable("MAIN_DIR")
        ovr.identify_application(os.path.join(main_dir, "skeleton.vrmanifest"), "p3dopenvr.demo.skeleton", force=True)

        # Load the actions manifest, it must be the same as the manifest referenced in the application manifest
        ovr.load_action_manifest(os.path.join(main_dir, "../manifest/actions.json"))

        # Use the '/actions/default' action set. This action set will be updated each frame
        ovr.add_action_set("/actions/default")

        # Get the handle of the action '/actions/default/in/Pose'. This hande will be used to update the position of the hands.
        hands_pose = ovr.vr_input.getActionHandle('/actions/default/in/Pose')

        # Get the handle of the skeleton actions. These handle will be used to update the
        # animation of the hands
        left_hand_skeleton_input = ovr.vr_input.getActionHandle('/actions/default/in/SkeletonLeftHand')
        right_hand_skeleton_input = ovr.vr_input.getActionHandle('/actions/default/in/SkeletonRightHand')

        # Create the representation of the left hand and attach a skinned hand model to it
        self.left_hand = LeftHand(ovr, "models/vr_glove_left_model.glb", hands_pose)
        self.left_hand.set_skeleton(DefaultLeftHandSkeleton(ovr, left_hand_skeleton_input))

        # Create the representation of the left hand and attach a skinned hand model to it
        self.right_hand = RightHand(ovr, "models/vr_glove_right_model.glb", hands_pose)
        self.right_hand.set_skeleton(DefaultRightHandSkeleton(ovr, right_hand_skeleton_input))

        # Register the update task with the correct sort number
        #taskMgr.add(self.update, sort=ovr.get_update_task_sort())

    #def update(self, task):
        # Update the position and orientation of the hands and their skeletons
        #self.left_hand.update()
        #self.right_hand.update()
        #return task.cont

# Set up the window, camera, etc.
app = Ursina()
world = BulletWorld()
Debugger(world, wireframe=True)
world.setGravity(Vec3(0, -9.81, 0))
#base.setFrameRateMeter(True)

# Create and configure the VR environment

ovr = P3DOpenVR()
ovr.init()

ground = Entity(model='cube',texture='grass', scale=(100,1,100), position=(0,-0.5,0))
BoxCollider(world, ground)
cube = Entity(model='cube', color=(255,0,0,1), position=(0,10,0), scale=(0.5,0.5,0.5))
cube_bounds = BoxCollider(world, cube, mass=1, scale=(0.25,0.25,0.25))
box = Entity(model='cube',scale=(0.1,0.1,0.2), color=(0,0,0,0))
point1 = Entity(model='sphere', scale=(0.05,0.05,0.05), color=(0,0,0,0))
point2 = Entity(model='sphere', scale=(0.05,0.05,0.05))
#min_bounds, max_bounds = model.get_tight_bounds()
#height = max_bounds.get_z() - min_bounds.get_z()
#model.set_scale(1.5 / height)
#model.set_pos(0, 1, -min_bounds.get_z() / height * 1.5)
demo = SkeletonDemo(ovr)
#box.reparent_to(demo.left_hand.hand_np)

box_bounds = BoxCollider(world, box, scale=(0.05,0.05,0.1))

def update():
    cube_bounds.setDeactivationEnabled(False)

    print(cube.bounds)

    point1.position = demo.left_hand.hand_np.getTightBounds()[0]
    point2.position = demo.left_hand.hand_np.getTightBounds()[1]

    box_bounds.scale_x = (point1.x - point2.x) * 6
    box_bounds.scale_y = (point1.y - point2.y) * 6
    box_bounds.scale_z = (point1.z - point2.z) * 6

    print(box_bounds.scale)

    box_bounds.x = (point1.x + point2.x) / 2
    box_bounds.y = (point1.y + point2.y) / 2
    box_bounds.z = (point1.z + point2.z) / 2

    #box_bounds.rotation_x = demo.left_hand.hand_np.getHpr()[0]
    #box_bounds.rotation_y = demo.left_hand.hand_np.getHpr()[1]
    #box_bounds.rotation_z = demo.left_hand.hand_np.getHpr()[2]
    
    dt = time.dt
    world.doPhysics(dt)
    demo.left_hand.update()
    demo.right_hand.update()
    

#base.accept('escape', base.userExit)
#base.accept('d', ovr.list_devices)
#base.accept('b', base.bufferViewer.toggleEnable)

app.run()
