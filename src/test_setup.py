# I think this file might only be set up for a Windows environment

import os
import sys
import traci

from utils.data_processor import DataProcessor

# Failsafe to ensure SUMO_HOME is found
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

def run_test():
    # Use 'sumo-gui' to see the visualization, or 'sumo' for headless execution
    sumo_binary = "sumo-gui"
    # TODO: look at xsi:noNamespaceSchemaLocation in the .net.xml and .rou.xml files
    sumo_cmd = [sumo_binary, "-c", "networks/test/test.sumocfg"]

    print("Starting SUMO...")
    traci.start(sumo_cmd)
    processor = DataProcessor()  # our data processor

    step = 0
    target_vehicle = "target_car"
    while step < 10001:
        # print(f"Running simulation step {step}")
        traci.simulationStep()
        # track new and departing vehicles
        processor.update_delays(exclude_vehicles=[target_vehicle])


        newly_spawned_vehicles = traci.simulation.getDepartedIDList()
        for veh_id in newly_spawned_vehicles:
            if traci.vehicle.getTypeID(veh_id) == "cav_car":
                # They just spawned, so we update their route immediately
                traci.vehicle.rerouteTraveltime(veh_id)

        active_vehicles = traci.vehicle.getIDList()
        # stop the target vehicle at step 50
        if step == 51 and target_vehicle in active_vehicles:
            print(f"Stopping {target_vehicle} at step {step}")
            # Use setSpeedMode to override any SUMO checks
            traci.vehicle.setSpeedMode(target_vehicle, 0)
            traci.vehicle.setSpeed(target_vehicle, 0)

            for lane_idx in range(2):
                crash_veh_id = f"crashed_car_{lane_idx}"

                # Add the vehicle directly onto the edge and lane
                traci.vehicle.add(crash_veh_id, routeID="route_main", typeID="cav_car")
                traci.vehicle.moveTo(crash_veh_id, f'highway_middle_{lane_idx}', pos=150.0)

                # Freeze it in place
                traci.vehicle.setSpeedMode(crash_veh_id, 0)
                traci.vehicle.setSpeed(crash_veh_id, 0)
                traci.vehicle.setColor(crash_veh_id, (255, 0, 0))

            print('Updating edge weights and rerouting CAVs')
            # artificially increase travel time in middle section to make it look slow
            traci.edge.adaptTraveltime("highway_middle", 9999)
            # Force CAVs to reroute based on the new travel time
            for veh_id in active_vehicles:
                if traci.vehicle.getTypeID(veh_id) == "cav_car":
                    traci.vehicle.rerouteTraveltime(veh_id)

        # track stats for all other vehicles
        if step % 10 == 0:
            summary = processor.get_current_summary(
                active_vehicles,
                exclude_vehicles=[target_vehicle]
            )
            processor.print_step_summary(summary, step)

        step += 1

    summary = processor.get_total_summary(exclude_vehicles=[target_vehicle])
    processor.print_total_summary(summary)
    processor.save_experiment_data('test_output.csv')

    traci.close()
    print("Simulation complete and closed successfully.")

if __name__ == "__main__":
    run_test()