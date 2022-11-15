# Instructions to run program
The software package can be executed using the Command Line Interface or the In-line Terminal Interface. 

## Command Line Interface
The command line interface offers a step-by-step interface that prompts the user for inputs on what program configuration the package should run. This method is convenient and recommended for users who are not familir with the software package.

`cd src`  
`bash start_program.sh`

---

## In-line Terminal Interface
The in-line terminal interface offers a one line quick and repeatable flag based command system for users who are familiar with the software package.

`cd src`  
`bash start_program.sh <flags>`

---

### In-line Terminal Interface `<flags>`
`-h`     Print help.  

`-s`     Define sequence type.  
       `0`   Use pre-existing sequence  
       `a`   Use arbitrary sequence  
       `s`   Use sine sequence  
       `c`   Use circular sequence  
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
