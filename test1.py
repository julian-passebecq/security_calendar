import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
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
        self.current_location = 'HQ'
        self.schedule = {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}


class Client:
    def __init__(self, id, name, required_interventions, zone):
        self.id = id
        self.name = name
        self.required_interventions = required_interventions
        self.zone = zone


class Task:
    def __init__(self, type, duration, location, required_skill, shift):
        self.type = type
        self.duration = duration
        self.location = location
        self.required_skill = required_skill
        self.shift = shift


# Define tasks
TASKS = {
    'firecheck': Task('firecheck', 2, 'onsite', 'fire_certification', 'day'),
    'fighting': Task('fighting', 5, 'onsite', 'fighting_diploma', 'night'),
    'security_camera': Task('security_camera', 1, 'HQ', None, 'any'),
    'night_security': Task('night_security', 1, 'onsite', None, 'night')
}


# Complete sample data generation function
def generate_sample_data():
    agents = [
        Agent(1, "Agent 1", ['fire_certification', 'fighting_diploma'], 40),
        Agent(2, "Agent 2", ['fire_certification'], 40),
        Agent(3, "Agent 3", ['fighting_diploma'], 40),
        Agent(4, "Agent 4", [], 40),
        Agent(5, "Agent 5", [], 32)
    ]

    zones = ['A', 'B', 'C']
    intervention_types = list(TASKS.keys())
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    clients = []
    for i in range(1, 11):
        required_interventions = {}
        for day in days:
            if random.random() > 0.5:  # 50% chance of having an intervention on each day
                required_interventions[day] = random.sample(intervention_types, random.randint(1, 2))

        clients.append(Client(
            i,
            f"Client {i}",
            required_interventions,
            random.choice(zones)
        ))

    return agents, clients


# Helper function to calculate travel time
def calculate_travel_time(zone1, zone2):
    if zone1 == 'HQ' or zone2 == 'HQ':
        return timedelta(minutes=30)
    elif zone1 == zone2:
        return timedelta(minutes=30)
    else:
        return timedelta(hours=1)


# Scheduling function (keep your existing create_schedule function here)

# Visual calendar function (keep your existing create_visual_calendar function here)

# Streamlit app
def main():
    st.title("Security Company Scheduler (8-Hour Workdays)")

    agents, clients = generate_sample_data()

    st.header("Agent Information")
    agent_data = [[a.name, ", ".join(a.skills), a.hours_per_week] for a in agents]
    agent_df = pd.DataFrame(agent_data, columns=["Agent", "Skills", "Hours per Week"])
    st.table(agent_df)

    st.header("Client Requirements")
    for client in clients:
        st.subheader(f"{client.name} (Zone {client.zone})")
        client_data = [[day, ", ".join(tasks)] for day, tasks in client.required_interventions.items()]
        client_df = pd.DataFrame(client_data, columns=["Day", "Required Interventions"])
        st.table(client_df)

    if st.button("Generate Schedule"):
        scheduled_agents = create_schedule(agents, clients)

        # (Keep the rest of your main function here, including displaying schedules,
        # workload summary, analytics, and visual calendar)


if __name__ == "__main__":
    main()