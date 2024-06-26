import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random


# Updated data models
class Agent:
    def __init__(self, id, name, skills, hours_per_week):
        self.id = id
        self.name = name
        self.skills = skills
        self.hours_per_week = hours_per_week
        self.scheduled_hours = 0
        self.current_location = 'HQ'


class Client:
    def __init__(self, id, name, required_interventions, zone):
        self.id = id
        self.name = name
        self.required_interventions = required_interventions
        self.zone = zone


class Task:
    def __init__(self, type, duration, location, required_skill):
        self.type = type
        self.duration = duration
        self.location = location
        self.required_skill = required_skill


class Shift:
    def __init__(self, client, day, task):
        self.client = client
        self.day = day
        self.task = task
        self.agent = None
        self.start_time = None


# Define tasks
TASKS = {
    'firecheck': Task('firecheck', 2, 'onsite', 'fire_certification'),
    'fighting': Task('fighting', 5, 'onsite', 'fighting_diploma'),
    'security_camera': Task('security_camera', 1, 'HQ', None),
    'night_security': Task('night_security', 1, 'onsite', None)
}


# Updated sample data generation
def generate_sample_data():
    skills = ['fire_certification', 'fighting_diploma']
    zones = ['A', 'B', 'C']

    agents = [
        Agent(1, "Agent 1", random.sample(skills, 1) + [None], 40),
        Agent(2, "Agent 2", random.sample(skills, 1) + [None], 40),
        Agent(3, "Agent 3", random.sample(skills, 1) + [None], 40),
        Agent(4, "Agent 4", random.sample(skills, 1) + [None], 40),
        Agent(5, "Agent 5", [None], 32)  # This agent works 80% and has no special skills
    ]

    clients = []
    for i in range(1, 11):
        interventions = random.sample(list(TASKS.keys()), random.randint(1, 2))
        clients.append(Client(i, f"Client {i}", interventions, random.choice(zones)))

    return agents, clients


# Helper function to calculate travel time
def calculate_travel_time(zone1, zone2):
    if zone1 == 'HQ' or zone2 == 'HQ':
        return timedelta(minutes=30)
    elif zone1 == zone2:
        return timedelta(minutes=30)
    else:
        return timedelta(hours=1)


# Improved scheduling algorithm
def create_schedule(agents, clients):
    schedule = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    for day in days:
        for client in clients:
            for intervention in client.required_interventions:
                task = TASKS[intervention]
                shift = Shift(client, day, task)

                available_agents = [
                    a for a in agents
                    if (task.required_skill in a.skills or task.required_skill is None) and
                       a.scheduled_hours + task.duration <= 5.5  # 5.5 hours max per day
                ]

                if available_agents:
                    agent = min(available_agents, key=lambda a: a.scheduled_hours)
                    travel_time = calculate_travel_time(agent.current_location,
                                                        'HQ' if task.location == 'HQ' else client.zone)

                    shift.agent = agent
                    shift.start_time = datetime.strptime("09:00", "%H:%M") + travel_time

                    agent.scheduled_hours += task.duration + travel_time.total_seconds() / 3600
                    agent.current_location = 'HQ' if task.location == 'HQ' else client.zone

                schedule.append(shift)

    return schedule


# Streamlit app
def main():
    st.title("Refined Security Company Scheduler")

    agents, clients = generate_sample_data()

    st.header("Agent Information")
    agent_data = [[a.name, ", ".join(filter(None, a.skills)), a.hours_per_week] for a in agents]
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
            if s.agent:
                end_time = s.start_time + timedelta(hours=s.task.duration)
                schedule_data.append([
                    s.day,
                    s.client.name,
                    s.client.zone,
                    s.task.type,
                    s.task.location,
                    s.agent.name,
                    s.start_time.strftime("%H:%M"),
                    end_time.strftime("%H:%M")
                ])

        schedule_df = pd.DataFrame(schedule_data, columns=[
            "Day", "Client", "Zone", "Task Type", "Task Location", "Assigned Agent", "Start Time", "End Time"
        ])
        st.dataframe(schedule_df)

        st.header("Agent Workload Summary")
        workload_data = [[a.name, round(a.scheduled_hours, 2)] for a in agents]
        workload_df = pd.DataFrame(workload_data, columns=["Agent", "Scheduled Hours"])
        st.table(workload_df)

        st.header("Schedule Analytics")
        total_tasks = len(schedule)
        assigned_tasks = sum(1 for s in schedule if s.agent is not None)
        unassigned_tasks = total_tasks - assigned_tasks

        st.write(f"Total tasks scheduled: {total_tasks}")
        st.write(f"Assigned tasks: {assigned_tasks}")
        st.write(f"Unassigned tasks: {unassigned_tasks}")

        total_available_hours = sum(a.hours_per_week for a in agents) * 5.5 / 40  # Adjusting for 5.5 hour workday
        total_scheduled_hours = sum(a.scheduled_hours for a in agents)
        utilization_rate = (total_scheduled_hours / total_available_hours) * 100
        st.write(f"Agent Utilization Rate: {utilization_rate:.2f}%")

        # Task type breakdown
        task_counts = {}
        for s in schedule:
            task_counts[s.task.type] = task_counts.get(s.task.type, 0) + 1
        st.write("Task Breakdown:")
        for task_type, count in task_counts.items():
            st.write(f"- {task_type}: {count}")


if __name__ == "__main__":
    main()