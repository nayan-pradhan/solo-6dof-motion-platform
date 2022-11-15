# Hardware Framework

<p align="center">
  <img src="../images/solo_render_labelled.png" width="500"/>
</p>

The hardware framework consists of three main components: 
1. the SOLO robot,
2. the platform attached to the legs of the SOLO robot, and
3. the component that makes sure the robot is fixed to a table.

The figure above shows the robot fixed to an optic table with the attached platform.

### 1. SOLO robot
The SOLO 12 Robot is a quadruped robot (assembled from four legs) of total mass $2.2$ kg with a torque-controller for tracking full-body motions computed with a kino-dynamic motion optimizer \cite{herzog2016structured} \cite{ponton2018time}. The brushless actuator module used in the SOLO robot consists of a $9:1$ dual-stage timing belt transmission, a high-resolution optical encoder, and a $5000$ count-per-revolution code wheel mounted directly on the motor shaft. The desired joint torques are converted into desired motor current using the relationship $\tau_{joint}=k_{i}iN$ where $k_{i}=0.025$ Nm/A and the gear reduction $N=9$ leading to a $\tau_{joint}=0.225i$. The actuators can output $\tau_{max}=2.7$ Nm joint torque at $12$ A. More information regarding the SOLO robot can be found in the Open Dynamic Robot Initiative [Website](https://open-dynamic-robot-initiative.github.io) and their [GitHub](https://github.com/open-dynamic-robot-initiative). 
<p align="center">
  <img src="../images/robot_solo12.png" width="500"/>  
</p>
<p align="center">Solo12 Quadruped Robot. Picture source: PAL robotics.</p>

