import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random


# Data models
class Agent:
    def __init__(self, id, name, skills, hours_per_week):
        self.id = id
        self.name = name
        self.skills = skills
        self.hours_per_week = hours_per_week
        self.scheduled_hours = 0
        self.current_location = None


class Client:
    def __init__(self, id, name, required_interventions, zone):
        self.id = id
        self.name = name
        self.required_interventions = required_interventions
        self.zone = zone


class Shift:
    def __init__(self, client, day, shift_type, start_time, intervention_type):
        self.client = client
        self.day = day
        self.shift_type = shift_type
        self.start_time = start_time
        self.intervention_type = intervention_type
        self.agent = None
        self.breaks = []


# Updated sample data generation
def generate_sample_data():
    skills = ["fighting", "firecheck", "on_site", "security_system"]
    zones = ["A", "B", "C"]

    agents = [
        Agent(1, "Agent 1", random.sample(skills, 3), 40),
        Agent(2, "Agent 2", random.sample(skills, 3), 40),
        Agent(3, "Agent 3", random.sample(skills, 3), 40),
        Agent(4, "Agent 4", random.sample(skills, 3), 40),
        Agent(5, "Agent 5", random.sample(skills, 2), 32)  # This agent works 80%
    ]

    clients = [
        Client(i, f"Client {i}", random.sample(skills, random.randint(1, 2)), random.choice(zones))
        for i in range(1, 11)
    ]

    return agents, clients


# Helper function to calculate travel time
def calculate_travel_time(zone1, zone2):
    if zone1 == zone2:
        return timedelta(minutes=30)
    else:
        return timedelta(hours=1)


# Improved scheduling algorithm
def create_schedule(agents, clients):
    schedule = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    shift_types = {
        'Day': [datetime.strptime("05:30", "%H:%M"), datetime.strptime("08:00", "%H:%M")],
        'Night': [datetime.strptime("17:30", "%H:%M"), datetime.strptime("20:00", "%H:%M")]
    }

    for day in days:
        for shift_type, start_times in shift_types.items():
            for client in clients:
                for intervention in client.required_interventions:
                    start_time = random.choice(start_times)
                    shift = Shift(client, day, shift_type, start_time, intervention)

                    # Sort available agents by scheduled hours (least to most)
                    available_agents = sorted(
                        [a for a in agents if intervention in a.skills and a.scheduled_hours < a.hours_per_week],
                        key=lambda a: a.scheduled_hours
                    )

                    if available_agents:
                        agent = available_agents[0]  # Select the agent with the least scheduled hours

                        # Calculate travel time
                        if agent.current_location:
                            travel_time = calculate_travel_time(agent.current_location, client.zone)
                            shift.start_time += travel_time

                        shift.agent = agent
                        agent.scheduled_hours += 8  # 8-hour shift
                        agent.current_location = client.zone

                        # Add breaks
                        shift_end = shift.start_time + timedelta(hours=8)
                        break_times = [
                            shift.start_time + timedelta(hours=2),
                            shift.start_time + timedelta(hours=4),  # Lunch/Dinner break
                            shift.start_time + timedelta(hours=6)
                        ]
                        shift.breaks = [
                            (bt, bt + timedelta(minutes=15 if i != 1 else 45))
                            for i, bt in enumerate(break_times)
                        ]

                    schedule.append(shift)

    return schedule


# Streamlit app
def main():
    st.title("Improved Security Company Scheduler")

    agents, clients = generate_sample_data()

    st.header("Agent Information")
    agent_data = [[a.name, ", ".join(a.skills), a.hours_per_week] for a in agents]
    agent_df = pd.DataFrame(agent_data, columns=["Agent", "Skills", "Hours per Week"])
    st.table(agent_df)

    st.header("Client Requirements")
    client_data = [[c.name, ", ".join(c.required_interventions), c.zone] for c in clients]
    client_df = pd.DataFrame(client_data, columns=["Client", "Required Interventions", "Zone"])
    st.table(client_df)

    if st.button("Generate Schedule"):
        schedule = create_schedule(agents, clients)

        st.header("Weekly Schedule")
        schedule_data = []
        for s in schedule:
            shift_end = s.start_time + timedelta(hours=8)
            break_info = ", ".join([f"{b[0].strftime('%H:%M')}-{b[1].strftime('%H:%M')}" for b in s.breaks])
            schedule_data.append([
                s.day,
                s.shift_type,
                s.start_time.strftime("%H:%M"),
                shift_end.strftime("%H:%M"),
                s.client.name,
                s.client.zone,
                s.intervention_type,
                s.agent.name if s.agent else "Unassigned",
                break_info
            ])

        schedule_df = pd.DataFrame(schedule_data, columns=[
            "Day", "Shift Type", "Start Time", "End Time", "Client", "Zone",
            "Intervention Type", "Assigned Agent", "Breaks"
        ])
        st.dataframe(schedule_df)

        st.header("Agent Workload Summary")
        workload_data = [[a.name, a.scheduled_hours] for a in agents]
        workload_df = pd.DataFrame(workload_data, columns=["Agent", "Scheduled Hours"])
        st.table(workload_df)

        st.header("Schedule Analytics")
        total_shifts = len(schedule)
        assigned_shifts = sum(1 for s in schedule if s.agent is not None)
        unassigned_shifts = total_shifts - assigned_shifts

        st.write(f"Total shifts scheduled: {total_shifts}")
        st.write(f"Assigned shifts: {assigned_shifts}")
        st.write(f"Unassigned shifts: {unassigned_shifts}")

        # Calculate and display utilization rate
        total_available_hours = sum(a.hours_per_week for a in agents)
        total_scheduled_hours = sum(a.scheduled_hours for a in agents)
        utilization_rate = (total_scheduled_hours / total_available_hours) * 100
        st.write(f"Agent Utilization Rate: {utilization_rate:.2f}%")


if __name__ == "__main__":
    main()