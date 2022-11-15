# Software Framework

Our open-source software package uses the master-board from the SOLO robot [Open Dynamic Robot Initiative GitHub page](https://github.com/open-dynamic-robot-initiative) to send torque commands to the motors and read sensor data. The [master-board](https://github.com/open-dynamic-robot-initiative/master-board) centralises all the sensor and actuator data and provides wired and wireless connection to a real-time computer. 

The primary language used in our software package is Python3. The software framework is built to be modular such that any user may update, add, or remove parts of the module. As long as the modules receive an input csv file of the proper format and output the respective csv files of proper format, the software framework will work as designed. 

Our software framework consists of 4 main modules:
1. Platform Trajectory Generation
2. Inverse Kinematics Tool 
3. Control Environment
4. Post Processing

A flowchart showing a high-level overiew of the complete software framework is shown below:
<p align="center">
  <img src="../images/solo-6dof-motion-platform_framework.png" width="250"/>
</p>

### Notes   
- Smooth landing position is hard-coded (joint angles are pre-defined).  
- To give access of output history files to user, do 'sudo chown user:user \*' in data_files/\*/history/ directory.  