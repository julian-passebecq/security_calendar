import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta, date, time


# Data models (keep the existing Agent, Client, and Shift classes)

# Modified sample data generation
def generate_sample_data():
    agents = [
        Agent(1, "John Doe", ["general", "firefighting"]),
        Agent(2, "Jane Smith", ["general", "driving"]),
        Agent(3, "Mike Johnson", ["general"]),
        Agent(4, "Emily Brown", ["general", "firefighting"]),
        Agent(5, "Chris Wilson", ["general", "driving"])
    ]

    clients = [
        Client(1, "Office Building A", ["general"]),
        Client(2, "Nightclub B", ["general", "firefighting"]),
        Client(3, "Residential Complex C", ["general", "driving"]),
        Client(4, "Factory D", ["general", "firefighting"]),
        Client(5, "Mall E", ["general"])
    ]

    # Add client schedules (example)
    client_schedules = {
        "Office Building A": [(time(9, 0), time(17, 0))],  # 9 AM to 5 PM
        "Nightclub B": [(time(22, 0), time(4, 0))],  # 10 PM to 4 AM
        "Residential Complex C": [(time(0, 0), time(23, 59))],  # 24/7
        "Factory D": [(time(6, 0), time(18, 0)), (time(18, 0), time(6, 0))],  # Two shifts
        "Mall E": [(time(10, 0), time(22, 0))]  # 10 AM to 10 PM
    }

    return agents, clients, client_schedules


# Modified scheduling algorithm
def create_schedule(agents, clients, client_schedules, start_date, num_days):
    schedule = []
    current_date = start_date

    for _ in range(num_days):
        for client in clients:
            for start_time, end_time in client_schedules[client.name]:
                shift_start = datetime.combine(current_date, start_time)
                shift_end = datetime.combine(current_date, end_time)
                if shift_end <= shift_start:
                    shift_end += timedelta(days=1)

                available_agents = [agent for agent in agents if
                                    set(client.requirements).issubset(set(agent.qualifications))]
                if available_agents:
                    assigned_agent = random.choice(available_agents)
                    shift = Shift(shift_start, shift_end, client, assigned_agent)
                    schedule.append(shift)

        current_date += timedelta(days=1)

    return schedule


# Create weekly calendar heatmap for clients
def create_client_calendar(client_schedules):
    hours = list(range(24))
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    data = np.zeros((len(days), len(hours)))

    for client, schedules in client_schedules.items():
        for start, end in schedules:
            start_hour = start.hour
            end_hour = end.hour if end > start else end.hour + 24
            for day in range(len(days)):
                for hour in range(start_hour, end_hour):
                    data[day, hour % 24] += 1

    df = pd.DataFrame(data, index=days, columns=hours)
    fig = px.imshow(df, labels=dict(x="Hour of Day", y="Day of Week", color="Number of Clients"),
                    x=hours, y=days, aspect="auto", title="Weekly Client Requirements")
    fig.update_layout(height=400)
    return fig


# Create weekly calendar heatmap for agents
def create_agent_calendar(schedule):
    hours = list(range(24))
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    data = np.zeros((len(days), len(hours), len(set(shift.agent.name for shift in schedule))))

    agents = list(set(shift.agent.name for shift in schedule))
    for shift in schedule:
        day_index = shift.start_time.weekday()
        start_hour = shift.start_time.hour
        end_hour = shift.end_time.hour if shift.end_time > shift.start_time else shift.end_time.hour + 24
        agent_index = agents.index(shift.agent.name)

        for hour in range(start_hour, end_hour):
            data[day_index, hour % 24, agent_index] = 1

    df = pd.DataFrame(data.sum(axis=2), index=days, columns=hours)
    fig = px.imshow(df, labels=dict(x="Hour of Day", y="Day of Week", color="Number of Agents"),
                    x=hours, y=days, aspect="auto", title="Weekly Agent Assignments")
    fig.update_layout(height=400)
    return fig


# Streamlit app
def main():
    st.title("Security Company Scheduler POC")

    agents, clients, client_schedules = generate_sample_data()

    st.header("Client Requirements Calendar")
    client_fig = create_client_calendar(client_schedules)
    st.plotly_chart(client_fig, use_container_width=True)

    st.header("Generate Schedule")
    start_date = st.date_input("Start Date", date.today())
    num_days = st.number_input("Number of Days", min_value=1, max_value=7, value=7)

    if st.button("Generate Schedule"):
        schedule = create_schedule(agents, clients, client_schedules, start_date, num_days)

        st.header("Agent Assignments Calendar")
        agent_fig = create_agent_calendar(schedule)
        st.plotly_chart(agent_fig, use_container_width=True)

        st.header("Detailed Schedule")
        schedule_data = []
        for shift in schedule:
            schedule_data.append({
                "Date": shift.start_time.date(),
                "Start Time": shift.start_time.strftime("%H:%M"),
                "End Time": shift.end_time.strftime("%H:%M"),
                "Client": shift.client.name,
                "Agent": shift.agent.name
            })

        schedule_df = pd.DataFrame(schedule_data)
        st.dataframe(schedule_df)


if __name__ == "__main__":
    main()