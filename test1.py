import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta, date
import plotly.express as px


# (Previous code for Agent, Client, Shift classes, and generate_sample_data function remains the same)

def create_schedule(agents, clients, start_date, num_days):
    schedule = []
    current_date = start_date

    for _ in range(num_days):
        for client in clients:
            shift_start = datetime.combine(current_date, datetime.min.time()).replace(hour=20, minute=0)
            shift_end = (shift_start + timedelta(hours=10)).replace(hour=6, minute=0)

            available_agents = [agent for agent in agents if
                                set(client.requirements).issubset(set(agent.qualifications))]
            if available_agents:
                assigned_agent = random.choice(available_agents)
                shift = Shift(shift_start, shift_end, client, assigned_agent)
                schedule.append(shift)

        current_date += timedelta(days=1)

    return schedule


def create_gantt_chart(schedule):
    df = pd.DataFrame([
        dict(Task=f"{shift.client.name} - {shift.agent.name}",
             Start=shift.start_time,
             Finish=shift.end_time,
             Agent=shift.agent.name)
        for shift in schedule
    ])

    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Agent",
                      title="Security Company Schedule")
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(height=600)

    return fig


def main():
    st.title("Security Company Scheduler POC")

    agents, clients = generate_sample_data()

    st.header("Agents")
    agent_df = pd.DataFrame([(a.id, a.name, ", ".join(a.qualifications)) for a in agents],
                            columns=["ID", "Name", "Qualifications"])
    st.table(agent_df)

    st.header("Clients")
    client_df = pd.DataFrame([(c.id, c.name, ", ".join(c.requirements)) for c in clients],
                             columns=["ID", "Name", "Requirements"])
    st.table(client_df)

    st.header("Generate Schedule")
    start_date = st.date_input("Start Date", date.today())
    num_days = st.number_input("Number of Days", min_value=1, max_value=30, value=7)

    if st.button("Generate Schedule"):
        schedule = create_schedule(agents, clients, start_date, num_days)

        st.header("Generated Schedule")
        schedule_data = []
        for shift in schedule:
            schedule_data.append({
                "Date": shift.start_time.date(),
                "Start Time": shift.start_time.strftime("%H:%M"),
                "End Time": shift.end_time.strftime("%H:%M"),
                "Client": shift.client.name,
                "Agent": shift.agent.name if shift.agent else "Unassigned"
            })

        schedule_df = pd.DataFrame(schedule_data)
        st.table(schedule_df)

        st.header("Visual Timetable")
        fig = create_gantt_chart(schedule)
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()