import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time


# Enhanced data models
class Agent:
    def __init__(self, id, name, skills, max_hours_per_week=40, max_consecutive_days=5):
        self.id = id
        self.name = name
        self.skills = skills
        self.max_hours_per_week = max_hours_per_week
        self.max_consecutive_days = max_consecutive_days
        self.scheduled_hours = 0
        self.consecutive_days = 0
        self.last_shift_end = None


class Client:
    def __init__(self, id, name, requirements, start_time, end_time, days_of_week, min_agents):
        self.id = id
        self.name = name
        self.requirements = requirements
        self.start_time = start_time
        self.end_time = end_time
        self.days_of_week = days_of_week
        self.min_agents = min_agents


class Shift:
    def __init__(self, client, start_time, end_time, agents=None):
        self.client = client
        self.start_time = start_time
        self.end_time = end_time
        self.agents = agents if agents else []


# Enhanced sample data generation
def generate_sample_data():
    agents = [
        Agent(1, "John Doe", ["general", "firefighting"], 40, 5),
        Agent(2, "Jane Smith", ["general", "driving"], 35, 4),
        Agent(3, "Mike Johnson", ["general"], 38, 6),
        Agent(4, "Emily Brown", ["general", "firefighting"], 42, 5),
        Agent(5, "Chris Wilson", ["general", "driving"], 37, 4)
    ]

    clients = [
        Client(1, "Office Building A", ["general"], time(9, 0), time(17, 0), [0, 1, 2, 3, 4], 1),
        Client(2, "Nightclub B", ["general", "firefighting"], time(22, 0), time(4, 0), [4, 5], 2),
        Client(3, "Residential Complex C", ["general", "driving"], time(0, 0), time(23, 59), [0, 1, 2, 3, 4, 5, 6], 1),
        Client(4, "Factory D", ["general", "firefighting"], time(6, 0), time(18, 0), [0, 1, 2, 3, 4], 2),
        Client(5, "Mall E", ["general"], time(10, 0), time(22, 0), [0, 1, 2, 3, 4, 5, 6], 1)
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
            shift_duration = (shift.end_time - shift.start_time).total_seconds() / 3600
            available_agents = [
                agent for agent in agents
                if set(shift.client.requirements).issubset(set(agent.skills))
                   and agent.scheduled_hours + shift_duration <= agent.max_hours_per_week
                   and (agent.last_shift_end is None or (
                            shift.start_time - agent.last_shift_end).total_seconds() / 3600 >= 8)
                   and agent.consecutive_days < agent.max_consecutive_days
            ]

            # Assign agents to the shift
            assigned_agents = []
            while len(assigned_agents) < shift.client.min_agents and available_agents:
                # Assign the agent with the least scheduled hours
                agent = min(available_agents, key=lambda a: a.scheduled_hours)
                assigned_agents.append(agent)
                available_agents.remove(agent)

                # Update agent's schedule
                agent.scheduled_hours += shift_duration
                agent.consecutive_days += 1
                agent.last_shift_end = shift.end_time

            shift.agents = assigned_agents
            schedule.append(shift)

        # Reset consecutive days for agents not working today
        for agent in agents:
            if agent not in [a for s in day_shifts for a in s.agents]:
                agent.consecutive_days = 0

        current_date += timedelta(days=1)

    return schedule


# Verification controls
def verify_schedule(schedule, agents, clients):
    issues = []

    # Check for unassigned shifts
    unassigned_shifts = [s for s in schedule if len(s.agents) < s.client.min_agents]
    if unassigned_shifts:
        issues.append(f"Found {len(unassigned_shifts)} shifts with insufficient agents assigned.")

    # Check for overworked agents
    for agent in agents:
        if agent.scheduled_hours > agent.max_hours_per_week:
            issues.append(
                f"{agent.name} is scheduled for {agent.scheduled_hours:.2f} hours, exceeding their max of {agent.max_hours_per_week}.")

    # Check for agents working too many consecutive days
    for agent in agents:
        if agent.consecutive_days > agent.max_consecutive_days:
            issues.append(
                f"{agent.name} is scheduled for {agent.consecutive_days} consecutive days, exceeding their max of {agent.max_consecutive_days}.")

    return issues


# Streamlit app
def main():
    st.title("Enhanced Security Company Scheduler POC")

    agents, clients = generate_sample_data()

    st.header("Client Requirements")
    client_data = [
        [c.name, ", ".join(c.requirements),
         c.start_time.strftime("%H:%M"), c.end_time.strftime("%H:%M"),
         ", ".join([["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][d] for d in c.days_of_week]),
         c.min_agents]
        for c in clients
    ]
    client_df = pd.DataFrame(client_data,
                             columns=["Client", "Requirements", "Start Time", "End Time", "Days", "Min Agents"])
    st.table(client_df)

    st.header("Agent Information")
    agent_data = [[a.name, ", ".join(a.skills), a.max_hours_per_week, a.max_consecutive_days] for a in agents]
    agent_df = pd.DataFrame(agent_data, columns=["Agent", "Skills", "Max Hours/Week", "Max Consecutive Days"])
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
             ", ".join([a.name for a in s.agents]) if s.agents else "Unassigned"]
            for s in schedule
        ]
        schedule_df = pd.DataFrame(schedule_data,
                                   columns=["Date & Start Time", "End Time", "Client", "Assigned Agents"])
        st.dataframe(schedule_df)

        st.header("Agent Workload Summary")
        workload_data = [[a.name, a.scheduled_hours, a.consecutive_days] for a in agents]
        workload_df = pd.DataFrame(workload_data, columns=["Agent", "Scheduled Hours", "Consecutive Days"])
        st.table(workload_df)

        st.header("Schedule Verification")
        issues = verify_schedule(schedule, agents, clients)
        if issues:
            st.warning("The following issues were found in the schedule:")
            for issue in issues:
                st.write(f"- {issue}")
        else:
            st.success("No issues found in the schedule.")

        st.header("Schedule Analytics")
        total_shifts = len(schedule)
        total_hours = sum(a.scheduled_hours for a in agents)
        avg_hours_per_agent = total_hours / len(agents)
        utilization_rate = total_hours / (len(agents) * agents[0].max_hours_per_week) * 100

        st.write(f"Total shifts scheduled: {total_shifts}")
        st.write(f"Total hours scheduled: {total_hours:.2f}")
        st.write(f"Average hours per agent: {avg_hours_per_agent:.2f}")
        st.write(f"Agent utilization rate: {utilization_rate:.2f}%")

        # Visualize agent workload distribution
        fig = px.bar(workload_df, x="Agent", y="Scheduled Hours", title="Agent Workload Distribution")
        st.plotly_chart(fig)


if __name__ == "__main__":
    main()