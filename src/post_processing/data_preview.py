"""
    Python script to preview stored data
"""

import csv
import numpy as np 
import matplotlib.pyplot as plt
import math
import argparse
import sys, os
sys.path.append('./')
from config import *

class DataPreviewClass():

    def __init__(self, 
        name_of_data_csv_file=None,
        name_of_calculated_csv_file=None,
        robot_env = '',                             # pybullet / solo
        plot_fr_joint_angles = False,               # for joint angles of front right leg
        plot_calculated_pos_data = False,           # for calculated pos
        plot_calculated_vel_data = False,           # for calculated vel
        plot_calculated_acc_data = False,           # for calculated acc
        plot_imu_data = False,                      # for imu data
        plot_circular_traj_platform = False,        # for circular trajectory platform plot
        plot_combined_pose_graph = False,           # for combined 6x3 pose graph
        plot_x_min = None,                          # for x min in x-axis
        plot_x_max = None                           # for x max in x-axis
    ):
        self.name_of_data_csv_file = name_of_data_csv_file 
        self.name_of_calculated_csv_file = name_of_calculated_csv_file 
        self.robot_env = robot_env
        self.plot_fr_joint_angles = plot_fr_joint_angles
        self.plot_calculated_pos_data = plot_calculated_pos_data
        self.plot_calculated_vel_data = plot_calculated_vel_data
        self.plot_calculated_acc_data = plot_calculated_acc_data
        self.plot_imu_data = plot_imu_data
        self.plot_circular_traj_platform = plot_circular_traj_platform
        self.plot_combined_pose_graph = plot_combined_pose_graph
        self.plot_x_min = int(plot_x_min) if plot_x_min is not None else None
        self.plot_x_max = int(plot_x_max) if plot_x_max is not None else None

        self.imu_data = None

        self.global_g = 9.81

        if self.robot_env == '':
            print("Robot env not specified. Exiting!")
            exit(-1)

        print('Loading data...', end='\r')

        if self.plot_fr_joint_angles or self.plot_imu_data or self.plot_calculated_vel_data or self.plot_calculated_acc_data or self.plot_calculated_pos_data or self.plot_circular_traj_platform:
            if self.plot_fr_joint_angles:self.init_fr_leg_params()
            try:
                if self.plot_fr_joint_angles:self.fill_values_from_data_csv()
                self.fill_values_from_calculated_csv()
            except Exception as e:
                print("Unable to fill values from csv. Is csv empty? ==>", self.name_of_data_csv_file)
                print("Excpetion:", e)
                exit(-1)

        print('Loading data...done')

        if self.robot_env == 'pybullet': 
            self.frequency = 240
            if self.plot_fr_joint_angles:
                self.curr_jointAngles = self.map_motors_according_to_ctrl_robot(self.curr_jointAngles)
                self.target_jointAngles = self.map_motors_according_to_ctrl_robot(self.target_jointAngles)
                self.current_value = self.map_motors_according_to_ctrl_robot(self.current_value)
        elif self.robot_env == 'solo':
            self.frequency = 1000

        print("Plotting...", end='\r')
        if self.plot_fr_joint_angles: self.fr_joint_angles_plotter()
        if self.plot_calculated_pos_data: self.calculated_pos_data_plotter()
        if self.plot_calculated_vel_data: self.calculated_vel_data_plotter()
        if self.plot_calculated_acc_data: self.calculated_acc_data_plotter()
        if self.plot_imu_data: self.raw_imu_data_plotter()
        if self.plot_circular_traj_platform: self.circular_traj_platform_plotter()
        if self.plot_combined_pose_graph: self.combined_pose_graph_v()
 
        print("Plotting...done")
        plt.show()
        print("Completed!")


    def fill_values_from_calculated_csv(self):
        """
            Fills calculated data values from csv file. 

            :return: None.
            :rtype: None.
        """
        raw_data = np.array(self.get_raw_data_from_csv(self.name_of_calculated_csv_file, header=True))
        
        self.platform_sys_time = raw_data[:, 0]
        self.platform_pos_calc = raw_data[:, 1 : 4]
        self.platform_ang_calc = raw_data[:, 4: 7]
        self.platform_lin_vel_calc = raw_data[:, 7: 10]
        self.platform_ang_vel_calc = raw_data[:, 10: 13]
        self.platform_lin_acc_calc = raw_data[:, 13: 16]
        self.platform_ang_acc_calc = raw_data[:, 16: 19]
        self.platform_pos = raw_data[:, 19 : 22]
        self.platform_ang = raw_data[:, 22: 25]

        self.platform_lin_vel = raw_data[:, 25 : 28]
        self.platform_ang_vel = raw_data[:, 28: 31]
        self.platform_lin_acc = raw_data[:, 31 : 34]
        self.platform_ang_acc = raw_data[:, 34: 37]

        self.transformted_lin_acc_imu_data = raw_data[:, 37 : 40]
        self.imu_calc_angular_acceleration = raw_data[:, 40 : 43]


    def init_fr_leg_params(self):
        """
            Initializes motor mapping and parameters for fr joint leg. 

            :return: None.
            :rtype: None.
        """
        self.motor_mapping = {
            "bl_hip" : 0,
            "br_hip" : 1,
            "bl_lower" : 2,
            "bl_upper" : 3,
            "br_lower" : 4,
            "br_upper" : 5,
            "fl_hip" : 6,
            "fr_hip" : 7,
            "fl_lower" : 8,
            "fl_upper" : 9,
            "fr_lower" : 10,
            "fr_upper" : 11,
            0 : "bl_hip",
            1 : "br_hip",
            2 : "bl_lower",
            3 : "bl_upper",
            4 : "br_lower",
            5 : "br_upper",
            6 : "fl_hip",
            7 : "fr_hip",
            8 : "fl_lower",
            9 : "fl_upper",
            10 : "fr_lower",
            11 : "fr_upper" 
        }
        self.iq_sat = 12
        self.seq_num = []
        self.time_stamp = [] 
        self.curr_jointAngles = [] 
        self.target_jointAngles = []
        self.current_value = []
    

    def map_motors_according_to_ctrl_robot(self, values):
        """
            Maps PyBullet motor indices to solo robot motor indices. 

            :param values: Motor values with motor index following PyBullet motor index convention.
            :type values: ndarray.
            :return: Updated motor values with motor index following SOLO robot motor index convention.
            :rtype: ndarray.
        """
        values = np.array(values)

        if len(values.T) != 12 and len(values.T) != 16:
            print("Number of joint positions != 12 or 16. Exiting!")
            exit(-1) 

        if len(values.T) == 16: # removing dummy joints if input
            dummy_joints = [3,7,11,15]
            updated_values = []
            for v in values:
                temp = []
                for ti, tv in enumerate(v):
                    if ti in dummy_joints:
                        continue
                    else:
                        temp.append(tv)
                updated_values.append(temp)
        
            values = updated_values
        
        mapped_values = []
        for value in values:
            mapped_value = [None] * 12
            mapped_value[self.motor_mapping["bl_hip"]] = - value[6] # bl_hip = hip_left_back 
            mapped_value[self.motor_mapping["br_hip"]] = value[9] # br_hip = hip_right_back
            mapped_value[self.motor_mapping["bl_lower"]] = value[8] # bl_lower = lower_leg_left_back
            mapped_value[self.motor_mapping["bl_upper"]] = value[7] # bl_upper = upper_leg_left_back
            mapped_value[self.motor_mapping["br_lower"]] = value[11] # br_lower = lower_leg_right_back
            mapped_value[self.motor_mapping["br_upper"]] = value[10] # br_upper = upper_leg_right_back
            mapped_value[self.motor_mapping["fl_hip"]] = value[0] # fl_hip = hip_left_front
            mapped_value[self.motor_mapping["fr_hip"]] = - value[3] # fr_hip = hip_right_front
            mapped_value[self.motor_mapping["fl_lower"]] = value[2] # fl_lower = lower_leg_left_front
            mapped_value[self.motor_mapping["fl_upper"]] = value[1] # fl_upper = upper_leg_left_front
            mapped_value[self.motor_mapping["fr_lower"]] = value[5] # fr_lower = lower_leg_right_front
            mapped_value[self.motor_mapping["fr_upper"]] = value[4] # fr_upper = upper_leg_right_front
            mapped_values.append(mapped_value)
        return np.array(mapped_values)

    
    def fill_values_from_data_csv(self):
        """
            Fills data values from data csv file. 

            :return: None.
            :rtype: None.
        """
        raw_data = np.array(self.get_raw_data_from_csv(self.name_of_data_csv_file, header=True))

        if self.name_of_data_csv_file == GLOBAL_OUTPUT_DIRECTORY + PYBULLET_DATA_OUTPUT_FILE_NAME:
            self.seq_num = raw_data[:, 0]
            self.time_stamp = self.seq_num
            self.curr_jointAngles = raw_data[:, 1 : 17]
            self.target_jointAngles = raw_data[:, 17 : 33]     
            self.current_value = raw_data[:, 33 : 49]   
            self.imu_data = None 
  
        else:
            self.time_stamp = raw_data[:-TIME_INTERPOLATE_LANDING+1, 0]
            self.time_stamp = self.time_stamp - self.time_stamp[0] # correct timestamp
            self.curr_jointAngles = raw_data[:-TIME_INTERPOLATE_LANDING+1, 1 : 13]
            self.target_jointAngles = raw_data[:-TIME_INTERPOLATE_LANDING+1, 13 : 25]
            self.current_value = raw_data[:-TIME_INTERPOLATE_LANDING+1, 25 : 37]
            self.imu_data = raw_data[:-TIME_INTERPOLATE_LANDING+1, 37 : 49]
         

    def get_raw_data_from_csv(self, name_of_data_csv_file, header=True):
        """
            Returns raw data from any csv file. 

            :param name_of_data_csv_file: Name of csv file.
            :type name_of_data_csv_file: str.
            :param header: Specify whether csv file have header or not.
            :type header: Bool.
            :return: Returns list of rows from csv file.
            :rtype: List[List[Float]].
        """
        f = open(name_of_data_csv_file)
        csv_reader = csv.reader(f)
        data = [] 
        header_skipped = False 
        for line in csv_reader:
            temp = []
            if not header_skipped and header:
                header_skipped = True 
                continue 
            for e in line:
                try:
                    temp.append(float(e))
                except:
                    temp.append(e)
            data.append(temp)
        return data 


    def fr_joint_angles_plotter(self, name_of_graph=''):
        """
            Plots graph for Front Right Leg. 

            :param name_of_graph: Name of graph. 
            :type name_of_graph: str.
            :return: None.
            :rtype: None.
        """
        if name_of_graph == '':
            name_of_graph = "Joint Angles for Front Right Leg"
        
        sf = 9 # scaling factor for motor angle
        if self.name_of_data_csv_file == GLOBAL_OUTPUT_DIRECTORY+PYBULLET_DATA_OUTPUT_FILE_NAME:
            sf = 1 

        rfh_c = []
        rfu_c = []
        rfl_c = []
        rfh_t = []
        rfu_t = []
        rfl_t = []
        rfh_curr = []
        rfu_curr = []
        rfl_curr = []

        for i in range(len(self.curr_jointAngles)-1):
            rfh_c.append([math.degrees(float(self.curr_jointAngles[i][self.motor_mapping['fr_hip']])/sf)])
            rfu_c.append([math.degrees(float(self.curr_jointAngles[i][self.motor_mapping['fr_upper']])/sf)])
            rfl_c.append([math.degrees(float(self.curr_jointAngles[i][self.motor_mapping['fr_lower']])/sf)])
            rfh_t.append([math.degrees(float(self.target_jointAngles[i][self.motor_mapping['fr_hip']])/sf)])
            rfu_t.append([math.degrees(float(self.target_jointAngles[i][self.motor_mapping['fr_upper']])/sf)])
            rfl_t.append([math.degrees(float(self.target_jointAngles[i][self.motor_mapping['fr_lower']])/sf)])
            rfh_curr.append([float(self.current_value[i][self.motor_mapping['fr_hip']])])
            rfu_curr.append([float(self.current_value[i][self.motor_mapping['fr_upper']])])
            rfl_curr.append([float(self.current_value[i][self.motor_mapping['fr_lower']])])

        # self.rfh_c = rfh_c
        # self.rfu_c = rfu_c
        # self.rfl_c = rfl_c
        # self.rfh_t = rfh_t
        # self.rfu_t = rfu_t
        # self.rfl_t = rfl_t

        fig, axs = plt.subplots(2, 3, figsize=(15, 10), sharex=True)

        axs[0, 0].plot(rfh_c, label='actual angle', color='royalblue', alpha=0.8)
        axs[0, 1].plot(rfu_c, label='actual angle', color='royalblue', alpha=0.8)
        axs[0, 2].plot(rfl_c, label='actual angle', color='royalblue', alpha=0.8)
        axs[0, 0].plot(rfh_t, label='target angle', color='orange', alpha=0.8)
        axs[0, 1].plot(rfu_t, label='target angle', color='orange', alpha=0.8)
        axs[0, 2].plot(rfl_t, label='target angle', color='orange', alpha=0.8)

        axs[1, 0].plot(rfh_curr, label='current', color='royalblue', alpha=0.8)
        axs[1, 1].plot(rfu_curr, label='current', color='royalblue', alpha=0.8)
        axs[1, 2].plot(rfl_curr, label='current', color='royalblue', alpha=0.8)

        ja_limits = 150

        axs[0,0].set_ylim([-50, 50])
        axs[0,1].set_ylim([-100, 0])
        axs[0,2].set_ylim([50, 150])

        axs[1,0].set_ylim([-self.iq_sat, self.iq_sat])
        axs[1,1].set_ylim([-self.iq_sat, self.iq_sat])
        axs[1,2].set_ylim([-self.iq_sat, self.iq_sat])
        
        for i in range(2):
            axs[i, 0].set_title('Right Front Hip')
            axs[i, 1].set_title('Right Front Upper')
            axs[i, 2].set_title('Right Front Lower')

            axs[i, 0].set_xlabel('Time (ms)')
            axs[i, 1].set_xlabel('Time (ms)')
            axs[i, 2].set_xlabel('Time (ms)')

        if (self.plot_x_max is not None) or (self.plot_x_min is not None):
            for i in range(2):
                for j in range(3):
                    axs[i,j].set_xlim([self.plot_x_min, self.plot_x_max])

        axs[0, 2].legend()

        axs[0, 0].set_ylabel('Joint Angles (degree)')
        axs[1, 0].set_ylabel('Current (A)')

        fig.suptitle(name_of_graph, fontsize=16)
        axs[1, 2].legend()

        # plt.show()


    def calculated_pos_data_plotter(self):
        """
            Plots graph for calculated and target platform position. 

            :return: None.
            :rtype: None.
        """
        fig, axs = plt.subplots(3, 2, figsize=(15, 10), sharex=True)
        fig.suptitle('Calculated position and orientation')
        self.platform_pos_calc = np.array(self.platform_pos_calc)
        self.platform_ang_calc = np.array(self.platform_ang_calc)
        axs[0, 0].set_title('Position X')
        axs[1, 0].set_title('Position Y')
        axs[2, 0].set_title('Position Z')
        axs[0, 1].set_title('Rotation X')
        axs[1, 1].set_title('Rotation Y')
        axs[2, 1].set_title('Rotation Z')
        axs[1, 0].set_ylabel('m')
        axs[1, 1].set_ylabel('degree')

        axs[2, 0].set_xlabel('time (ms)')
        axs[2, 1].set_xlabel('time (ms)')

        for i in range(3):
            temp_platform_ang_calc_degrees = np.array(list([math.degrees(e) for e in self.platform_ang_calc[:, i]]))
            temp_platform_ang_degrees = np.array(list([math.degrees(e) for e in self.platform_ang[:, i]]))

            axs[i, 0].plot(self.platform_sys_time, self.platform_pos_calc[:,i], color='royalblue', alpha=0.5, label='calculated')
            axs[i, 0].plot(self.platform_pos[:,i], color='orange', label='target')
            axs[i, 1].plot(self.platform_sys_time, temp_platform_ang_calc_degrees, color='royalblue', alpha=0.5, label='calculated')
            axs[i, 1].plot(temp_platform_ang_degrees, color='orange', label='target')
        axs[0, 0].legend()

        if (self.plot_x_max is not None) or (self.plot_x_min is not None):
            for i in range(3):
                for j in range(2):
                    axs[i,j].set_xlim([self.plot_x_min, self.plot_x_max])

        # plt.show()


    def calculated_vel_data_plotter(self):
        """
            Plots graph for calculated and target platform velocity. 

            :return: None.
            :rtype: None.
        """
        fig, axs = plt.subplots(3, 2, figsize=(15, 10), sharex=True)
        fig.suptitle('Calculated Velocity')
        self.platform_lin_vel = np.array(self.platform_lin_vel)
        self.platform_lin_vel_calc = np.array(self.platform_lin_vel_calc)
        self.platform_ang_vel = np.array(self.platform_ang_vel)
        self.platform_ang_vel_calc = np.array(self.platform_ang_vel_calc)
        axs[0, 0].set_title('Linear Velocity X')
        axs[1, 0].set_title('Linear Velocity Y')
        axs[2, 0].set_title('Linear Velocity Z')
        axs[0, 1].set_title('Angular Velocity X')
        axs[1, 1].set_title('Angular Velocity Y')
        axs[2, 1].set_title('Angular Velocity Z')
        axs[1, 0].set_ylabel('m/s')
        axs[1, 1].set_ylabel('degree/s')

        axs[2, 0].set_xlabel('time (ms)')
        axs[2, 1].set_xlabel('time (ms)')

        for i in range(3):
            temp_platform_ang_calc_degrees = np.array(list([math.degrees(e) for e in self.platform_ang_vel_calc[:, i]]))
            temp_platform_ang_degrees = np.array(list([math.degrees(e) for e in self.platform_ang_vel[:, i]]))
            if self.robot_env == 'solo' or self.imu_data is not None:
                temp_gyro_degree = np.array(list([math.degrees(g) for g in self.imu_data[:, 3+i]]))
            # temp_transformed_ang_vel_imu = np.array(list([math.degrees(g) for g in self.transformed_ang_vel_imu_data[:, i]]))
            # temp_transformed_lin_vel_imu = np.array(list([g for g in self.transformed_lin_vel_imu_data[:, i]]))

            # axs[i, 0].plot(self.platform_sys_time, temp_transformed_lin_vel_imu, color='cyan', alpha=0.75, label='imu@ center of platform')
            axs[i, 0].plot(self.platform_sys_time, self.platform_lin_vel_calc[:,i], color='royalblue', alpha=0.5, label = 'calculated')
            axs[i, 0].plot(self.platform_lin_vel[:,i], color='orange', label = 'target')

            axs[i, 1].plot(self.platform_sys_time, temp_platform_ang_calc_degrees, color='royalblue', alpha=0.5, label = 'calculated')
            axs[i, 1].plot(temp_platform_ang_degrees, color='orange', label = 'target')
            if self.robot_env == 'solo' or self.imu_data is not None:
                axs[i, 1].plot(self.platform_sys_time, temp_gyro_degree, color='red', alpha=0.5, label='imu gyroscope at imu')
            # axs[i, 1].plot(self.platform_sys_time, temp_transformed_ang_vel_imu, color='cyan', alpha=0.75, label='imu gyroscope@ center of platform')

            axs[i, 0].legend()
            axs[i, 1].legend()

        plt.legend()
        
        if (self.plot_x_max is not None) or (self.plot_x_min is not None):
            for i in range(3):
                for j in range(2):
                    axs[i,j].set_xlim([self.plot_x_min, self.plot_x_max])

        # plt.show()


    def calculated_acc_data_plotter(self):
        """
            Plots graph for calculated and target platform acceleration. 

            :return: None.
            :rtype: None.
        """
        fig, axs = plt.subplots(3, 2, figsize=(15, 10), sharex=True)
        fig.suptitle('Calculated Acceleration')
        self.platform_lin_acc = np.array(self.platform_lin_acc)
        self.platform_lin_acc_calc = np.array(self.platform_lin_acc_calc)
        self.platform_ang_acc = np.array(self.platform_ang_acc)
        self.platform_ang_acc_calc = np.array(self.platform_ang_acc_calc)
        axs[0, 0].set_title('Linear Acceleration X')
        axs[1, 0].set_title('Linear Acceleration Y')
        axs[2, 0].set_title('Linear Acceleration Z')
        axs[0, 1].set_title('Angular Acceleration X')
        axs[1, 1].set_title('Angular Acceleration Y')
        axs[2, 1].set_title('Angular Acceleration Z')
        axs[1, 0].set_ylabel('m/s^2')
        axs[1, 1].set_ylabel('degree/s^2')

        axs[2, 0].set_xlabel('time (ms)')
        axs[2, 1].set_xlabel('time (ms)')
        
        for i in range(3):
            temp_platform_ang_calc_degrees = np.array(list([math.degrees(e) for e in self.platform_ang_acc_calc[:, i]]))
            temp_platform_ang_degrees = np.array(list([math.degrees(e) for e in self.platform_ang_acc[:, i]]))

            # temp_g_raw = np.array(list([g*self.global_g for g in self.imu_data[:, i]]))
            # temp_g_kalman = np.array(list([g*self.global_g for g in self.imu_data[:, 9+i]]))
            if self.robot_env == 'solo' or self.imu_data is not None:
                temp_g_raw = np.array(list([g for g in self.imu_data[:, i]]))
                temp_g_kalman = np.array(list([g for g in self.imu_data[:, 9+i]]))

            if self.robot_env == 'solo' or self.imu_data is not None:
                temp_transformed_imu = np.array(list([g for g in self.transformted_lin_acc_imu_data[:, i]]))
                temp_calc_angular_acceleration = np.array(list([math.degrees(g) for g in self.imu_calc_angular_acceleration[:, i]]))

            axs[i, 0].plot(self.platform_sys_time, self.platform_lin_acc_calc[:,i], color='royalblue', alpha=0.5, label='calculated')

            if self.robot_env == 'solo' or self.imu_data is not None:
                axs[i, 0].plot(self.platform_sys_time, temp_g_raw, color='red', alpha=0.5, label='raw imu ground truth')
                axs[i, 0].plot(self.platform_sys_time, temp_g_kalman, color='green', alpha=0.5, label='kalman filter acceleration')

                axs[i, 0].plot(self.platform_sys_time, temp_transformed_imu, color='cyan', alpha=0.8, label='transformed imu acc@ center of platform')
                axs[i, 1].plot(self.platform_sys_time, temp_calc_angular_acceleration, color='cyan', linewidth=0.8, alpha=0.5, label='calculated transformed imu acc@ center of platform')
            
            axs[i, 0].plot(self.platform_lin_acc[:,i], color='orange', label='target')

            axs[i, 1].plot(self.platform_sys_time, temp_platform_ang_calc_degrees, color='royalblue', alpha=0.5, linewidth=0.8, label='calculated')
            axs[i, 1].plot(temp_platform_ang_degrees, color='orange', label='target')
            axs[i, 0].legend()
            axs[i, 1].legend()

        # plt.show()

        if (self.plot_x_max is not None) or (self.plot_x_min is not None):
            for i in range(3):
                for j in range(2):
                    axs[i,j].set_xlim([self.plot_x_min, self.plot_x_max])


    def raw_imu_data_plotter(self):
        """
            Plots graph for raw imu data. 

            :return: None.
            :rtype: None.
        """
        if self.robot_env != 'solo' or self.imu_data is None:
            print("IMU Data only available for SOLO env!")
            return

        fig, axes = plt.subplots(4, 3, figsize=(15, 10), sharex=True)
        row_labels = [
            'accelerometer',
            'gyroscope',
            'attitude',
            'linear_acceleration'
        ]
        for row in range(len(row_labels)):
            for iaxes in range(3):
                ax = axes[row][iaxes]
                ax.grid()
                ax.set_title(row_labels[row] + ' [' + ['x', 'y', 'z'][iaxes] + ']')
                # ax.plot(self.time_stamp, self.imu_data[:, 3 * row + iaxes], alpha=0.2)
                if row == 0:
                    if iaxes==0:
                        ax.set_ylabel('m/s^2')
                    ax.plot(self.time_stamp, self.imu_data[:, 3 * row + iaxes], alpha=0.8, linewidth=0.8, label='imu pos', color='royalblue')
                    ax.plot(self.time_stamp, self.transformted_lin_acc_imu_data[:, iaxes], alpha=0.8, linewidth=0.8, color='cyan', label='center of platform pos')

                    ax.legend()
                elif row == 1:
                    if iaxes==0:
                        ax.set_ylabel('rad/s')
                    ax.plot(self.time_stamp, self.imu_data[:, 3 * row + iaxes], alpha=0.8, linewidth=0.5, label='imu pos', color='royalblue')
                    ax.legend()
                else:
                    ax.plot(self.time_stamp, self.imu_data[:, 3 * row + iaxes], alpha=0.8, linewidth=0.8, color='royalblue')
                if row == 3:
                    if iaxes==0:
                        ax.set_ylabel('g')
                    ax.set_xlabel('Time (ms)')

        fig.suptitle('Raw IMU data')

        if (self.plot_x_max is not None) or (self.plot_x_min is not None):
            for i in range(4):
                for j in range(3):
                    axes[i,j].set_xlim([self.plot_x_min, self.plot_x_max])
        

    def msd(self, arr1, arr2):
        """
            Calculates and returns mean squared distance. 

            :param arr1: Array 1.
            :type arr1: List[Float].
            :param arr2: Array 2.
            :type arr2: List[Float].

            :return: Mean squared distance between two arrays.
            :rtype: Float.
        """
        return np.square(np.subtract(arr1,arr2)).mean()

    
    def circular_traj_platform_plotter(self):
        """
            Plots circular trajectory with x-axis and y-axis. 

            :return: None.
            :rtype: None.
        """
        fig, axs = plt.subplots(1, 2, figsize=(22.5, 10), sharex=False)
        axs[0].set_title("Translation")
        axs[1].set_title("Rotation")

        temp_platform_ang_degrees_0 = np.array(list([math.degrees(e) for e in self.platform_ang[:, 0]]))
        temp_calc_platform_ang_degrees_0 = np.array(list([math.degrees(e) for e in self.platform_ang_calc[:, 0]]))
        temp_platform_ang_degrees_1 = np.array(list([math.degrees(e) for e in self.platform_ang[:, 1]]))
        temp_calc_platform_ang_degrees_1 = np.array(list([math.degrees(e) for e in self.platform_ang_calc[:, 1]]))

        axs[0].plot(self.platform_pos_calc[:,0],self.platform_pos_calc[:,1], color='royalblue', alpha=0.5, label='calculated')
        axs[1].plot(temp_calc_platform_ang_degrees_0[:],temp_calc_platform_ang_degrees_1[:], color='royalblue', alpha=0.5, label='calculated')
        
        axs[0].plot(self.platform_pos_calc[0,0],self.platform_pos_calc[0,1], marker='o', linestyle = 'None', color='royalblue', label='calculated start')
        axs[0].plot(self.platform_pos_calc[-1,0],self.platform_pos_calc[-1,1], marker='x', linestyle = 'None', color='royalblue', label='calculated end')
        axs[1].plot(temp_calc_platform_ang_degrees_0[0],temp_calc_platform_ang_degrees_1[0], marker='o', linestyle = 'None', color='royalblue', label='calculated start')
        axs[1].plot(temp_calc_platform_ang_degrees_0[-1],temp_calc_platform_ang_degrees_1[-1], marker='x', linestyle = 'None', color='royalblue', label='calculated end')

        axs[0].plot(self.platform_pos[:,0],self.platform_pos[:,1], color='orange', label='target') 
        axs[1].plot(temp_platform_ang_degrees_0[:],temp_platform_ang_degrees_1[:], color='orange', label='target')
      
        axs[0].plot(self.platform_pos[0,0],self.platform_pos[0,1], marker='o', linestyle = 'None', color='orange', label='target start')
        axs[0].plot(self.platform_pos[-1,0],self.platform_pos[-1,1], marker='x', linestyle = 'None', color='orange', label='target end')
        axs[1].plot(temp_platform_ang_degrees_0[0],temp_platform_ang_degrees_1[0], marker='o', linestyle = 'None', color='orange', label='target start')
        axs[1].plot(temp_platform_ang_degrees_0[-1],temp_platform_ang_degrees_1[-1], marker='x', linestyle = 'None', color='orange', label='target end')

        t_lim = 0.06 # m
        r_lim = 50 # deg

        axs[0].set_xlim([-t_lim, t_lim])
        axs[0].set_ylim([-t_lim, t_lim])
        axs[1].set_xlim([-r_lim, r_lim])
        axs[1].set_ylim([-r_lim, r_lim])

        axs[0].set_xlabel('x (m)')
        axs[0].set_ylabel('y (m)')

        axs[1].set_xlabel('x (deg)')
        axs[1].set_ylabel('y (deg)')

        axs[0].legend()
        axs[1].legend()

        axs[0].grid()
        axs[1].grid()


    def print_msd_results(self):
        """
            Prints MSD results for platform translation and rotation.

            :return: None.
            :rtype: None.
        """
        print("MSD of translation at x:",'%.3f'% (self.msd(self.platform_pos_calc[:, 0], self.platform_pos[:, 0])*1000), "mm")
        print("MSD of translation at y:",'%.3f'% (self.msd(self.platform_pos_calc[:, 1], self.platform_pos[:, 1])*1000), "mm")
        print("MSD of translation at z:",'%.3f'% (self.msd(self.platform_pos_calc[:, 2], self.platform_pos[:, 2])*1000), "mm")
        print("MSD translation: ",'%.3f'% (self.msd(self.platform_pos_calc[:, :3], self.platform_pos[:, :3])*1000), "mm")
        print("MSD of rotation at x:",'%.3f'% math.degrees((self.msd(self.platform_ang_calc[:, 0], self.platform_ang[:, 0]))), "deg")
        print("MSD of rotation at y:",'%.3f'% math.degrees((self.msd(self.platform_ang_calc[:, 1], self.platform_ang[:, 1]))), "deg")
        print("MSD of rotation at z:",'%.3f'% math.degrees((self.msd(self.platform_ang_calc[:, 2], self.platform_ang[:, 2]))), "deg")
        print("MSD rotation: ",'%.3f'% math.degrees(self.msd(self.platform_ang_calc[:, :3], self.platform_ang[:, :3])), "deg")


    def combined_pose_graph_v(self):
        """
            Plots combined graph at specified x-axis range for calculated and target platform position, velocity, acceleration. 

            :return: None.
            :rtype: None.
        """
        fig, axs = plt.subplots(6, 3, figsize=(10, 15))
        fig.suptitle("Position, Velocity, Acceleration for 6 DoF Sine Motion")
        axs[0, 0].set_title('Position (m)')
        axs[0, 1].set_title('Linear Velocity (m/s)')
        axs[0, 2].set_title('Linear Acceleration (m/s^2)')
        axs[3, 0].set_title('Orientation (deg)')
        axs[3, 1].set_title('Angular Velocity (deg/s)')
        axs[3, 2].set_title('Angular Acceleration (deg/s^2)')
        
        axs[5, 1].set_xlabel('time (ms)')

        axs[0, 0].set_ylabel('Translation X')
        axs[1, 0].set_ylabel('Translation Y')
        axs[2, 0].set_ylabel('Translation Z')
        axs[3, 0].set_ylabel('Rotation X')
        axs[4, 0].set_ylabel('Rotation Y')
        axs[5, 0].set_ylabel('Rotation Z')

        temp_platform_ang_calc_degrees = []
        temp_platform_ang_degree = []
        temp_platform_ang_calc_degrees.append(np.array(list([math.degrees(e) for e in self.platform_ang_calc[:, 0]])))
        temp_platform_ang_calc_degrees.append(np.array(list([math.degrees(e) for e in self.platform_ang_calc[:, 1]])))
        temp_platform_ang_calc_degrees.append(np.array(list([math.degrees(e) for e in self.platform_ang_calc[:, 2]])))
        temp_platform_ang_calc_degrees = np.array(temp_platform_ang_calc_degrees)
        temp_platform_ang_degree.append(np.array(list([math.degrees(e) for e in self.platform_ang[:, 0]])))
        temp_platform_ang_degree.append(np.array(list([math.degrees(e) for e in self.platform_ang[:, 1]])))
        temp_platform_ang_degree.append(np.array(list([math.degrees(e) for e in self.platform_ang[:, 2]])))
        temp_platform_ang_degree = np.array(temp_platform_ang_degree)

        temp_platform_ang_vel_calc_degrees = []
        temp_platform_ang_vel_degrees = []
        temp_platform_ang_vel_calc_degrees.append(np.array(list([math.degrees(e) for e in self.platform_ang_vel_calc[:, 0]])))
        temp_platform_ang_vel_calc_degrees.append(np.array(list([math.degrees(e) for e in self.platform_ang_vel_calc[:, 1]])))
        temp_platform_ang_vel_calc_degrees.append(np.array(list([math.degrees(e) for e in self.platform_ang_vel_calc[:, 2]])))
        temp_platform_ang_vel_calc_degrees = np.array(temp_platform_ang_vel_calc_degrees)
        temp_platform_ang_vel_degrees.append(np.array(list([math.degrees(e) for e in self.platform_ang_vel[:, 0]])))
        temp_platform_ang_vel_degrees.append(np.array(list([math.degrees(e) for e in self.platform_ang_vel[:, 1]])))
        temp_platform_ang_vel_degrees.append(np.array(list([math.degrees(e) for e in self.platform_ang_vel[:, 2]])))
        temp_platform_ang_vel_degrees = np.array(temp_platform_ang_vel_degrees)

        temp_gyro_degrees = []
        if self.robot_env == 'solo' or self.imu_data is not None:
            temp_gyro_degrees.append(np.array(list([math.degrees(-1*g) for g in self.imu_data[:, 3+0]])))
            temp_gyro_degrees.append(np.array(list([math.degrees(-1*g) for g in self.imu_data[:, 3+1]])))
            temp_gyro_degrees.append(np.array(list([math.degrees(-1*g) for g in self.imu_data[:, 3+2]])))
            temp_gyro_degrees = np.array(temp_gyro_degrees)

        temp_platform_ang_acc_calc_degrees = []
        temp_platform_ang_acc_degrees = []
        temp_platform_ang_acc_calc_degrees.append(np.array(list([math.degrees(e) for e in self.platform_ang_acc_calc[:, 0]])))
        temp_platform_ang_acc_calc_degrees.append(np.array(list([math.degrees(e) for e in self.platform_ang_acc_calc[:, 1]])))
        temp_platform_ang_acc_calc_degrees.append(np.array(list([math.degrees(e) for e in self.platform_ang_acc_calc[:, 2]])))
        temp_platform_ang_acc_calc_degrees = np.array(temp_platform_ang_acc_calc_degrees)
        temp_platform_ang_acc_degrees.append(np.array(list([math.degrees(e) for e in self.platform_ang_acc[:, 0]])))
        temp_platform_ang_acc_degrees.append(np.array(list([math.degrees(e) for e in self.platform_ang_acc[:, 1]])))
        temp_platform_ang_acc_degrees.append(np.array(list([math.degrees(e) for e in self.platform_ang_acc[:, 2]])))
        temp_platform_ang_acc_degrees = np.array(temp_platform_ang_acc_degrees)

        temp_g_raw = []
        temp_g_kalman = []
        if self.robot_env == 'solo' or self.imu_data is not None:
            temp_g_raw.append(np.array(list([g for g in self.imu_data[:, 0]])))
            temp_g_raw.append(np.array(list([g for g in self.imu_data[:, 1]])))
            temp_g_raw.append(np.array(list([g for g in self.imu_data[:, 2]])))
            temp_g_raw = np.array(temp_g_raw)

            temp_g_kalman.append(np.array(list([g for g in self.imu_data[:, 9+0]])))   
            temp_g_kalman.append(np.array(list([g for g in self.imu_data[:, 9+1]])))  
            temp_g_kalman.append(np.array(list([g for g in self.imu_data[:, 9+2]]))) 
            temp_g_kalman = np.array(temp_g_kalman)

        for i in range(3):
            seq_runtime = 3000
            seq_waittime = 2000

            start_= 2000 + i*(seq_runtime + seq_waittime)
            end_ = start_+seq_runtime
            padding = 500
            p_start = start_ - padding
            p_end = end_ + padding
            # translation
            axs[i,0].plot(self.platform_sys_time[p_start:p_end], self.platform_pos_calc[p_start:p_end,i], color='royalblue', alpha=0.5, label='calculated')
            axs[i,0].plot(self.platform_sys_time[p_start:p_end], self.platform_pos[p_start:p_end,i], color='orange', label='target')

            axs[i,1].plot(self.platform_sys_time[p_start:p_end], self.platform_lin_vel_calc[p_start:p_end,i], color='royalblue', alpha=0.5, label='calculated')
            axs[i,1].plot(self.platform_sys_time[p_start:p_end], self.platform_lin_vel[p_start:p_end,i], color='orange', label='target')

            axs[i,2].plot(self.platform_sys_time[p_start:p_end], self.platform_lin_acc_calc[p_start:p_end,i], color='royalblue', alpha=0.5, label='calculated')
            axs[i,2].plot(self.platform_sys_time[p_start:p_end], self.platform_lin_acc[p_start:p_end,i], color='orange', label='target')
            if self.robot_env == 'solo' or self.imu_data is not None:
                axs[i,2].plot(self.platform_sys_time[p_start:p_end], temp_g_kalman[i, p_start:p_end], color='cyan', alpha=0.5, label='imu')
            axs[i,2].set_ylim([-20,20])

            # rotation
            start_= (2000+3*(seq_runtime+seq_waittime)) + i*(seq_runtime + seq_waittime)
            end_ = start_+seq_runtime
            padding = 1000
            p_start = start_ - padding
            p_end = end_ + padding
            axs[i+3,0].plot(self.platform_sys_time[p_start:p_end], temp_platform_ang_calc_degrees[i, p_start:p_end], color='royalblue', alpha=0.5, label='calculated')
            axs[i+3,0].plot(self.platform_sys_time[p_start:p_end], temp_platform_ang_degree[i, p_start:p_end], color='orange', label='target')

            axs[i+3,1].plot(self.platform_sys_time[p_start:p_end], temp_platform_ang_vel_calc_degrees[i, p_start:p_end], color='royalblue', alpha=0.5, label='calculated')
            axs[i+3,1].plot(self.platform_sys_time[p_start:p_end], temp_platform_ang_vel_degrees[i, p_start:p_end], color='orange', label='target')
            if self.robot_env == 'solo' or self.imu_data is not None:
                axs[i+3,1].plot(self.platform_sys_time[p_start:p_end], temp_gyro_degrees[i, p_start:p_end], color='cyan', alpha=0.5, label='imu')
            # axs[1, i+3].set_ylim([-200,200])

            axs[i+3,2].plot(self.platform_sys_time[p_start:p_end], temp_platform_ang_acc_calc_degrees[i, p_start:p_end], color='royalblue', alpha=0.5, label='calculated')
            axs[i+3,2].plot(self.platform_sys_time[p_start:p_end], temp_platform_ang_acc_degrees[i, p_start:p_end], color='orange', label='target')
            axs[i+3,2].set_ylim([-5000,5000])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Debug options.')

    parser.add_argument('-all',
                    '--plot_all',
                    action='store_true',
                    help='plot all')

    parser.add_argument('-fr',
                    '--fr_leg',
                    action='store_true',
                    help='plot front right leg joint angles')

    parser.add_argument('-pos',
                    '--position',
                    action='store_true',
                    help='plot position and orientation')

    parser.add_argument('-vel',
                    '--velocity',
                    action='store_true',
                    help='plot linear and angular velocity')

    parser.add_argument('-acc',
                    '--acceleration',
                    action='store_true',
                    help='plot linear and angular velocity')

    parser.add_argument('-imu',
                    '--imu',
                    action='store_true',
                    help='plot imu')

    parser.add_argument('-circ',
                    '--circular_plt',
                    action='store_true',
                    help='plot circular platform trajectory')

    parser.add_argument('-xmin',
                        '--xminimum',
                        help='x minimum')

    parser.add_argument('-xmax',
                        '--xmaximum',
                        help='x maximum')

    if len(sys.argv) <= 1:
        parser.print_help(sys.stderr)
        print('No arguments given. Run script again with argument -all for all graphs.')
        exit(1)


    data_env = [GLOBAL_OUTPUT_DIRECTORY+SOLO_DATA_OUTPUT_FILE_NAME, GLOBAL_OUTPUT_DIRECTORY+SOLO_CALCULATED_FILE_NAME , 'solo']
    # data_env = [GLOBAL_OUTPUT_DIRECTORY+PYBULLET_DATA_OUTPUT_FILE_NAME, GLOBAL_OUTPUT_DIRECTORY+PYBULLET_CALCULATED_FILE_NAME, 'pybullet'] 

    preview_data = DataPreviewClass(
        name_of_data_csv_file = data_env[0] ,
        name_of_calculated_csv_file = data_env[1] ,
        robot_env = data_env[2] ,
        plot_fr_joint_angles = parser.parse_args().fr_leg or parser.parse_args().plot_all,
        plot_calculated_pos_data = parser.parse_args().position or parser.parse_args().plot_all,
        plot_calculated_vel_data = parser.parse_args().velocity or parser.parse_args().plot_all,
        plot_calculated_acc_data = parser.parse_args().acceleration or parser.parse_args().plot_all,
        plot_imu_data = parser.parse_args().imu or parser.parse_args().plot_all,
        plot_circular_traj_platform = parser.parse_args().circular_plt or parser.parse_args().plot_all,
        plot_x_min = parser.parse_args().xminimum,
        plot_x_max = parser.parse_args().xmaximum
    )