'''
    Python script to go to folders and update calculated data files.
'''

import math 
import csv 
import os 
from data_processing import *

class UpdateDataClass():

    def __init__(
        self,
        input_directory = '', 
        noise_test = False,
    ):

        list_of_folders = []
        list_of_files = []

        list_of_folders = self.get_list_of_folders(input_directory)

        if noise_test:
            list_of_folders.append(input_directory)

        for folder in list_of_folders:
            list_of_files = self.get_list_of_files(folder)
            for file in list_of_files:
                if file[-28:-24] == "data":
                    if file[54:65] == "history_bin":
                        continue
                    data_file = file 
                    calculated_file = file[:-28] + 'calculated' + file[-24:]
                    new_calculated_data_file = file[:-28] + 'updated_calculated' + file[-24:]
                    print("---\nUpdating file:", data_file)
                    DataProcessClass(
                        name_of_data_csv = data_file,
                        robot_env = "solo", # pybullet / solo
                        point_on_platform = [0,0,0],
                        raw_data_traj_platform = calculated_file,
                        external_output_directory = new_calculated_data_file, # specify if you do not want to use config output directory
                        external_output_file_name = "",
                        save_data = False,
                        save_history = True,
                        update_data = True,
                    )

                    print("Saved file:", new_calculated_data_file)


    def get_list_of_folders(self, input_directory):
        directory_list = []
        for root, dirs, files in os.walk(input_directory, topdown=False):
            for name in dirs:
                if root[-11:] == 'history_bin': continue
                directory_list.append(os.path.join(root, name))
        return directory_list
        

    def get_list_of_files(self, input_directory):
        files_list = []
        for root, dirs, files in os.walk(input_directory, topdown=False):
            for name in files:
                files_list.append(os.path.join(root, name))
        return files_list

if __name__ == "__main__":
    UpdateDataClass(
        input_directory='/home/nayan/Downloads/[0219]-individual-DOF',
        noise_test = False  
    )