import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta


# Data models
class Agent:
    def __init__(self, id, name, skills, hours_per_week):
        self.id = id
        self.name = name
        self.skills = skills
        self.hours_per_week = hours_per_week
        self.scheduled_hours = 0
        self.schedule = {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}


class Client:
    def __init__(self, id, name, required_interventions, zone):
        self.id = id
        self.name = name
        self.required_interventions = required_interventions
        self.zone = zone


# Define tasks
TASKS = {
    'firecheck': {'duration': 2, 'required_skill': 'fire_certification', 'shift': 'day'},
    'fighting': {'duration': 5, 'required_skill': 'fighting_diploma', 'shift': 'night'},
    'security_camera': {'duration': 1, 'required_skill': None, 'shift': 'any'},
    'night_security': {'duration': 1, 'required_skill': None, 'shift': 'night'}
}


# Sample data generation
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


# Simplified scheduling function
def create_schedule(agents, clients):
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        for client in clients:
            if day in client.required_interventions:
                for task_type in client.required_interventions[day]:
                    task = TASKS[task_type]
                    available_agents = [a for a in agents if
                                        task['required_skill'] in a.skills or task['required_skill'] is None]
                    if available_agents:
                        agent = min(available_agents, key=lambda a: a.scheduled_hours)
                        start_time = datetime.strptime("09:00", "%H:%M") if task[
                                                                                'shift'] != 'night' else datetime.strptime(
                            "21:00", "%H:%M")
                        end_time = start_time + timedelta(hours=task['duration'])
                        agent.schedule[day].append({
                            'client': client.name,
                            'task': task_type,
                            'start': start_time,
                            'end': end_time
                        })
                        agent.scheduled_hours += task['duration']
    return agents


# Streamlit app
def main():
    st.title("Security Company Scheduler")

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

        st.header("Agent Schedules")
        for agent in scheduled_agents:
            st.subheader(f"{agent.name}")
            schedule_data = []
            for day, tasks in agent.schedule.items():
                for task in tasks:
                    schedule_data.append([
                        day,
                        task['client'],
                        task['task'],
                        task['start'].strftime("%H:%M"),
                        task['end'].strftime("%H:%M")
                    ])
            schedule_df = pd.DataFrame(schedule_data, columns=["Day", "Client", "Task", "Start Time", "End Time"])
            st.table(schedule_df)

        st.header("Agent Workload Summary")
        workload_data = [[a.name, a.scheduled_hours] for a in scheduled_agents]
        workload_df = pd.DataFrame(workload_data, columns=["Agent", "Scheduled Hours"])
        st.table(workload_df)


if __name__ == "__main__":
    main()