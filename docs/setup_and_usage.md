# Setup and Usage

1. [Hardware Setup](#hardware-setup)
2. [Software Setup](#software-setup)


---

<a name="hardware-setup"></a>

### Hardware Setup
1. Refer to the [Open Robot Quadruped Robot 12 DoF](https://github.com/open-dynamic-robot-initiative/open_robot_actuator_hardware/blob/master/mechanics/quadruped_robot_12dof_v1/README.md#quadruped-robot-12dof-v1) for setting up the SOLO 12 Robot.
2. Refer to the [Hardware Framework](docs/hardware_framework.md) page for instructions on setting up the motion platform environment. 

---

<a name="software-setup"></a>

### Software Setup
1. Get and setup the [Open Dynamic Robot Initiative Masterboard SDK](https://github.com/open-dynamic-robot-initiative/master-board/blob/master/sdk/master_board_sdk/README.md) interface.
2. Clone the `solo-6dof-motion-platform` repository. 
    ```
    git clone https://github.com/nayan-pradhan/solo-6dof-motion-platform
    ```
3. Clone the Open Dynamic Robot Initiative Masterboard Git repository inside `solo-6dof-motion-platform/resources/`. 
    ```
    cd solo-6dof-motion-platform/resources/
    git clone --recursive https://github.com/open-dynamic-robot-initiative/master-board.git
    ```
4. Setup, build, and install necessary modules for the master-board package.
    ```
    cd master-board/sdk/master_board_sdk
    mkdir build
    cd build
    cmake -DBUILD_PYTHON_INTERFACE=ON -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE=$(which python3) ..
    make
    sudo PYTHONPATH=./master-board/sdk/master_board_sdk/build pip3 install pybullet pynput
    ```

### Robot Positions

### Notes   
- Smooth landing position is hard-coded (joint angles are pre-defined).  
- To give access of output history files to user, do 'sudo chown user:user \*' in data_files/\*/history/ directory.  
