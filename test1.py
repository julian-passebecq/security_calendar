import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

# Define shift types
SHIFTS = {
    'Day1': {'start': '06:00', 'end': '14:00'},
    'Day2': {'start': '09:00', 'end': '17:00'},
    'Night1': {'start': '18:00', 'end': '02:00'},
    'Night2': {'start': '22:00', 'end': '06:00'}
}


# Data models
class Agent:
    def __init__(self, id, name, skills, hours_per_week, shift_type):
        self.id = id
        self.name = name
        self.skills = skills
        self.hours_per_week = hours_per_week
        self.shift_type = shift_type
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
    'fighting': {'duration': 4, 'required_skill': 'fighting_diploma', 'shift': 'night'},
    'security_camera': {'duration': 2, 'required_skill': None, 'shift': 'any'},
    'night_security': {'duration': 4, 'required_skill': None, 'shift': 'night'}
}


# Sample data generation
def generate_sample_data():
    agents = [
        Agent(1, "Agent 1", ['fire_certification', 'fighting_diploma'], 40, 'Day1'),
        Agent(2, "Agent 2", ['fire_certification'], 40, 'Day2'),
        Agent(3, "Agent 3", ['fighting_diploma'], 40, 'Night1'),
        Agent(4, "Agent 4", [], 40, 'Night2'),
        Agent(5, "Agent 5", [], 32, 'Day1')
    ]

    zones = ['A', 'B', 'C']
    intervention_types = list(TASKS.keys())
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    clients = []
    for i in range(1, 11):
        required_interventions = {}
        for day in days:
            required_interventions[day] = random.sample(intervention_types, random.randint(2, 3))

        clients.append(Client(
            i,
            f"Client {i}",
            required_interventions,
            random.choice(zones)
        ))

    return agents, clients


# Improved scheduling function
def create_schedule(agents, clients):
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        for client in clients:
            for task_type in client.required_interventions[day]:
                task = TASKS[task_type]
                available_agents = [
                    a for a in agents
                    if (task['required_skill'] in a.skills or task['required_skill'] is None) and
                       (task['shift'] == 'any' or task['shift'] == a.shift_type.lower()[:3]) and
                       a.scheduled_hours + task['duration'] <= a.hours_per_week
                ]
                if available_agents:
                    agent = min(available_agents, key=lambda a: a.scheduled_hours)
                    shift = SHIFTS[agent.shift_type]
                    start_time = datetime.strptime(shift['start'], "%H:%M")
                    end_time = start_time + timedelta(hours=task['duration'])
                    if end_time > datetime.strptime(shift['end'], "%H:%M"):
                        continue  # Skip if task doesn't fit in shift
                    agent.schedule[day].append({
                        'client': client.name,
                        'task': task_type,
                        'start': start_time.strftime("%H:%M"),
                        'end': end_time.strftime("%H:%M")
                    })
                    agent.scheduled_hours += task['duration']
    return agents


# Streamlit app
def main():
    st.title("Improved Security Company Scheduler")

    agents, clients = generate_sample_data()

    st.header("Agent Information")
    agent_data = [[a.name, ", ".join(a.skills), a.hours_per_week, a.shift_type] for a in agents]
    agent_df = pd.DataFrame(agent_data, columns=["Agent", "Skills", "Hours per Week", "Shift Type"])
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
            st.subheader(f"{agent.name} ({agent.shift_type})")
            schedule_data = []
            for day, tasks in agent.schedule.items():
                for task in tasks:
                    schedule_data.append([
                        day,
                        task['client'],
                        task['task'],
                        task['start'],
                        task['end']
                    ])
            schedule_df = pd.DataFrame(schedule_data, columns=["Day", "Client", "Task", "Start Time", "End Time"])
            st.table(schedule_df)

        st.header("Agent Workload Summary")
        workload_data = [[a.name, a.scheduled_hours, a.shift_type] for a in scheduled_agents]
        workload_df = pd.DataFrame(workload_data, columns=["Agent", "Scheduled Hours", "Shift Type"])
        st.table(workload_df)

        # Calculate and display analytics
        total_tasks = sum(len(tasks) for c in clients for tasks in c.required_interventions.values())
        assigned_tasks = sum(len(tasks) for a in scheduled_agents for tasks in a.schedule.values())
        st.header("Schedule Analytics")
        st.write(f"Total tasks: {total_tasks}")
        st.write(f"Assigned tasks: {assigned_tasks}")
        st.write(f"Unassigned tasks: {total_tasks - assigned_tasks}")

        total_available_hours = sum(a.hours_per_week for a in agents)
        total_scheduled_hours = sum(a.scheduled_hours for a in scheduled_agents)
        utilization_rate = (total_scheduled_hours / total_available_hours) * 100
        st.write(f"Agent Utilization Rate: {utilization_rate:.2f}%")


if __name__ == "__main__":
    main()