'''
This is the launch point for 1 run of the SUMO simulation experiment.
'''

import os
import sys
import traci
import argparse

from utils.data_processor import DataProcessor

def check_environment():
    # Failsafe to ensure SUMO_HOME is found
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("Please declare environment variable 'SUMO_HOME'")


def main(connectivity):
    # Use 'sumo-gui' to see the visualization, or 'sumo' for headless execution
    sumo_binary = "sumo-gui"
    sumo_cmd = [sumo_binary, "-c", "networks/experiment/experiment.sumocfg"]

    print(f"Starting SUMO with connectivity: {connectivity*100}%")
    traci.start(sumo_cmd)
    processor = DataProcessor()  # our data processor

    step = 0
    while step < 2400:
        traci.simulationStep()
        processor.update_delays()

        # Start the crash at 10 minutes (600 seconds)
        if step == 600:
            print(f'Starting crash at step {step}')
            # Take up 3 lanes on the northbound highway
            for lane_idx in range(3):
                crash_veh_id = f"crashed_car_{lane_idx}"

                # # Add the vehicle directly onto the edge and lane
                # traci.vehicle.add(crash_veh_id, routeID="route_main", typeID="cav_car")
                # traci.vehicle.moveTo(crash_veh_id, f'highway_middle_{lane_idx}', pos=150.0)
                #
                # # Freeze it in place
                # traci.vehicle.setSpeedMode(crash_veh_id, 0)
                # traci.vehicle.setSpeed(crash_veh_id, 0)
                # traci.vehicle.setColor(crash_veh_id, (255, 0, 0))

if __name__ == "__main__":
    check_environment()

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Launch a SUMO simulation experiment.")
    parser.add_argument('-c',
                        '--connectivity',
                        type=float,
                        required=True,
                        help='The connectivity percentage as a decimal (e.g., 0.1 for 10%)')
    args = parser.parse_args()

    main(args.connectivity)