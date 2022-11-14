"""
    python script that asks user for input
"""

from pybullet_program import *
from solo_program import *

class StartProgramClass():

    def __init__(self,
        sequence_type = None,
        inverse_kinematics_tool = None,
        control_platform = None, 
        calibration_phase = None,  
    ):
        print("---")
        if control_platform == "PyBullet Simulation Control":
            """
                If Start Program Class instance is initialized with in-line flags for Pybullet Simulation Control.
            """
            self.input_arr = [sequence_type, inverse_kinematics_tool, control_platform]
            print("Program Running:\n+", self.input_arr[0],"\n+", self.input_arr[1],"\n+", self.input_arr[2])

        elif control_platform == "Solo Robot Control":
            """
                If Start Program Class instance is initialized with in-line flags for Solo Robot Control.
            """
            self.input_arr = [sequence_type, inverse_kinematics_tool, control_platform, calibration_phase]
            print("Program Running:\n+", self.input_arr[0],"\n+", self.input_arr[1],"\n+", self.input_arr[2],"\n+", self.input_arr[3])

        else:
            self.input_arr = [None, None, None, None]

        if all(list([i is not None for i in self.input_arr])):
            """
                Run in direct mode if input_array is filled.
            """
            print("---")
            self.run_direct_mode(sequence_type, inverse_kinematics_tool, control_platform, calibration_phase)

        else:
            """
                If Start Program Class instance is initialized without in-line flags.
            """
            self.welcome_msg()
            self.init_input_params()
            self.get_user_input()


    def welcome_msg(self):
        """
            Prints welcome message.

            :return: None.
            :rtype: None.
        """
        print("\n================================================")
        print("|| SOLO 6 DOF MOTION CONTROL PLATFORM PROGRAM ||")
        print("================================================\n")


    def init_input_params(self):
        """
            Initializes input parametes that gets filled from user's input.

            :return: None.
            :rtype: None.
        """
        self.output_prompt_counter = 0
        self.output_prompts = [ # add output prompts here
            "Select sequence type:",
            "Select Inverse Kinematics tool:",
            "Select Control Platform",
            "Select Calibration Phase"
        ] 
        
        self.selected_sequence_type = None 
        self.selected_ik_type = None 
        self.select_control_type = None 
        self.selected_calibration_phase = None 
        self.skip_trajectory_generation = False 

        self.sequence_types_array = [ # add sequence types here
            "Use Pre-existing Sequence File", 
            "Arbitrary Sequence", 
            "Sine Sequence", 
            "Circular Trajectory",
            "Step Func"
        ]
        self.ik_types_array = [ # add inverse kinematics tools here
            "Use Pre-existing IK Output File", 
            "PyBullet Inverse Kinematics"
        ]

        self.control_types_array = [ # add control environment here
            "-",
            "PyBullet Simulation Control", 
            "Solo Robot Control"
        ]


    def get_user_input(self):
        """
            Gets user input and initializes program class.

            :return: None.
            :rtype: None.
        """
        self.selected_sequence_type = self.parse_user_input(self.selected_sequence_type, self.sequence_types_array)
        self.selected_ik_type = self.parse_user_input(self.selected_ik_type, self.ik_types_array)
        self.select_control_type = self.parse_user_input(self.select_control_type, self.control_types_array)
        
        if self.select_control_type == "PyBullet Simulation Control":
            print("Program Running:\n+", self.selected_sequence_type,"\n+", self.selected_ik_type,"\n+", self.select_control_type)
            print("\n---\n")

            PybulletProgram(
                sequence = self.selected_sequence_type,
                ik = self.selected_ik_type,
                ctrl = self.select_control_type,
                skip_sequence = True if self.selected_sequence_type == self.sequence_types_array[0] else False,
                skip_ik = True if self.selected_ik_type == self.ik_types_array[0] else False
            )

        elif self.select_control_type == "Solo Robot Control":
            self.calibration_phases_array = ["Already Calibrated","Phase 0 Calibration", "Phase 1 Calibration", "Phase 2 Calibration"]
            self.selected_calibration_phase = self.parse_user_input(self.selected_calibration_phase, self.calibration_phases_array)
            print("Program Running:\n+", self.selected_sequence_type,"\n+", self.selected_ik_type,"\n+", self.select_control_type,"\n+", self.selected_calibration_phase)
            print("\n---\n")

            SoloProgram(
                sequence = self.selected_sequence_type,
                ik = self.selected_ik_type,
                ctrl = self.select_control_type,
                skip_sequence = True if self.selected_sequence_type == self.sequence_types_array[0] else False,
                skip_ik = True if self.selected_ik_type == self.ik_types_array[0] else False,
                solo_calibration_phase_0 = True if self.selected_calibration_phase == self.calibration_phases_array[1] else False,
                solo_calibration_phase_1 = True if self.selected_calibration_phase == self.calibration_phases_array[2] else False,
                solo_calibration_phase_2 = True if self.selected_calibration_phase == self.calibration_phases_array[3] else False,
            )

        print("\n---\n")

    def parse_user_input(self, output_val, options):
        """
            Parses user input. The user is prompted with options to run the program. Options are selected by inputing a number (0, 1, 2, ...) depending on the number of options. 
            This method displays the options for the user, takes the input from the user, and outputs the selected value from the options array.

            :param output_val: Initially None when method is called.
            :type output_val: None.
            :param options: Array of options to display to the user. 
            :type options: list[string].
            :return: User selected value from options array.
            :rtype: None or selected user value.
        """
        selected_index = None
        while(output_val is None):
            print('> '+self.output_prompts[self.output_prompt_counter])
            print("[-1] Exit Program")
            for si, s in enumerate(options):
                print("["+str(si)+"] "+str(s))
                if si == 0: print(" - ")

            try:
                selected_index = int(input("--> "))

                if selected_index > len(options) or selected_index < -1:
                    print("[x] Invalid input, enter valid integer.")
                    output_val = None 
                elif selected_index == -1:
                    print("Exiting Program.")
                    exit(-1)
                    
                else:
                    output_val = options[selected_index]
                    if output_val == '-':
                        print("[x] Invalid input, enter valid integer.")
                        output_val = None 
                    else:
                        print("+ Selected:", output_val)
                        self.output_prompt_counter += 1

            except Exception as e:
                print("[x] Invalid input, enter valid integer. Exception:", e)
                output_val = None 

            print("\n---\n")
        return output_val


    def run_direct_mode(self, sequence_type, inverse_kinematics_tool, control_platform, calibration_phase):
        """
            Initializes class instance for pybullet or solo program from in-line flags.

            :param sequence_type: Selected sequence passed through in-line flags. 
            :type sequence_type: String.
            :param inverse_kinematics_tool: Selected inverse kinematics tool passed through in-line flags.
            :type inverse_kinematics_tool: String.
            :param control_platform: Selected control environment passed through in-line flags.
            :type control_platform: String.
            :param calibration_phase: Selected calibration phase passed through in-line flags if using solo env.
            :type calibration_phase: None or String.
            :return: None.
            :rtype: None.
        """
        self.sequence_types_array = ["Use Pre-existing Sequence File", "Arbitrary Sequence", "Sine Sequence", "Circular Trajectory", "Step Func"]
        self.ik_types_array = ["Use Pre-existing IK Output File", "PyBullet Inverse Kinematics"]
        self.control_types_array = ["-","PyBullet Simulation Control", "Solo Robot Control"]
        self.calibration_phases_array = ["Already Calibrated","Phase 0 Calibration", "Phase 1 Calibration", "Phase 2 Calibration"]
        
        if control_platform == "PyBullet Simulation Control":
            PybulletProgram(
                sequence = sequence_type,
                ik = inverse_kinematics_tool,
                ctrl = control_platform, 
                skip_sequence = True if sequence_type == self.sequence_types_array[0] else False, 
                skip_ik =  True if inverse_kinematics_tool == self.ik_types_array[0] else False, 
            )
        elif control_platform == "Solo Robot Control":
            SoloProgram(
               sequence = sequence_type,
                ik = inverse_kinematics_tool,
                ctrl = control_platform, 
                skip_sequence = True if sequence_type == self.sequence_types_array[0] else False, 
                skip_ik =  True if inverse_kinematics_tool == self.ik_types_array[0] else False, 
                solo_calibration_phase_0 = True if calibration_phase == self.calibration_phases_array[1] else False,
                solo_calibration_phase_1 = True if calibration_phase == self.calibration_phases_array[2] else False,
                solo_calibration_phase_2 = True if calibration_phase == self.calibration_phases_array[3] else False,
            )


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='start program.')

    parser.add_argument('-s0',
                        '--use-pre-existing-sequence',
                        action='store_true',
                        help='Use pre-existing sequence')

    parser.add_argument('-sa',
                        '--use-arbitrary-sequence',
                        action='store_true',
                        help='Use arbitrary sequence')

    parser.add_argument('-ss',
                        '--use-sine-sequence',
                        action='store_true',
                        help='Use sine sequence')
    
    parser.add_argument('-sc',
                        '--use-circular-trajectory',
                        action='store_true',
                        help='Use circular trajectory')

    parser.add_argument('-st',
                        '--use-step-func',
                        action='store_true',
                        help='Use step func')

    parser.add_argument('-i0',
                        '--use-pre-existing-ik',
                        action='store_true',
                        help='Use pre-existing inverse kinematics')

    parser.add_argument('-ip',
                        '--use-pybullet-ik',
                        action='store_true',
                        help='Use pybullet inverse kinematics')

    parser.add_argument('-cp',
                        '--use-pybullet-control_env',
                        action='store_true',
                        help='Use pybullet control environment')

    parser.add_argument('-cs',
                        '--use-solo-control-env',
                        action='store_true',
                        help='Use solo control environment')

    parser.add_argument('-px',
                        '--already-calibrated',
                        action='store_true',
                        help='Use calibration phase 0')

    parser.add_argument('-p0',
                        '--use-phase0-calibration',
                        action='store_true',
                        help='Use calibration phase 0')
    
    parser.add_argument('-p1',
                        '--use-phase1-calibration',
                        action='store_true',
                        help='Use calibration phase 1')
    
    parser.add_argument('-p2',
                        '--use-phase2-calibration',
                        action='store_true',
                        help='Use calibration phase 2')

    sequence_types_options = ["Use Pre-existing Sequence File", "Arbitrary Sequence", "Sine Sequence", "Circular Trajectory", "Step Func"]
    ik_types_array = ["Use Pre-existing IK Output File", "PyBullet Inverse Kinematics"]
    control_types_array = ["PyBullet Simulation Control", "Solo Robot Control"]
    calibration_phases_array = ["Already Calibrated","Phase 0 Calibration", "Phase 1 Calibration", "Phase 2 Calibration"]

    sequence_type_mask = [parser.parse_args().use_pre_existing_sequence, parser.parse_args().use_arbitrary_sequence, parser.parse_args().use_sine_sequence, parser.parse_args().use_circular_trajectory, parser.parse_args().use_step_func]
    ik_type_mask = [parser.parse_args().use_pre_existing_ik, parser.parse_args().use_pybullet_ik]
    control_types_mask = [parser.parse_args().use_pybullet_control_env ,parser.parse_args().use_solo_control_env]
    calibration_phase_mask = [parser.parse_args().already_calibrated, parser.parse_args().use_phase0_calibration, parser.parse_args().use_phase1_calibration, parser.parse_args().use_phase2_calibration]

    if not any(sequence_type_mask) or not any(ik_type_mask) or not any(ik_type_mask):
        StartProgramClass()

    elif control_types_mask[0]:
        StartProgramClass(
            sequence_type = sequence_types_options[[i for i, x in enumerate(sequence_type_mask) if x == True][0]],
            inverse_kinematics_tool = ik_types_array[[i for i, x in enumerate(ik_type_mask) if x == True][0]],
            control_platform = control_types_array[[i for i, x in enumerate(control_types_mask) if x == True][0]],
            calibration_phase = None
        )

    elif control_types_mask[1]:
        StartProgramClass(
            sequence_type = sequence_types_options[[i for i, x in enumerate(sequence_type_mask) if x == True][0]],
            inverse_kinematics_tool = ik_types_array[[i for i, x in enumerate(ik_type_mask) if x == True][0]],
            control_platform = control_types_array[[i for i, x in enumerate(control_types_mask) if x == True][0]],
            calibration_phase = calibration_phases_array[[i for i, x in enumerate(calibration_phase_mask) if x == True][0]]
        )
