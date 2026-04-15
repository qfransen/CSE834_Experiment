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

    print("Environment check passed: SUMO_HOME found.")


def main(connectivity):
    # Use 'sumo-gui' to see the visualization, or 'sumo' for headless execution
    sumo_binary = "sumo-gui"
    sumo_cmd = [sumo_binary, "-c", "networks/run.sumocfg"]

    print(f"Starting SUMO with connectivity: {connectivity*100}%")
    traci.start(sumo_cmd)
    processor = DataProcessor(connectivity=connectivity)  # our data processor

    step = 0
    while step < 2400:
        traci.simulationStep()
        processor.update_delays()

        # Start the crash at 10 minutes (600 seconds)
        if step == 600:
            print(f'Starting crash at step {step}')

            # The target edge on the Northbound I-405
            crash_edge = "124550370"
            # Create a short dummy route for the crashed vehicles
            # (Required because traci.vehicle.add needs a valid routeID)
            traci.route.add("crash_route", [crash_edge])

            total_lanes = traci.edge.getLaneNumber(crash_edge)
            crash_lane_indices = [0, 1, 2]  # Lanes to block (0 is the rightmost lane)
            # Take up 3 lanes on the northbound highway
            for lane_idx in range(total_lanes):
                target_lane = f"{crash_edge}_{lane_idx}"
                if lane_idx in crash_lane_indices:
                    crash_veh_id = f"crashed_car_{lane_idx}"

                    # Add the vehicle directly onto the edge and lane
                    traci.vehicle.add(crash_veh_id, routeID="crash_route", typeID="standard_veh")
                    traci.vehicle.moveTo(crash_veh_id, f'{target_lane}', pos=150.0)

                    # Freeze it in place
                    traci.vehicle.setSpeedMode(crash_veh_id, 0)
                    traci.vehicle.setSpeed(crash_veh_id, 0)
                    traci.vehicle.setLaneChangeMode(crash_veh_id, 0)
                    traci.vehicle.setColor(crash_veh_id, (0, 0, 255))

                    # Close the lane to traffic
                    # Prevents vehicles that don't have class "authority" from entering the lane, effectively blocking it
                    traci.lane.setAllowed(target_lane, ["authority"])
                else:
                    # Slow down open lanes to allow for merging
                    traci.lane.setMaxSpeed(target_lane, 15.0)
        if step % 100 == 0:
            active_vehicles = traci.vehicle.getIDList()
            summary = processor.get_current_summary(
                active_vehicles,
                exclude_vehicles=None
            )
            processor.print_step_summary(summary, step)

        step += 1

    # Simulation is done, print final summary and save data
    summary = processor.get_total_summary(exclude_vehicles=None)
    processor.print_total_summary(summary)
    processor.save_experiment_data('experiment_output.csv')

    traci.close()
    print("Simulation complete and closed successfully.")

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