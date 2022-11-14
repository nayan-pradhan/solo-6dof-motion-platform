'''
    Master Pybullet Program
'''

from platform_trajectory_generation.generate_arbitrary_trajectory import *
from platform_trajectory_generation.generate_sine_trajectory import *
from platform_trajectory_generation.generate_step_trajectory import *
from platform_trajectory_generation.generate_circular_trajectory import *
from inverse_kinematics.pybullet_IK import *
from control.solo_ctrl import *
from control.pybullet_ctrl import *
from post_processing.data_processing import *
from post_processing.data_preview import *
import config


class PybulletProgram():

    def __init__(self, 
        sequence='', 
        ik='',
        ctrl='',
        skip_sequence=False,
        skip_ik=False,
    ):
        if not skip_sequence:
            ''' Pybullet Trajectory Generation '''

            if sequence == 'Arbitrary Sequence':
                CURRENT_INPUT_FILE = INPUT_ARBITRARY_FILE_NAME
                print("Sequence for arbitrary motion.")
                GenerateArbitraryTrajectory_CSV_Class(frequency=240, input_file_name=CURRENT_INPUT_FILE)

            elif sequence == 'Sine Sequence':
                CURRENT_INPUT_FILE = INPUT_SINE_FILE_NAME
                print("Sequence for sine wave motion.")
                GenerateSineTrajectoryClass(frequency=240, input_file_name=CURRENT_INPUT_FILE)
            
            elif sequence == 'Circular Trajectory':
                CURRENT_INPUT_FILE = INPUT_CIRCULAR_FILE_NAME
                print("Sequence for circular trajectory.")
                GenerateCircularTrajectoryClass(frequency=240, input_file_name=CURRENT_INPUT_FILE)

            elif sequence == 'Step Func':
                CURRENT_INPUT_FILE = INPUT_STEP_FILE_NAME
                print("Sequence for step function motion.")
                GenerateStepTrajectory_CSV_Class(frequency=240, input_file_name=CURRENT_INPUT_FILE)

            else:
                print("Sequence type not defined in class instance. Exiting!")
                exit(-1)

        if not skip_ik:
            ''' Inverse Kinematics '''

            if ik == 'PyBullet Inverse Kinematics':
                print("Generating joint angles from Pybullet Inverse Kinematics Class.")
                PybulletIKClass(robot_environment="pybullet")
            
            else:
                print("Inverse kinematics library not defined in class instance. Exiting!")
                exit(-1)
    
        ''' Control '''

        if ctrl == 'PyBullet Simulation Control':
            print("Using PyBullet simulation control.")
            PybulletControlClass()
            print('---')
        else:
            print("Use solo_program.py to use solo control. Exiting pybullet program.")
            exit(-1)

                
        ''' Post Processing '''
        DataProcessClass(GLOBAL_OUTPUT_DIRECTORY+PYBULLET_DATA_OUTPUT_FILE_NAME, 'pybullet', [0,0,0])
        DataPreviewClass(
            name_of_data_csv_file = GLOBAL_OUTPUT_DIRECTORY+PYBULLET_DATA_OUTPUT_FILE_NAME ,
            name_of_calculated_csv_file = GLOBAL_OUTPUT_DIRECTORY+PYBULLET_CALCULATED_FILE_NAME,
            robot_env = 'pybullet',
            plot_fr_joint_angles = True,
            plot_calculated_pos_data = True,
            plot_calculated_vel_data = True,
            plot_calculated_acc_data = True,
            plot_imu_data = False,
        )

'''
if __name__ == '__main__':
    solo_arbitrary_sequence = PybulletProgram(sequence='arbitrary', ik='pybullet', ctrl='simulation', skip_sequence=True)
    # solo_sine_sequence = PybulletProgram(sequence='sine', ik='pybullet')
'''