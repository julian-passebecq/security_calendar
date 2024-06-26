import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
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


# Updated sample data generation
def generate_sample_data():
    agents = [
        Agent(1, "Agent 1", ['fire_certification', 'fighting_diploma'], 40),
        Agent(2, "Agent 2", ['fire_certification'], 40),
        Agent(3, "Agent 3", ['fighting_diploma'], 40),
        Agent(4, "Agent 4", [], 40),
        Agent(5, "Agent 5", [], 32)
    ]

    clients = [
        Client(1, "Client 1", {'Monday': ['firecheck'], 'Wednesday': ['night_security']}, 'A'),
        Client(2, "Client 2", {'Tuesday': ['fighting'], 'Thursday': ['security_camera']}, 'B'),
        Client(3, "Client 3", {'Monday': ['night_security'], 'Friday': ['security_camera']}, 'C'),
        Client(4, "Client 4", {'Wednesday': ['firecheck'], 'Thursday': ['night_security']}, 'A'),
        Client(5, "Client 5", {'Tuesday': ['security_camera'], 'Friday': ['fighting']}, 'B')
    ]

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
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    day_shift_start = datetime.strptime("09:00", "%H:%M")
    night_shift_start = datetime.strptime("21:00", "%H:%M")

    for day in days:
        for client in clients:
            if day in client.required_interventions:
                for intervention in client.required_interventions[day]:
                    task = TASKS[intervention]
                    shift_start = night_shift_start if task.shift == 'night' else day_shift_start

                    available_agents = [
                        a for a in agents
                        if (task.required_skill in a.skills or task.required_skill is None) and
                           a.scheduled_hours + task.duration <= a.hours_per_week
                    ]

                    if available_agents:
                        agent = min(available_agents, key=lambda a: a.scheduled_hours)
                        travel_time = calculate_travel_time(agent.current_location,
                                                            'HQ' if task.location == 'HQ' else client.zone)

                        start_time = shift_start + travel_time
                        end_time = start_time + timedelta(hours=task.duration)

                        agent.schedule[day].append({
                            'client': client.name,
                            'task': task.type,
                            'start': start_time,
                            'end': end_time,
                            'zone': client.zone if task.location == 'onsite' else 'HQ'
                        })

                        agent.scheduled_hours += task.duration + travel_time.total_seconds() / 3600
                        agent.current_location = 'HQ' if task.location == 'HQ' else client.zone

    return agents


# Create visual calendar
def create_visual_calendar(agents):
    data = []
    for agent in agents:
        for day, tasks in agent.schedule.items():
            for task in tasks:
                data.append(dict(Task=agent.name, Start=task['start'], Finish=task['end'],
                                 Resource=f"{task['client']} - {task['task']} ({task['zone']})"))

    fig = ff.create_gantt(data, index_col='Resource', show_colorbar=True, group_tasks=True)
    fig.update_layout(title='Agent Schedules', xaxis_title='Time', yaxis_title='Agent')
    return fig


# Streamlit app
def main():
    st.title("Comprehensive Security Company Scheduler")

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
                        task['zone'],
                        task['start'].strftime("%H:%M"),
                        task['end'].strftime("%H:%M")
                    ])
            schedule_df = pd.DataFrame(schedule_data,
                                       columns=["Day", "Client", "Task", "Zone", "Start Time", "End Time"])
            st.table(schedule_df)

        st.header("Agent Workload Summary")
        workload_data = [[a.name, round(a.scheduled_hours, 2)] for a in scheduled_agents]
        workload_df = pd.DataFrame(workload_data, columns=["Agent", "Scheduled Hours (including travel)"])
        st.table(workload_df)

        st.header("Schedule Analytics")
        total_tasks = sum(len(tasks) for c in clients for tasks in c.required_interventions.values())
        assigned_tasks = sum(len(tasks) for a in scheduled_agents for tasks in a.schedule.values())
        unassigned_tasks = total_tasks - assigned_tasks

        st.write(f"Total tasks: {total_tasks}")
        st.write(f"Assigned tasks: {assigned_tasks}")
        st.write(f"Unassigned tasks: {unassigned_tasks}")

        total_available_hours = sum(a.hours_per_week for a in agents)
        total_scheduled_hours = sum(a.scheduled_hours for a in scheduled_agents)
        utilization_rate = (total_scheduled_hours / total_available_hours) * 100
        st.write(f"Agent Utilization Rate: {utilization_rate:.2f}%")

        st.header("Visual Calendar")
        fig = create_visual_calendar(scheduled_agents)
        st.plotly_chart(fig)


if __name__ == "__main__":
    main()