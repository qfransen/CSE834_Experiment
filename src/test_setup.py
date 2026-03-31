# I think this file might only be set up for a Windows environment

import os
import sys
import traci

# Failsafe to ensure SUMO_HOME is found
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

def run_test():
    # Use 'sumo-gui' to see the visualization, or 'sumo' for headless execution
    sumo_binary = "sumo"
    # TODO: look at xsi:noNamespaceSchemaLocation in the .net.xml and .rou.xml files
    sumo_cmd = [sumo_binary, "-c", "networks/test.sumocfg"]

    print("Starting SUMO...")
    traci.start(sumo_cmd)

    step = 0
    while step < 100:
        print(f"Running simulation step {step}")
        traci.simulationStep()
        # Example interaction: get the number of vehicles currently in the network
        veh_count = traci.vehicle.getIDCount()
        print(f"Step {step}: {veh_count} vehicles active.")
        step += 1

    traci.close()
    print("Simulation complete and closed successfully.")

if __name__ == "__main__":
    run_test()