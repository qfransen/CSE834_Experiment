# SUMO Traffic Simulation Repository

This repository contains the simulation framework, source code, and dataset used to evaluate the 
macroscopic impact of varying Connected Vehicle (CV) penetration rates under adverse capacity constraints.

## Our experiment data
The data we used in our analysis in available in `data.csv`.

## Prerequisites and Setup
To run the simulations in this repository, you must have the 
**Eclipse SUMO** (Simulation of Urban MObility) traffic simulator installed.

1. Install SUMO: [official Eclipse SUMO website](https://eclipse.dev/sumo/)
2. Set Environment Variable: You must set the `SUMO_HOME` environment variable on your system to point to the root directory of your SUMO installation
3. Install Python dependencies: `pip install -r requirements.txt`

## Run a simulation
Navigate to the `src/` directory and execute the main script:

`python .\launch_experiment.py -c <connectivity>`

where `<connectivity>` is a decimal value between 0 and 1 that 
determines the percentage of vehicles that are connected self-driving vehicles.

## Repository Structure
* **`networks/`**: Store all SUMO-specific XML files here (`.net.xml`, `.rou.xml`, `.add.xml`, `.sumocfg`). Keeping the simulation assets separated from the logic makes the repo much easier to navigate.
* **`src/`**: Main Python execution scripts.
    * **`src/agents/`**: If you plan to implement any algorithmic control logic, keep those classes here.
    * **`src/utils/`**: Helper scripts (e.g., parsing SUMO output files or generating random routes).