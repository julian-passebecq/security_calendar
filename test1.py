import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date


# Data models
class Agent:
    def __init__(self, id, name, skills, shift_type):
        self.id = id
        self.name = name
        self.skills = skills
        self.shift_type = shift_type  # 'day' or 'night'


class Client:
    def __init__(self, id, name, requirements, start_time, end_time):
        self.id = id
        self.name = name
        self.requirements = requirements
        self.start_time = start_time
        self.end_time = end_time


# Sample data generation
def generate_sample_data():
    agents = [
        Agent(1, "John Doe", ["general", "firefighting"], "day"),
        Agent(2, "Jane Smith", ["general", "driving"], "night"),
        Agent(3, "Mike Johnson", ["general"], "day"),
        Agent(4, "Emily Brown", ["general", "firefighting"], "night"),
        Agent(5, "Chris Wilson", ["general", "driving"], "day")
    ]

    clients = [
        Client(1, "Office Building A", ["general"], "09:00", "17:00"),
        Client(2, "Nightclub B", ["general", "firefighting"], "22:00", "04:00"),
        Client(3, "Residential Complex C", ["general", "driving"], "00:00", "23:59"),
        Client(4, "Factory D", ["general", "firefighting"], "06:00", "18:00"),
        Client(5, "Mall E", ["general"], "10:00", "22:00")
    ]

    return agents, clients


# Simple scheduling algorithm
def create_schedule(agents, clients, start_date, num_days):
    schedule = {}
    current_date = start_date

    for _ in range(num_days):
        day_schedule = {}
        for client in clients:
            available_agents = [agent for agent in agents
                                if set(client.requirements).issubset(set(agent.skills))
                                and ((agent.shift_type == 'day' and client.start_time < "18:00")
                                     or (agent.shift_type == 'night' and client.start_time >= "18:00"))]
            if available_agents:
                assigned_agent = available_agents[0]  # Simple assignment, take the first available agent
                day_schedule[client.name] = assigned_agent.name
            else:
                day_schedule[client.name] = "Unassigned"

        schedule[current_date.strftime("%Y-%m-%d")] = day_schedule
        current_date += timedelta(days=1)

    return schedule


# Streamlit app
def main():
    st.title("Security Company Scheduler POC")

    agents, clients = generate_sample_data()

    st.header("Client Requirements")
    client_data = [[c.name, ", ".join(c.requirements), c.start_time, c.end_time] for c in clients]
    client_df = pd.DataFrame(client_data, columns=["Client", "Requirements", "Start Time", "End Time"])
    st.table(client_df)

    st.header("Agent Information")
    agent_data = [[a.name, ", ".join(a.skills), a.shift_type] for a in agents]
    agent_df = pd.DataFrame(agent_data, columns=["Agent", "Skills", "Shift Type"])
    st.table(agent_df)

    st.header("Generate Schedule")
    start_date = st.date_input("Start Date", date.today())
    num_days = st.number_input("Number of Days", min_value=1, max_value=7, value=7)

    if st.button("Generate Schedule"):
        schedule = create_schedule(agents, clients, start_date, num_days)

        st.header("Weekly Schedule")
        schedule_df = pd.DataFrame(schedule).T  # Transpose to have dates as rows
        st.table(schedule_df)


if __name__ == "__main__":
    main()