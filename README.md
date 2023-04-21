# SOLO 6 DoF Motion Platform

[![motion platform](http://img.youtube.com/vi/BtfoymwgIUY/0.jpg)](http://www.youtube.com/watch?v=BtfoymwgIUY "6-DoF- Motion Platform")

## <u>Introduction</u>
We present an open-source 6 DoF motion platform capable of producing controlled highly dynamic motion in 3D space. The idea is to flip a quadruped robot, attach a 3D printed platform (holding the payload) to the feet, and using inverse kinematics to move the attached platform in the closed-loop kinematic chain. 12 motors works together to produce high acceleration.

Our design is based on the [open-dynamic-robot-initiative](https://github.com/open-dynamic-robot-initiative).

The platform design, pybullet simulation and robot control framework are fully open source.

1. [Hardware Framework](docs/hardware_framework.md)
2. [Software Framework](docs/software_framework.md)
3. [Setup and Notes](docs/setup_and_notes.md)
4. [Calibration and Usage](docs/calibration_and_usage.md) 
5. [Program Execution](docs/program_execution.md)
6. [Video](https://youtu.be/BtfoymwgIUY)

## <u>About the Creaters</u>
The SOLO 6 DoF Motion Platform was created at the [Dynamic Locomotion Group](https://dlg.is.mpg.de) at the [Max-Planck Institute for Intelligent Systems](https://is.mpg.de) by: 
- Nayan Man Singh Pradhan
- Patrick Frank
- An Mo

## <u>Link to Paper</u>
http://dx.doi.org/10.48550/arXiv.2303.17974

Pradhan, N. M. S., Frank, P., Mo, A., & Badri-Spröwitz, A. (2023). Upside down: affordable high-performance motion platform. arXiv preprint arXiv:2303.17974.