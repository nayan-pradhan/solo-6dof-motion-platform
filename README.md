# solo-6dof-motion-platform

## <u>Instructions to run program</u>:

### Command Line Interface
`cd src`  
`bash start_program.sh`

---

### In-line Terminal Interface
`cd src`  
`bash start_program.sh <flags>`

---

### In-line Terminal Interface `<flags>`
`-h`     Print help.  

`-s`     Define sequence type.  
       `0`   Use pre-existing sequence  
       `a`   Use arbitrary sequence  
       `s`   Use sine sequence  
       `t`   Use step sequence  
    
`-i`     Define inverse kinematics tool.  
       `0`   Use pre-existing inverse kinematics  
       `p`   Use pybullet inverse kinematics  
    
`-c`    Define control environment.  
       `p`   Use pybullet environment  
       `s`   Use solo robot environment  
    
`-p`     Define calibration phase.  
       `x`   Use no calibration  
       `0`   Calibration Phase 0  
       `1`   Calibration Phase 1  
       `2`   Calibration Phase 2  

---

### Notes   
- Smooth landing position is hard-coded (joint angles are pre-defined).  
- To give access of output history files to user, do 'sudo chown user:user \*' in data_files/\*/history/ directory.   

---

### Package Framework Flowchart
![](images/solo-6dof-motion-platform_framework.png)
