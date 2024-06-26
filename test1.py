import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time


# Data models
class Agent:
    def __init__(self, id, name, skills, max_hours_per_week=40):
        self.id = id
        self.name = name
        self.skills = skills
        self.max_hours_per_week = max_hours_per_week
        self.scheduled_hours = 0


class Client:
    def __init__(self, id, name, requirements, start_time, end_time, days_of_week):
        self.id = id
        self.name = name
        self.requirements = requirements
        self.start_time = start_time
        self.end_time = end_time
        self.days_of_week = days_of_week


class Shift:
    def __init__(self, client, start_time, end_time, agent=None):
        self.client = client
        self.start_time = start_time
        self.end_time = end_time
        self.agent = agent


# Sample data generation
def generate_sample_data():
    agents = [
        Agent(1, "John Doe", ["general", "firefighting"]),
        Agent(2, "Jane Smith", ["general", "driving"]),
        Agent(3, "Mike Johnson", ["general"]),
        Agent(4, "Emily Brown", ["general", "firefighting"]),
        Agent(5, "Chris Wilson", ["general", "driving"])
    ]

    clients = [
        Client(1, "Office Building A", ["general"], time(9, 0), time(17, 0), [0, 1, 2, 3, 4]),
        Client(2, "Nightclub B", ["general", "firefighting"], time(22, 0), time(4, 0), [4, 5]),
        Client(3, "Residential Complex C", ["general", "driving"], time(0, 0), time(23, 59), [0, 1, 2, 3, 4, 5, 6]),
        Client(4, "Factory D", ["general", "firefighting"], time(6, 0), time(18, 0), [0, 1, 2, 3, 4]),
        Client(5, "Mall E", ["general"], time(10, 0), time(22, 0), [0, 1, 2, 3, 4, 5, 6])
    ]

    return agents, clients


# Improved scheduling algorithm
def create_schedule(agents, clients, start_date, num_days):
    schedule = []
    current_date = start_date

    for _ in range(num_days):
        day_shifts = []
        for client in clients:
            if current_date.weekday() in client.days_of_week:
                shift_start = datetime.combine(current_date, client.start_time)
                shift_end = datetime.combine(current_date, client.end_time)
                if shift_end <= shift_start:
                    shift_end += timedelta(days=1)

                shift = Shift(client, shift_start, shift_end)
                day_shifts.append(shift)

        # Sort shifts by start time
        day_shifts.sort(key=lambda x: x.start_time)

        for shift in day_shifts:
            available_agents = [
                agent for agent in agents
                if set(shift.client.requirements).issubset(set(agent.skills))
                   and agent.scheduled_hours + (
                               shift.end_time - shift.start_time).total_seconds() / 3600 <= agent.max_hours_per_week
            ]

            if available_agents:
                # Assign the agent with the least scheduled hours
                assigned_agent = min(available_agents, key=lambda a: a.scheduled_hours)
                shift.agent = assigned_agent
                assigned_agent.scheduled_hours += (shift.end_time - shift.start_time).total_seconds() / 3600

            schedule.append(shift)

        current_date += timedelta(days=1)

    return schedule


# Streamlit app
def main():
    st.title("Security Company Scheduler POC")

    agents, clients = generate_sample_data()

    st.header("Client Requirements")
    client_data = [
        [c.name, ", ".join(c.requirements),
         c.start_time.strftime("%H:%M"), c.end_time.strftime("%H:%M"),
         ", ".join([["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][d] for d in c.days_of_week])]
        for c in clients
    ]
    client_df = pd.DataFrame(client_data, columns=["Client", "Requirements", "Start Time", "End Time", "Days"])
    st.table(client_df)

    st.header("Agent Information")
    agent_data = [[a.name, ", ".join(a.skills), a.max_hours_per_week] for a in agents]
    agent_df = pd.DataFrame(agent_data, columns=["Agent", "Skills", "Max Hours/Week"])
    st.table(agent_df)

    st.header("Generate Schedule")
    start_date = st.date_input("Start Date", datetime.now().date())
    num_days = st.number_input("Number of Days", min_value=1, max_value=14, value=7)

    if st.button("Generate Schedule"):
        schedule = create_schedule(agents, clients, start_date, num_days)

        st.header("Weekly Schedule")
        schedule_data = [
            [s.start_time.strftime("%Y-%m-%d %H:%M"),
             s.end_time.strftime("%H:%M"),
             s.client.name,
             s.agent.name if s.agent else "Unassigned"]
            for s in schedule
        ]
        schedule_df = pd.DataFrame(schedule_data, columns=["Date & Start Time", "End Time", "Client", "Assigned Agent"])
        st.dataframe(schedule_df)

        st.header("Agent Workload Summary")
        workload_data = [[a.name, a.scheduled_hours] for a in agents]
        workload_df = pd.DataFrame(workload_data, columns=["Agent", "Scheduled Hours"])
        st.table(workload_df)


if __name__ == "__main__":
    main()