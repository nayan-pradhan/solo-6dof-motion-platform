'''
    Master Solo Program
'''

from platform_trajectory_generation.generate_arbitrary_trajectory import *
from platform_trajectory_generation.generate_sine_trajectory import *
from platform_trajectory_generation.generate_step_trajectory import *
from platform_trajectory_generation.generate_circular_trajectory import *
from post_processing.data_processing import *
from post_processing.data_preview import *
from inverse_kinematics.pybullet_IK import *
from control.solo_ctrl import *


class SoloProgram():

    def __init__(self, 
        sequence='', 
        ik='',
        ctrl='',
        skip_sequence=False,
        skip_ik=False,
        solo_calibration_phase_0=True,
        solo_calibration_phase_1=False,
        solo_calibration_phase_2=False,
    ):
        if not skip_sequence:
            ''' Pybullet Trajectory Generation '''

            if sequence == 'Arbitrary Sequence':
                CURRENT_INPUT_FILE = INPUT_ARBITRARY_FILE_NAME
                print("Sequence for arbitrary motion.")
                GenerateArbitraryTrajectory_CSV_Class(frequency=1000, input_file_name=CURRENT_INPUT_FILE)

            elif sequence == 'Sine Sequence':
                CURRENT_INPUT_FILE = INPUT_SINE_FILE_NAME
                print("Sequence for sine wave motion.")
                GenerateSineTrajectoryClass(frequency=1000, input_file_name=CURRENT_INPUT_FILE)

            elif sequence == 'Circular Trajectory':
                CURRENT_INPUT_FILE = INPUT_CIRCULAR_FILE_NAME
                print("Sequence for circular trajectory.")
                GenerateCircularTrajectoryClass(frequency=1000, input_file_name=CURRENT_INPUT_FILE)
            
            elif sequence == 'Step Func':
                CURRENT_INPUT_FILE = INPUT_STEP_FILE_NAME
                print("Sequence for step function motion.")
                GenerateStepTrajectory_CSV_Class(frequency=1000, input_file_name=CURRENT_INPUT_FILE)

            else:
                print("Sequence type not defined in class instance. Exiting!")
                exit(-1)

        if not skip_ik:
            ''' Inverse Kinematics '''

            if ik == 'PyBullet Inverse Kinematics':
                print("Generating joint angles from Pybullet Inverse Kinematics Class.")
                PybulletIKClass(robot_environment="solo")
            
            else:
                print("Inverse kinematics library not defined in class instance. Exiting!")
                exit(-1)
    
        ''' Control '''

        if ctrl == 'Solo Robot Control':
            print("Using solo control.")
            print('---')
            SoloControlClass(
                phase_0_calibration = solo_calibration_phase_0,
                phase_1_calibration = solo_calibration_phase_1,
                phase_2_calibration = solo_calibration_phase_2
            )
        else:
            print("Use pybullet_program.py to use pybullet control. Exiting solo program.")
            exit(-1)

        
        ''' Post Processing '''
        DataProcessClass(GLOBAL_OUTPUT_DIRECTORY+SOLO_DATA_OUTPUT_FILE_NAME, 'solo', [0,0,0])
        DataPreviewClass(
            name_of_data_csv_file = GLOBAL_OUTPUT_DIRECTORY+SOLO_DATA_OUTPUT_FILE_NAME ,
            name_of_calculated_csv_file = GLOBAL_OUTPUT_DIRECTORY+SOLO_CALCULATED_FILE_NAME,
            name_of_phantom_csv_file = None , 
            robot_env = 'solo',
            plot_fr_joint_angles = True,
            plot_calculated_pos_data = True,
            plot_calculated_vel_data = True,
            plot_calculated_acc_data = True,
            plot_imu_data = True,
            plot_phantom_data = False,
            plot_circular_traj_platform=True
        )

'''
if __name__ == '__main__':
    solo_arbitrary_sequence = SoloProgram(sequence='arbitrary', ik='pybullet', ctrl='solo', skip_sequence=True)
    # solo_sine_sequence = SoloProgram(sequence='sine', ik='pybullet')
'''