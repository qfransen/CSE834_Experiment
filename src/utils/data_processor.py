import traci

class DataProcessor:
    def __init(self):
        # Can add in state variables for tracking cumulative stats over entire simultation
        pass

    def get_current_summary(self, active_vehicles: list, exclude_vehicles: list = None):
        """
        Calculates average speed, emissions, and trip time for all currently active vehicles
        :param active_vehicles: list of vehicle IDs currently active in the simulation
        :param exclude_vehicles: optional list of vehicle IDs to exclude from the summary (e.g., the target vehicle)
        :return: summary dictionary
        """
        if exclude_vehicles is None:
            exclude_vehicles = []

        # Filter out excluded vehicles
        relevant_vehicles = [veh_id for veh_id in active_vehicles if veh_id not in exclude_vehicles]
        veh_count = len(relevant_vehicles)

        if veh_count == 0:
            return {
                "average_speed": 0,
                "average_co2": 0,
                "average_trip_time": 0,
                "vehicle_count": 0
            }

        total_speed = 0.0
        total_co2 = 0.0
        total_trip_time = 0.0

        current_time = traci.simulation.getTime()

        for veh_id in relevant_vehicles:
            total_speed += traci.vehicle.getSpeed(veh_id)
            total_co2 += traci.vehicle.getCO2Emission(veh_id)

            # TODO: May want to change to keep track of trip times differently
            #  (total time for an individual trip, rather than just current times of trips)
            depart_time = traci.vehicle.getDeparture(veh_id)
            total_trip_time += (current_time - depart_time)

        return {
            "average_speed": total_speed / veh_count,
            "average_co2": total_co2 / veh_count,
            "average_trip_time": total_trip_time / veh_count,
            "vehicle_count": veh_count
        }


    def print_summary(self, summary: dict, step: int):
        print(f"\nStep {step} Summary:")
        print(f"Vehicle count: {summary['vehicle_count']}")
        if summary['vehicle_count'] > 0:
            print(f"Average speed: {summary['average_speed']:.2f} m/s")
            print(f"Average CO2 emissions: {summary['average_co2']:.2f} g/s")
            print(f"Average trip time: {summary['average_trip_time']:.2f} s")
