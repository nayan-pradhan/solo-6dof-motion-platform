from pickle import GLOBAL
import pybullet as p
import csv
import numpy as np
import math
from scipy.spatial.transform import Rotation as R
from matplotlib import pyplot as plt
from config import *

class PybulletIKClass():

    def __init__(self, 
        robot_environment = ''
    ):
        self.robot_environment = robot_environment
        self.data = []
        self.robot_id = None
        self.dummy_joints = []

        self.read_from_csv(True)
        self.data = np.array(self.data)

        self.positions = self.data[:, :3]
        self.orientations = self.data[:, 3:]

        self.joint_targets = []

        # Connecting to physics client
        p.connect(p.DIRECT)

        self.load_URDF_model()
        self.calculate_inverse_kinematic()
        
        p.disconnect()


    def load_URDF_model(self):
        """
            Setup PyBullet control environment by loading robot URDFs, adjusting collision, and adding contraints.

            :return: None.
            :rtype: None.
        """
        # loading robot URFD file
        URDF_home_position = [0,0,0]
        URDF_home_orientation = p.getQuaternionFromEuler([0,0,0])
        self.robot_id = p.loadURDF("../resources/URDF/URDF_motion_simulator_simplified_dummy/urdf/URDF_motion_simulator_simplified_dummy.urdf",
                                    URDF_home_position, 
                                    URDF_home_orientation, 
                                    useFixedBase = 1)

        # set indices for dummy joints
        self.dummy_joints = [3, 7, 11, 15]

        # load platform URDF model
        URDF_home_position = self.positions[0]
        URDF_home_orientation = p.getQuaternionFromEuler(self.orientations[0])
        self.platform_id = p.loadURDF("../resources/URDF/URDF_sensor_platform_simplified/urdf/URDF_sensor_platform_simplified.urdf",
                            URDF_home_position, 
                            URDF_home_orientation, 
                            useFixedBase = 0)

        # disable collision for dummy joints
        for i in self.dummy_joints:
            p.setCollisionFilterPair(self.robot_id, self.platform_id, i, -1, False) # disable collision

        # Set contraints between legs and platform
        joint_pos_leg = np.array([-1.1, 0, -93.07])/1000 # relative Position of new Joint to COM of link
        joint_pos_platform = np.array([181.65, 118.89, 6.73])/1000   # relative Position of ball joint to origin
        offset_com_platform = np.array([-6.23, 1.26, -4.63])/1000 # offset center of mass to origin of the platform
        joint_indices = [2, 6, 10, 14] # Indices of the lower legs (FL, FR, HL, HR)
        
        
        for i in joint_indices:
            p.setCollisionFilterPair(self.robot_id, self.platform_id, i, -1, False) # disable collision
            newjoint_pos_leg = joint_pos_leg # Position of new joint

            if i == joint_indices[0]: # front left
                newjoint_pos_platform = joint_pos_platform + offset_com_platform
            elif i == joint_indices[1]: # front right
                newjoint_pos_platform = joint_pos_platform * np.array([1, -1, 1]) + offset_com_platform
            elif i == joint_indices[2]: # back left
                newjoint_pos_platform = joint_pos_platform * np.array([-1, 1, 1]) + offset_com_platform
            elif i == joint_indices[3]: # back right
                newjoint_pos_platform = joint_pos_platform * np.array([-1, -1, 1]) + offset_com_platform

            cid = p.createConstraint(
            self.robot_id,                # Parent body unique ID
            i,                      # Parent link index
            self.platform_id,             # Child body unique ID
            -1,                     # Child link index (-1 for base)
            p.JOINT_POINT2POINT,    # Joint type
            [0,0,0],                # Joint axis in child link frame
            newjoint_pos_leg,         # Position of the joint frame relative to parent center of mass frame.
            newjoint_pos_platform,    # Position of the joint frame relative to a given child center of mass frame 
            )

            p.changeConstraint(cid, maxForce = 20.)     # Set maxForce of constraint


    def controller(self):
        """
            Controller required calculate PyBullet Inverse Kinematics.

            :return: None.
            :rtype: None.
        """
        velocity_target = 0
        torque = []
        kp = 20
        kd = 0.2
        torque_saturation = 2

        for i in range(len(self.joint_targets)):
            # get joints positions
            joint_state = p.getJointState(self.robot_id, i)
            joint_pos = joint_state[0]
            joint_vel = joint_state[1]

            # calculate error
            pos_err = self.joint_targets[i] - joint_pos
            vel_err = velocity_target - joint_vel

            # calculate torque
            torque.append(pos_err * kp + vel_err * kd)
            # saturation
            if torque[-1] > torque_saturation:
                torque[-1] = torque_saturation
            elif torque[-1] < -torque_saturation:
                torque[-1] = -torque_saturation
        
        p.setJointMotorControlArray(bodyUniqueId=self.robot_id, 
                                    jointIndices=list(range(len(self.joint_targets))), 
                                    controlMode=p.TORQUE_CONTROL, 
                                    forces=torque)


    def calculate_inverse_kinematic(self):
        """
            Calculates target joint angles from PyBullet Inverse Kinematics and stores in csv file. 

            :return: None.
            :rtype: None.
        """
        joint_positions = []
        progress = 0.
        p.setGravity(0,0,-9.81)
        print('Calculating inverse kinematics', math.floor(progress), '%', end='\r')
        last_joint_pos = [-0.03720331288427462,0.829007129122855,-1.6202734972969408,0.0,0.034261802256937444,-0.8275962751091314,1.617652654183728,0.0,0.03734524762342967,-0.8291123597545643,1.6206753705804764,0.0,-0.03441818042258571,0.8276649022998361,-1.6178770197057506,0.0]

        p.setJointMotorControlArray(self.robot_id,
                                    list(range(p.getNumJoints(self.robot_id))),
                                    p.VELOCITY_CONTROL,
                                    forces = np.zeros(16))
        first = True

        for pos, orn in zip(self.positions, self.orientations):
            target_position = self.transform_platform_to_robot(pos, orn)
            if first: # Setting initial pose with knees bend inwards
                first = False
                joint_positions.append(p.calculateInverseKinematics2(self.robot_id, 
                                                                self.dummy_joints, 
                                                                target_position, 
                                                                maxNumIterations = 10000, 
                                                                currentPositions = last_joint_pos))
            else:
                joint_positions.append(p.calculateInverseKinematics2(self.robot_id, 
                                                                self.dummy_joints, 
                                                                target_position, 
                                                                maxNumIterations = 10000))

            self.joint_targets = joint_positions[-1]
            self.controller()
            p.stepSimulation()
            
            progress += float(1 / len(self.positions)) * 100
            print('Calculating inverse kinematics', math.floor(progress), '%', end='\r')
        print('Calculating inverse kinematics', 100, '%')

        print('Saving data to csv...', end='\r')
        f = open(GLOBAL_AUTOGENERATED_DIRECTORY + TRAJ_JOINTS_FILE_NAME, 'w')
        if self.robot_environment == "pybullet":
            fn = "pybu" 
        else:
            fn = "solo"
        fc = open(GLOBAL_AUTOGENERATED_DIRECTORY + HISTORY_DIR + fn + '_' + TRAJ_JOINTS_FILE_UNIQUE, 'w')
        writer = csv.writer(f)
        writerc = csv.writer(fc)
        writer.writerow([self.robot_environment])
        writerc.writerow([self.robot_environment])

        header_line = [
            "fl_hip", "fl_upper", "fl_lower", "fl_dummy", 
            "fr_hip", "fr_upper", "fr_lower", "fr_dummy",
            "bl_hip", "bl_upper", "bl_lower", "bl_dummy",
            "br_hip", "br_upper", "br_lower", "br_dummy"
            ]

        writer.writerow(header_line)
        writerc.writerow(header_line)

        writer.writerows(joint_positions[1:])
        writerc.writerows(joint_positions[1:])
        fc.close()
        f.close()
        print('Saving data to csv...done')

        """
        # Debugging option
        joint_positions = np.array(joint_positions)
        plt.plot(joint_positions[:, [0, 4, 8, 12]], label=['target hip fl', 'target hip fr', 'target hip bl', 'target hip br'])
        plt.legend()
        plt.show()

        plt.plot(joint_positions[:, [1, 5, 9, 13]], label=['target upper fl', 'target upper fr', 'target upper bl', 'target upper br'])
        plt.legend()
        plt.show()

        plt.plot(joint_positions[:, [2, 6, 10, 14]], label=['target lower fl', 'target lower fr', 'target lower bl', 'target lower br'])
        plt.legend()
        plt.show()
        """

    def transform_platform_to_robot(self, platform_pos, platform_orn):
        """
            Transforms target platform pose to target robot end-effector ball joint position.

            :param platform_pos: List of target platform position values.
            :type platform_pos: list[list[float]].
            :param platform_orn: List of target platform orientation values.
            :type platform_orn: list[list[float]].
            :return: Retuns list of transformed target robot end-effector ball joint position.
            :rtype: list[float].
        """
        target_pos = []
        ball_joint_pos = []
        joint_pos_platform = np.array([181.65, 118.89, 6.73])/1000   # relative Position of ball joint to origin

        # calculate ball joint positions on platform
        rot_matrix = self.get_rotation_matrix(platform_orn)
        ball_joint_pos.append(rot_matrix.dot(joint_pos_platform))
        ball_joint_pos.append(rot_matrix.dot(joint_pos_platform * np.array([1, -1, 1])))
        ball_joint_pos.append(rot_matrix.dot(joint_pos_platform * np.array([-1, 1, 1])))
        ball_joint_pos.append(rot_matrix.dot(joint_pos_platform * np.array([-1, -1, 1])))

        for ball_joint in ball_joint_pos:
            target_pos.append(platform_pos + ball_joint)

        return target_pos


    def get_rotation_matrix(self, orientation):
        """
            Returns rotation matrix calculated with orientation value.

            :param orientation: Orientation of platform.
            :type orientation: list[float].
            :return: Retuns rotation matrix.
            :rtype:: ndarray.
        """
        if len(orientation) == 3:
            r_mat = R.from_euler('xyz', orientation, degrees=False).as_matrix() 
            return r_mat
        elif len(orientation) == 4:
            r_mat = R.from_quat(orientation).as_matrix()
            return r_mat
        else:
            print('Wrong input for orientation.')
            exit()


    def read_from_csv(self, header = False):
        """
            Reads data from csv file.

            :param header: Specify whether csv file have header or not.
            :type header: Bool.
            :return: None.
            :rtype: None.
        """
        f = open(GLOBAL_AUTOGENERATED_DIRECTORY + TRAJ_PLATFORM_FILE_NAME, 'r')
        for line in csv.reader(f):
            if header:
                header = False
            else:
                temp = []
                for e in line:
                    try:
                        temp.append(float(e))
                    except:
                        temp.append(e)
                self.data.append(temp)
        f.close()


if __name__ == '__main__':
    PybulletIKClass()
