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
    sumo_binary = "sumo-gui"
    # TODO: look at xsi:noNamespaceSchemaLocation in the .net.xml and .rou.xml files
    sumo_cmd = [sumo_binary, "-c", "networks/test/test.sumocfg"]

    print("Starting SUMO...")
    traci.start(sumo_cmd)

    step = 0
    target_vehicle = "target_car"
    while step < 1000:
        # print(f"Running simulation step {step}")
        traci.simulationStep()

        active_vehicles = traci.vehicle.getIDList()
        # stop the target vehicle at step 50
        if step == 50 and target_vehicle in active_vehicles:
            print(f"Stopping {target_vehicle} at step {step}")
            # Use setSpeedMode to override any SUMO checks
            traci.vehicle.setSpeedMode(target_vehicle, 0)
            traci.vehicle.setSpeed(target_vehicle, 0)

        # track stats for all other vehicles
        if step % 10 == 0:
            average_speed = 0
            co2_emissions = 0
            total = 0
            for veh_id in active_vehicles:
                if veh_id != target_vehicle:
                    speed = traci.vehicle.getSpeed(veh_id)
                    emit1 = traci.vehicle.getCO2Emission(veh_id)
                    emit2 = traci.vehicle.getCOEmission(veh_id)
                    # print(f'{emit1=}, {emit2=}')

                    average_speed += speed
                    co2_emissions += emit1
                    total += 1
            if total > 0:
                average_speed /= total
                co2_emissions /= total
                print(f"Step {step}: "
                      f"\nAverage speed of other vehicles = {average_speed:.2f} m/s"
                      f"\nAverage CO2 emissions of other vehicles = {co2_emissions:.2f}")

        # Example interaction: get the number of vehicles currently in the network
        veh_count = traci.vehicle.getIDCount()
        # print(f"Step {step}: {veh_count} vehicles active.")
        step += 1

    traci.close()
    print("Simulation complete and closed successfully.")

if __name__ == "__main__":
    run_test()