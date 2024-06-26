import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import random


# (Keep the existing Agent, Client, Task, and TASKS definitions)

# Sample data generation
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


# (Keep the existing create_schedule and create_visual_calendar functions)

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

        st.header("Agent Schedules")
        for agent in scheduled_agents:
            st.subheader(f"{agent.name}")
            schedule_data = []
            total_hours = 0
            for day, tasks in agent.schedule.items():
                daily_hours = 0
                for task in tasks:
                    duration = (task['end'] - task['start']).total_seconds() / 3600
                    schedule_data.append([
                        day,
                        task['client'],
                        task['task'],
                        task['zone'],
                        task['start'].strftime("%H:%M"),
                        task['end'].strftime("%H:%M"),
                        f"{duration:.2f}"
                    ])
                    daily_hours += duration
                total_hours += daily_hours
                schedule_data.append([day, "Daily Total", "", "", "", "", f"{daily_hours:.2f}"])
            schedule_data.append(["Weekly Total", "", "", "", "", "", f"{total_hours:.2f}"])
            schedule_df = pd.DataFrame(schedule_data,
                                       columns=["Day", "Client", "Task", "Zone", "Start Time", "End Time", "Hours"])
            st.table(schedule_df)

        st.header("Agent Workload Summary")
        workload_data = [[a.name, sum((task['end'] - task['start']).total_seconds() / 3600
                                      for tasks in a.schedule.values() for task in tasks)]
                         for a in scheduled_agents]
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
        total_scheduled_hours = sum(workload_data[i][1] for i in range(len(workload_data)))
        utilization_rate = (total_scheduled_hours / total_available_hours) * 100
        st.write(f"Agent Utilization Rate: {utilization_rate:.2f}%")

        st.header("Visual Calendar")
        fig = create_visual_calendar(scheduled_agents)
        st.plotly_chart(fig)


if __name__ == "__main__":
    main()