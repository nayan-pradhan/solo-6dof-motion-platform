#! /bin/bash

# Help
Help()
{
   # Display Help
   echo 
   echo "###################################### Help ######################################"
   echo
   echo "Syntax: bash start_program.sh [ | -h | -s 0/a/s/t | -i 0/p | -c p/s | -p x/0/1/2]"
   echo "options:"
   echo 
   echo "       Run program using command line interface."
   echo
   echo "-h     Print this Help."
   echo 
   echo "-c  f  Solo Free Control."
   echo 
   echo "-s     Define sequence type."
   echo "       0   Use pre-existing sequence"
   echo "       a   Use arbitrary sequence"
   echo "       s   Use sine sequence"
   echo "       c   Use circular sequence"
   echo "       t   Use step sequence"
   echo 
   echo "-i     Define inverse kinematics tool."
   echo "       0   Use pre-existing inverse kinematics"
   echo "       p   Use pybullet inverse kinematics"
   echo 
   echo "-c     Define control environment."
   echo "       p   Use pybullet environment"
   echo "       s   Use solo robot environment"
   echo 
   echo "-p     Define calibration phase."
   echo "       x   Use no calibration"
   echo "       0   Calibration Phase 0"
   echo "       1   Calibration Phase 1"
   echo "       2   Calibration Phase 2"
   echo 
   echo "##################################################################################"
   echo 
}

# CLI
CLI() 
{
    echo "------------------------------------------------"
    echo "-         Using Command Line Interface         -"
    echo "------------------------------------------------"
    echo
    sudo PYTHONPATH=../resources/master-board/sdk/master_board_sdk/build python3 start_program.py
}

# Set variables
sequence_type=""
ik_tool=""
control_env=""
calibration_phase=""

# Getting user input flags
while getopts hs:i:c:p: flag
do 
    case "${flag}" in
        h)  # Display help 
            Help 
            exit;;
        
        s) # Enter sequence type
            sequence_type=$OPTARG;;
                
        i) # Enter inverse kinematics tool 
            ik_tool=$OPTARG;;

        c) # Enter control environment
            control_env=$OPTARG;;

        p) # Enter calibration phase
            calibration_phase=$OPTARG;;
        
        \?) # Invalid option 
            echo "Error: Invalid option"
            exit;;
    esac
done

if [ "$control_env" = "f" ] ; then 
    sudo PYTHONPATH=../resources/master-board/sdk/master_board_sdk/build python3 start_program.py -c$control_env
elif [ "$control_env" = "solo" ] || [ "$control_env" = "s" ] ; then
    sudo PYTHONPATH=../resources/master-board/sdk/master_board_sdk/build python3 start_program.py -s$sequence_type -i$ik_tool -c$control_env -p$calibration_phase
elif [ "$control_env" = "pybullet" ] || [ "$control_env" = "p" ] ; then 
    sudo PYTHONPATH=../resources/master-board/sdk/master_board_sdk/build python3 start_program.py -s$sequence_type -i$ik_tool -c$control_env
else
    CLI
fi