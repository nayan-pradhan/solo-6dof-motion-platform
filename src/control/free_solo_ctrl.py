"""
    Python script for free solo. 
"""
import math
import os
from time import process_time
import csv
import numpy as np
from config import *
import time

try:
    import libmaster_board_sdk_pywrap as mbs
except ImportError:
    print("- Cannot find libmaster_board_sdk_pywrap. PyBullet Simulation will work as normal but SOLO control will not work.")

class FreeSoloClass():

    def __init__(self,
        name_interface = 'enp9s0f1',
        n_slaves = 6,
        run_time_sec = None, # if None == run till ctrl+c is pressed
    ):
        self.name_interface = name_interface
        self.n_slaves = n_slaves
        self.run_time_sec = run_time_sec
        self.dt = 1/1000
        self.adc_trigger_threshold = 0.50
        self.adc_triggered_ctr = 0

        self.init_masterboard_params()
        self.init_motor_mapping()

        self.init_pos_motors = [None]*self.n_slaves*2
        self.motor_pos = [None]*self.n_slaves*2
        self.motor_vel = [None]*self.n_slaves*2

        self.global_ctr = 0

        self.calibration_offsets = self.load_offsets()

        self.main_loop()

        self.robot_if.Stop()  # Shut down the interface between the computer and the master board

        print('---')

        if self.robot_if.IsTimeout():
            print("Masterboard timeout detected.")
            print("Either the masterboard has been shut down or there has been a connection issue with the cable/wifi.")

    
    def main_loop(self):
        while(1):
            if ((time.time() - self.last) > self.dt):
                self.last = time.time()

                self.robot_if.ParseSensorData()

                if (self.state == 0):  #  If the system is not ready
                    self.state = 1
                    # for all motors on a connected slave
                    for i in self.motors_spi_connected_indexes:  # Check if all motors are enabled and ready
                        if not (self.robot_if.GetMotor(i).IsEnabled() and self.robot_if.GetMotor(i).IsReady()):
                            self.robot_if.SendInit()
                            self.state = 0
                        self.init_pos_motors[i] = self.robot_if.GetMotor(i).GetPosition()
                
                else:
                    self.read_adc_trigger()
                        
                    for i in self.motors_spi_connected_indexes:
                        self.global_i = i
                        if i % 2 == 0 and self.robot_if.GetDriver(i // 2).GetErrorCode() == 0xf:
                            #print("Transaction with SPI{} failed".format(i // 2))
                            continue #user should decide what to do in that case, here we ignore that motor
                                                    
                        if self.robot_if.GetMotor(i).IsEnabled():

                            if self.run_time_sec is None:
                                self.free_controller()
                            else:
                                if (self.global_ctr <= self.run_time_sec*1000):
                                    self.free_controller()
                                else:
                                    self.robot_if.Stop()
                                    exit()

            self.robot_if.SendCommand()

    
    def read_adc_trigger(self):
        if (self.robot_if.GetDriver(3).adc[0]) > self.adc_trigger_threshold:
            self.save_offset(values_at_trigger=self.motor_pos)
            self.adc_triggered_ctr+=1
            print('---------------------------------------------')
            print("ADC Triggered Counter:", self.adc_trigger_threshold)
            print("Motor Pos:",self.motor_pos)
            print('---------------------------------------------')
            # returns in case other parts of program wants to read it
            return True, self.adc_triggered_ctr, self.motor_pos
        else:
            return False, self.adc_triggered_ctr, []

    
    def save_offset(self, f_name=GLOBAL_CALIBRATION_FILES_DIRECTORY+LANDING_POS_FILE, values_at_trigger=[]):
        """
            Saves calibration offsets into given file.

            :param f_name: Name of file.
            :type f_name: str.
            :return: None.
            :rtype: None.
        """
        f = open(f_name, 'w')
        writer = csv.writer(f)
        writer.writerow(values_at_trigger)
        f.close() 
        print("Landing Joint Angles Saved!")

    
    def init_masterboard_params(self):
        """
            Initialize masterboard parameters.

            :return: None.
            :rtype: None.
        """
        self.state = 0 # State of the system (ready (1) or not (0))
        os.nice(-20)  #  Set the process to highest priority (from -20 highest to +20 lowest)
        self.init_motor_drivers()

    
    def init_motor_drivers(self):
        """
            Initialize motor drivers.

            :return: None.
            :rtype: None.
        """
        self.init_pos_motors = [0.0 for i in range(self.n_slaves * 2)] # List that will store the initial position of motors
        
        self.motors_spi_connected_indexes = [] # indexes of the motors on each connected slaves
        self.motors_spi_connected_indexes_array = np.zeros(self.n_slaves*2) # 1 if motor at index is connected

        self.robot_if = mbs.MasterBoardInterface(self.name_interface)
        self.robot_if.Init()  # Initialization of the interface between the computer and the master board

        for i in range(self.n_slaves):  #  We enable each controler driver and its two associated motors
            self.robot_if.GetDriver(i).motor1.SetCurrentReference(0)
            self.robot_if.GetDriver(i).motor2.SetCurrentReference(0)
            self.robot_if.GetDriver(i).motor1.Enable()
            self.robot_if.GetDriver(i).motor2.Enable()
            self.robot_if.GetDriver(i).EnablePositionRolloverError()
            self.robot_if.GetDriver(i).SetTimeout(5)
            self.robot_if.GetDriver(i).Enable()

        self.last = time.time()

        while (not self.robot_if.IsTimeout() and not self.robot_if.IsAckMsgReceived()):
            if ((time.time() - self.last) > self.dt):
                self.last = time.time()
                self.robot_if.SendInit()

        if self.robot_if.IsTimeout():
            print("Timeout while waiting for ack.")
        else:
            # fill the connected motors indexes array
            for i in range(self.n_slaves):
                if self.robot_if.GetDriver(i).IsConnected():
                    # if slave i is connected then motors 2i and 2i+1 are potentially connected
                    self.motors_spi_connected_indexes.append(2 * i)
                    self.motors_spi_connected_indexes.append(2 * i + 1)

        for i in self.motors_spi_connected_indexes:
            self.motors_spi_connected_indexes_array[i] = 1

    
    def init_motor_mapping(self):
        """
            Initialize motor  mapping.

            :return: None.
            :rtype: None.
        """
        self.motor_mapping = {
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


    def load_offsets(self, f_name=GLOBAL_CALIBRATION_FILES_DIRECTORY+CALIBRATION_PHASE_2_FILE):
        """
            Loads calibration offsets from given file.

            :param f_name: Name of file.
            :type f_name: str.
            :return: Returns calibraiton offset array.
            :rtype: list[float].
        """
        row = []
        try:
            f = open(f_name, 'r')
            reader = csv.reader(f)
            for line in reader:
                row.append(line)
            row = list([float(co) for co in row[-1]])
            print("CSV:", f_name, "loaded successfully!")
            print('---')
            print("Loaded values:", row)
        except:
            print("CSV:", f_name, "invalid. Using 0 calibration offset!")
            row = [0.0]*12
        print('---')
        return row 


    def free_controller(self):
        """
            Controller with no PD parameters. Prints joint angles.

            :return: None.
            :rtype: None.
        """

        if self.robot_if.GetMotor(self.global_i).IsEnabled():
            if self.global_i == 0:
                print("Motor No.        Motor Name.         Joint Angle")
                for i in range(self.n_slaves*2):
                    self.motor_pos[i] = self.robot_if.GetMotor(i).GetPosition() + self.calibration_offsets[i] # adding calibration ph2 offsets here
                    self.motor_vel[i] = self.robot_if.GetMotor(i).GetVelocity()
                    print("  "+str(i)+"              "+str(self.motor_mapping[i])+"             "+str(self.motor_pos[i]))
                print("---")
                self.global_ctr+=1

            for i in self.motors_spi_connected_indexes:
                ### DO NOT CHANGE 
                self.robot_if.GetMotor(i).SetCurrentReference(0.) # sets currents to 0 so nothing happens   