"""
    Python script to generate arbitrary trajectory
"""

import csv
import numpy as np 
from scipy.interpolate import interp1d
import math
from config import *

class GenerateArbitraryTrajectory_CSV_Class():

    def __init__(self,
        path_to_input_file = GLOBAL_INPUT_DIRECTORY,
        input_file_name = '',
        frequency = 240,
        threshold_amplitude = THRESHOLD_AMPLITUDE
    ): 
        self.threshold_amplitude = threshold_amplitude
        if input_file_name == '':
            print("Input file name is empty!")
            exit(-1)
            
        input_file_name = path_to_input_file + input_file_name
        arbitrary_sequences = self.read_from_csv(file_name=input_file_name)

        prev_pos = [0.0,0.0,0.0] # home offset added in program later
        prev_orn = [0.0,0.0,0.0] # home offset added in program later

        # Arbitrary Trajectory generated for initial wait time before trajectory starts. 
        GenerateArbitraryTrajectoryClass(
                flush = True, 
                trajectory_frequency = frequency,
                start_pos_xyz = prev_pos,
                start_orn_xyz = prev_orn,
                end_pos_xyz = prev_pos,
                end_orn_xyz = prev_orn,
                interpolate_time=2
            )

        for si, arbitrary_sequence in enumerate(arbitrary_sequences):
            f = False 

            local_start_pos_xyz = []
            local_start_orn_xyz = []
            local_end_pos_xyz = []
            local_end_orn_xyz = []
            local_interpolation_time = 5

            try:
                if si == 0:
                    for xyz_i in range(3):
                        local_start_pos_xyz.append(prev_pos[xyz_i])
                        local_start_orn_xyz.append(prev_orn[xyz_i])
                        local_end_pos_xyz.append(arbitrary_sequence[xyz_i])
                        local_end_orn_xyz.append(arbitrary_sequence[xyz_i+3])
                else:
                    local_start_pos_xyz = prev_pos 
                    local_start_orn_xyz = prev_orn 
                    for xyz_i in range(3):
                        local_end_pos_xyz.append(arbitrary_sequence[xyz_i])
                        local_end_orn_xyz.append(arbitrary_sequence[xyz_i+3])

                local_interpolation_time = arbitrary_sequence[-1] # interpolation time

            except:
                print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                print("ERROR:Check arbitrary input file. Input incorrect!")
                print("Exiting")
                print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                exit(-1)

            if si != 0:
                # checking if starting pose of next trajecoty == ending pose of previous trajectory 
                if not self.are_arrays_same(prev_pos, local_start_pos_xyz):
                    print("previous end position != current start position in seq:", si)
                    local_start_pos_xyz = prev_pos
                    print("current start position updated to be previous end position to avoid sudden jumps.")

                if not self.are_arrays_same(prev_orn, local_start_orn_xyz):
                    print("previous end orientation != current start orientationin seq:", si)
                    local_start_orn_xyz = prev_orn
                    print("current start orientation updated to be previous end orientation to avoid sudden jumps.")

            GenerateArbitraryTrajectoryClass(
                flush = f, 
                trajectory_frequency = frequency,
                start_pos_xyz = local_start_pos_xyz,
                start_orn_xyz = local_start_orn_xyz,
                end_pos_xyz = local_end_pos_xyz,
                end_orn_xyz = local_end_orn_xyz,
                interpolate_time = local_interpolation_time,
            )

            prev_pos = local_end_pos_xyz
            prev_orn = local_end_orn_xyz


    def are_arrays_same(self, arr1, arr2):
        """
            Checks if two arrays have same size and elements. 

            :param arr1: First array.
            :type arr1: list[].
            :param arr1: Second array.
            :type arr1: list[].
            :return: True if arrays are same, False if arrays are different.
            :rtype: Bool.
        """
        if len(arr1) != len(arr2):
            return False 
        for i in range(len(arr1)):
            if arr1[i] != arr2[i]:
                return False 
        return True

            
    def read_from_csv(self, file_name='', header=True):
        """
            Reads from csv file.

            :param file_name: Name of csv file. 
            :param type: String. 
            :param header: True if csv file contains header, False if csv file does not contain header.
            :return: Returns all lines from csv file.
            :rtype: list[ [[],[],..], [[],[],..], .. ].
        """
        self.r_file = open(file_name)
        csv_reader = csv.reader(self.r_file)
        lines = []
        for line in csv_reader:
            temp = []
            for elem_i, elem in enumerate(line):
                try:
                    if elem_i < 3:
                        if float(elem) > self.threshold_amplitude:
                            print("- Pos " + str(elem) + "mm is larger than tested mm threshold of solo robot of "+str(self.threshold_amplitude) + "mm. Using maximum threshold ("+ 
                                str(self.threshold_amplitude) +" mm) instead.")
                            temp.append(float(self.threshold_amplitude)/1000)
                        elif float(elem) < -self.threshold_amplitude:
                            print("- Pos " + str(elem) + "mm is smaller than tested mm threshold of solo robot of -"+str(self.threshold_amplitude) + "mm. Using minimum threshold (-"+ 
                                str(self.threshold_amplitude) +" mm) instead.")
                            temp.append(-1*float(self.threshold_amplitude)/1000)
                        else:
                            temp.append(float(elem) / 1000) # convert mm to m
                    elif elem_i >= 3 and elem_i < 6:
                        if float(elem) > self.threshold_amplitude:
                            print("- Orn " + str(elem) + "deg is larger than tested deg threshold of solo robot of "+str(self.threshold_amplitude) + "deg. Using maximum threshold ("+ 
                                str(self.threshold_amplitude) +" deg) instead.")
                            temp.append(float(math.radians(self.threshold_amplitude)))
                        elif float(elem) < -self.threshold_amplitude:
                            print("- Orn " + str(elem) + "deg is smaller than tested deg threshold of solo robot of -"+str(self.threshold_amplitude) + "deg. Using minimum threshold (-"+ 
                                str(self.threshold_amplitude) +" deg) instead.")
                            temp.append(float(-1*(math.radians(self.threshold_amplitude))))
                        else:
                            temp.append(math.radians(float(elem))) # conver deg to rad
                    else:
                        temp.append(int(elem)) # time in seconds
                    '''
                    try:
                        if elem_i < 3 or (elem_i > 5 and elem_i < 9):
                            if float(elem) > self.threshold_amplitude:
                                print("- Pos " + str(elem) + "mm is larger than tested mm threshold of solo robot of "+str(self.threshold_amplitude) + "mm. Using maximum threshold ("+ 
                                    str(self.threshold_amplitude) +" mm) instead.")
                                temp.append(float(self.threshold_amplitude)/1000)
                            elif float(elem) < -self.threshold_amplitude:
                                print("- Pos " + str(elem) + "mm is smaller than tested mm threshold of solo robot of -"+str(self.threshold_amplitude) + "mm. Using minimum threshold (-"+ 
                                    str(self.threshold_amplitude) +" mm) instead.")
                                temp.append(-1*float(self.threshold_amplitude)/1000)
                            else:
                                temp.append(float(elem) / 1000) # convert mm to m
                        elif (elem_i >= 3 and elem_i < 6) or (elem_i >= 9 and elem_i < 12):
                            if float(elem) > self.threshold_amplitude:
                                print("- Orn " + str(elem) + "deg is larger than tested deg threshold of solo robot of "+str(self.threshold_amplitude) + "deg. Using maximum threshold ("+ 
                                    str(self.threshold_amplitude) +" deg) instead.")
                                temp.append(float(math.radians(self.threshold_amplitude)))
                            elif float(elem) < -self.threshold_amplitude:
                                print("- Orn " + str(elem) + "deg is smaller than tested deg threshold of solo robot of -"+str(self.threshold_amplitude) + "deg. Using minimum threshold (-"+ 
                                    str(self.threshold_amplitude) +" deg) instead.")
                                temp.append(float(-1*(math.radians(self.threshold_amplitude))))
                            else:
                                temp.append(math.radians(float(elem))) # conver deg to rad
                        else:
                            temp.append(int(elem)) # time in seconds
                    '''
                except:
                    temp.append(elem)
            lines.append(temp)
        if header:
            lines = lines[1:] # cut out title line in csv file
        return lines


