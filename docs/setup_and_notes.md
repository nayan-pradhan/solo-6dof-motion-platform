# Setup and Notes

1. [Hardware Setup](#hardware-setup)
2. [Software Setup](#software-setup)
3. [Realtime OS Setup](#realtime-os-setup)
4. [Known Issues and Solutions](#known-issues-and-solutions)
5. [Notes](#notes)

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

---

<a name="realtime-os-setup"></a>

### Realtime OS Setup

#### Install Linux and preempt RT patch.
1. Download and install Ubuntu. 
2. Install required dependencies.
    ```
    sudo apt install -y flex bison libssl-dev libelf-dev libncurses5-dev
    ```
3. Check kernel version. We are using version 5.15.0.
    ```
    uname -r
    ```
4. Download preempt RT patch (.patch.xz file) for your kernel version via this [link](https://wiki.linuxfoundation.org/realtime/preempt_rt_versions). We take the latest 5.15 kernel patch.
5. Download the kernel matching the preempt RT patch you just downloaded (.tar.xz file) via this [link](https://mirrors.edge.kernel.org/pub/linux/kernel/)
6. Extract the downloaded files.
    ```
    cd ~/Downloads/
    xz -d linux-YOURVERSION.tar.xz
    xz -d patch-YOURVERSION.patch.xz
    tar xf linux-YOURVERSION.tar
    ```
7. Change directory to kernel directory and apply patch. 
    ```
    cd linux-YOURVERSION/
    patch -p1 < ../patch-YOURVERSION.patch
    ```
8. Configure kernel.
    ```
    cp -v /boot/config-$(uname -r) .config
    make oldconfig
    ```
    For Preemption model choose: Fully Preemptible Kernel (Real-Time). For the rest use default settings by pressing enter.
    ```
    scripts/config --disable SYSTEM_TRUSTED_KEYS
    make x86_64_defconfig
    ```
9. Compile and install kernel.
    ```
    sudo make deb-pkg
    sudo make modules_install
    sudo make install
    ```
10. Update grub. 
    ```
    sudo update-initramfs -c -k YOURVERSION
    sudo update-grub
    ```
11. Reboot your system. 

#### Update Nvidia Driver
First try the easier way to install the driver, but it is not possible on some systems.
1. Download latest Nvidia driver from the [Nvidia website](https://www.nvidia.com/download/index.aspx).
2. Go to your Downloads folder, make file executable, and run the file. 
    ```
    cd ~/Downloads/
    chmod +x ./NVIDIAFILE.run
    sudo ./NVIDIAFILE.run
    ```
If this is not working and you get the error 'x server is running' or the message that Nvidia drivers will not work on realtime systems, try the following steps:
1.  Press Ctrl+Alt+F1 to open a Terminal and login with your credentials.
2.  Stop X-Server. 
    ```
    sudo systemctl stop lightdm
    ```
3. Install the driver. 
    ```
    cd ~/Downloads/
    sudo IGNORE_PREEMPT_RT_PRESENCE=1 bash ./NVIDIAFILE.run
    ```
4. Start X-Server.
    ```
    sudo systemctl start lightdm
    ```
5. Reboot your system. 

#### Configure your System
1. Create 'realtime' group and add users.
    ```
    sudo groupadd realtime
    sudo usermod -aG realtime <username>
    ```
2. Set rtprio and memlock limits.
    ```
    sudo tee /etc/security/limits.d/99-realtime.conf > /dev/null <<EOL
    @realtime - rtprio 99
    @realtime - memlock unlimited
    EOL
    ```
3. Reboot your system. 

--- 

<a name="known-issues-and-solutions"></a>

### Known Issues and Solutions

- #### Beeping sound from motor drivers
    **_Issue:_** Robot motor drivers beep when starting up bash script. This issue usually occurs when testing with the robot is done for a very long time or if the power supply has been turned ON for a very long time (3-4 hours). The masterboard also gets very warm.  
    **_Solution:_** Turn the power supply OFF for a few minutes (around 10-15 minutes) and restart the power supply when the masterboard is cool to touch.

- #### Robot timeout/motor drivers red blinking lights  
    **_Issue:_** Robot times out and the motor drivers start blinking red lights. This issue usually occurs when the motors do not receive a new command for more than 1 milli-second. We experienced this issue when we were trying to append new data into a 2-dimensional array and when we tried printing multiple lines in the main loop.  
    **_Solution:_** Avoid running tasks that take a lot of time (eg. appending into 2-dimensional array, printing multiple lines in each iteration, etc) in the main loop.

- #### Wrong motor index found
    **_Issue:_** Sometimes the correct motor indices are not found in the calibration step. If the correct motor indices are not found, the motors will have an offset of . This issue happens if the robot is not setup properly for Calibration Phase 2.  
    **_Solution:_** If you see that the correct motor is not found (motor has an offset of ), immediately stop the program and redo Calibration Phase 2. Make sure the robot motor joints are in the correct 'Calibration Position' as shown in Robot Positions/Configurations.

- #### Robot does unexpected sudden movement at startup
    **_Issue:_** Stop the program immediately if the robot does unexpected sudden movements at startup. This is usually a result of not following the calibration steps properly.  
    **_Solution:_** Re-do the calibration steps carefully. Make sure proper motor indices are saved in the csv files.

---

<a name="notes"></a>

### Notes   
- To give edit access of output history files to user, do `sudo chown user:user \*` in `data_files/*/history/` directory.
