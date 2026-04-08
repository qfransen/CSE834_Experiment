import traci

class DataProcessor:
    def __init__(self):
        # Dictionary to track {veh_id: {"entry_time": float, "free_flow_time": float}}
        self.active_trips = {}
        # List to store the calculated delay (in seconds) of each vehicle that has finished its route
        self.completed_delays = []

    def update_delays(self, exclude_vehicles: list = None):
        """
        Monitors departures and arrivals to calculate delays.
        Must be called every simulation step
        :param exclude_vehicles: optional list of vehicle IDs to exclude from delay tracking
        :return: None
        """
        if exclude_vehicles is None:
            exclude_vehicles = []

        current_time = traci.simulation.getTime()

        # Process newly departed vehicles and add to tracking dictionary
        departed = traci.simulation.getDepartedIDList()
        for veh_id in departed:
            # Only track vehicles that are not in the exclude list
            if veh_id in exclude_vehicles:
                continue

            # Calculate the free flow travel time for this specific vehicle
            route_edges = traci.vehicle.getRoute(veh_id)
            veh_max_speed = traci.vehicle.getMaxSpeed(veh_id)

            free_flow_time = 0.0
            for edge_id in route_edges:
                # Assume lane 0 is representative of edge length and speed limit for simplicity
                edge_length = traci.lane.getLength(f"{edge_id}_0")
                edge_speed_limit = traci.lane.getMaxSpeed(f"{edge_id}_0")

                # Take the fastest the vehicle will travel on this edge
                effective_max_speed = min(veh_max_speed, edge_speed_limit)
                free_flow_time += edge_length / effective_max_speed

            self.active_trips[veh_id] = {
                "entry_time": current_time,
                "free_flow_time": free_flow_time
            }

        # Process arrived vehicles and calculate delay
        arrived = traci.simulation.getArrivedIDList()
        for veh_id in arrived:
            if veh_id in exclude_vehicles:
                continue

            # Vehicle delay: actual trip time - free flow time
            if veh_id in self.active_trips:
                trip_info = self.active_trips.pop(veh_id)
                actual_trip_time = current_time - trip_info["entry_time"]
                delay = actual_trip_time - trip_info["free_flow_time"]
                self.completed_delays.append(max(delay, 0.0))  # Ensure we don't record negative delays

    def get_total_summary(self, exclude_vehicles: list = None):
        """
        Provides a summary of all completed trips
        :param exclude_vehicles: optional list of vehicle IDs to exclude from the summary
        :return: summary dictionary
        """
        if exclude_vehicles is None:
            exclude_vehicles = []

        # Filter out delays from excluded vehicles
        relevant_delays = [delay for delay in self.completed_delays if delay not in exclude_vehicles]
        ongoing_trips = len([trip for trip in self.active_trips if trip not in exclude_vehicles])

        if len(relevant_delays) == 0:
            return {
                "average_delay": 0,
                "completed_trips": 0,
                "ongoing_trips": ongoing_trips
            }

        completed_trips = len(relevant_delays)

        average_delay = sum(relevant_delays) / completed_trips
        return {
            "average_delay": average_delay,
            "completed_trips": completed_trips,
            "ongoing_trips": ongoing_trips
        }

    def print_total_summary(self, summary: dict):
        """
        Prints a summary of all completed trips to the console
        :param summary: summary dictionary
        :return: None
        """
        print("\nTotal Summary:")
        print(f"Completed trips: {summary['completed_trips']}")
        print(f"Ongoing trips: {summary['ongoing_trips']}")
        if summary['completed_trips'] > 0:
            print(f"Average delay: {summary['average_delay']:.2f} s")


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


    def print_step_summary(self, summary: dict, step: int):
        """
        Prints a summary of the current simulation state to the console
        :param summary: summary dictionary
        :param step: current SUMO simulation step
        :return: None
        """
        print(f"\nStep {step} Summary:")
        print(f"Vehicle count: {summary['vehicle_count']}")
        if summary['vehicle_count'] > 0:
            print(f"Average speed: {summary['average_speed']:.2f} m/s")
            print(f"Average CO2 emissions: {summary['average_co2']:.2f} g/s")
            print(f"Average trip time: {summary['average_trip_time']:.2f} s")