class GenerateArbitraryTrajectoryClass():

    def __init__(self, 
        output_file_name = TRAJ_PLATFORM_FILE_NAME,
        flush = False,
        interpolate_time = 5,
        trajectory_frequency = 240,
        path_to_output_file = GLOBAL_AUTOGENERATED_DIRECTORY,
        pos_offset = [0,0,0.25],
        orn_offset = [0,0,0],
        start_pos_xyz = [0,0,0],
        start_orn_xyz = [0,0,0],
        end_pos_xyz = [0,0,0],
        end_orn_xyz = [0,0,0],
    ):
        self.interpolate_time = interpolate_time
        self.pos_offset = pos_offset 
        self.orn_offset = orn_offset
        self.flush = flush
        self.trajectory_frequency = trajectory_frequency

        output_file_name = path_to_output_file + output_file_name

        self.end_pos_xyz = [0]*3
        self.end_orn_xyz = [0]*3

        self.end_pos_xyz = end_pos_xyz
        self.end_orn_xyz = end_orn_xyz
        
        self.start_writer(output_file_name, flush)

        arbitrary_trajectory = self.generate_arbitrary_trajectory(start_pos_xyz, start_orn_xyz, end_pos_xyz, end_orn_xyz)

        # print(np.shape(arbitrary_trajectory))
        self.write_output(output_file_name, arbitrary_trajectory)
        # print("Arbitrary trajectory generated and saved!")


    def start_writer(self, output_file_name, flush=True):
        """
            Initializes and starts csv writer. 

            :param output_file_name: Name of output file. 
            :type output_file_name: String.
            :param flush: True if user wants to re-write in file, False is user wants to append in file. 
            :type flush: Bool. 
            :return: None.
            :rtype: None. 
        """
        if flush:
            self.file = open(output_file_name, 'w') 
        else:
            self.file = open(output_file_name, 'a')

        self.data_writer = csv.writer(self.file)

        if flush:
            header = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
            self.data_writer.writerow(header)
        
    
    def write_output(self, output_file_name, data):
        """
            Writes to csv file. 

            :param output_file_name: Name of output file. 
            :type output_file_name: String. 
            :data: Data to write in csv file. 
            :type data: list[float]
            :return: None.
            :rtype: None.
        """
        try:
            self.data_writer.writerows(data)        

        except Exception as e:
            print("Writing data failed! Exiting with:", e)
            exit(-1)
            
        print("+ Successfully writing data into:", output_file_name)
        self.file.close()


    def generate_arbitrary_trajectory(self, start_pos_xyz, start_orn_xyz, end_pos_xyz, end_orn_xyz):
        """
            Generates arbitrary trajectory.

            :param start_pos_xyz: Starting position [x, y, z].
            :type start_pos_xyz: list[float, float, float].
            :param start_orn_xyz: Starting orientation [x, y, z].
            :type start_orn_xyz: list[float, float, float].
            :param end_pos_xyz: Ending position [x, y, z].
            :type end_pos_xyz: list[float, float, float].
            :param end_orn_xyz: Ending orientation [x, y, z].
            :type end_orn_xyz: list[float, float, float].
            :return: Generated arbitrary trajectory. 
            :rtype: list[].
        """

        arbitrary_trajectory = [None]*6
        
        try:
            start_tx, start_ty, start_tz = np.array(start_pos_xyz) + np.array(self.pos_offset)
            start_rx, start_ry, start_rz = np.array(start_orn_xyz) + np.array(self.orn_offset)

            end_tx, end_ty, end_tz = np.array(end_pos_xyz) + np.array(self.pos_offset)
            end_rx, end_ry, end_rz = np.array(end_orn_xyz) + np.array(self.orn_offset)

            arbitrary_trajectory[0] = self.get_interpolated_traj(start_tx, end_tx) # tx
            arbitrary_trajectory[1] = self.get_interpolated_traj(start_ty, end_ty) # ty
            arbitrary_trajectory[2] = self.get_interpolated_traj(start_tz, end_tz) # tz
            arbitrary_trajectory[3] = self.get_interpolated_traj(start_rx, end_rx) # rx
            arbitrary_trajectory[4] = self.get_interpolated_traj(start_ry, end_ry) # ry
            arbitrary_trajectory[5] = self.get_interpolated_traj(start_rz, end_rz) # rz
        
        except Exception as e:
            print("Failed to generate arbitrary trajectory. Returning 0s!")
            print("Excpetion:", e)
            arbitrary_trajectory = [None]*6

        arbitrary_trajectory = np.array(arbitrary_trajectory).T 

        if np.shape(arbitrary_trajectory)[1] != 6:
            print("ERROR. Please try again!")
            exit(-1)

        return arbitrary_trajectory

    
    def get_interpolated_traj(self, start, end):
        """
            Generate interpolated trajectory.

            :param start: Starting point. 
            :type start: Float.
            :param end: Ending point. 
            :type end: Float.
            :return: Returns linear interpolated points.
            :rtype: list[]
        """
        yx = np.arange(0, 2)
        y = [start, end]
        f = interp1d(yx, y, kind='linear', axis=0)
        x = np.arange(0, 1, step=1/(self.interpolate_time*self.trajectory_frequency), dtype=float)
        return f(x)


if __name__ == '__main__':
    GenerateArbitraryTrajectory_CSV_Class()
