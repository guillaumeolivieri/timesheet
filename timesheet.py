import streamlit as st
import pandas as pd
import numpy as np
import random

def distribute_hours(hours):
    hours_list = list(hours)
    random.shuffle(hours_list)
    for i in range(len(hours_list)):
        hours_list[i] += random.uniform(-1, 1)
    return np.clip(np.array(hours_list), 0, np.inf)

def main():
    st.markdown("<h1 style='font-family: Arial; color: red;'>Timesheet generator</h1>", unsafe_allow_html=True)
    st.header("Enter Project Information")

    # Get project codes from user
    codes = st.text_input("Enter project codes separated by commas")
    project_codes = [code.strip() for code in codes.split(",")]

    # Get percentage of time spent on each project
    percents = []
    for code in project_codes:
        percent = st.slider(f"Level of effort this week on project {code}", 0, 100, 20, 5)
        percents.append(percent)

    # Confirm the user input
    if st.button("Confirm"):
        total_percent = sum(percents)
        if total_percent != 100:
            st.warning("Total percentage should be 100. The input values will be adjusted to match.")
            adjusted_percents = []
            for percent in percents:
                adjusted_percent = int(percent * 100 / total_percent)
                adjusted_percents.append(adjusted_percent)
            remaining_percent = 100 - sum(adjusted_percents)
            if remaining_percent > 0:
                adjusted_percents[0] += remaining_percent
            percents = adjusted_percents

        actual_percents = dict(zip(project_codes, percents))

        # Distribute the hours worked each week randomly, based on the actual percentages
        st.subheader("Hours worked on each project, each day:")
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        project_hours = {}
        for code, percent in actual_percents.items():
            hours = percent / 100 * 40
            day_hours = distribute_hours(np.array([hours/5]*5))
            project_hours[code] = day_hours
        
        #ensure that hours add up to 8
        for day in day_names:
            total_hours = sum([project_hours[code][day_names.index(day)] for code in project_codes])
            if total_hours != 8:
                for code in project_codes:
                    hours = project_hours[code][day_names.index(day)]
                    project_hours[code][day_names.index(day)] = hours * (8 / total_hours)
   
        total_hours_per_day = np.zeros(5)
        for code, hours in project_hours.items():
            total_hours_per_day += hours
        for i in range(5):
            if total_hours_per_day[i] != 8:
                excess_indices = np.where(total_hours_per_day > 8)[0]
                for code in project_hours:
                    excess_hours = total_hours_per_day[i] - 8
                    excess_hours_per_project = np.zeros(len(excess_indices))
                    for j in range(len(excess_indices)):
                        excess_hours_per_project[j] = max(0, project_hours[code][excess_indices[j]] - excess_hours/len(excess_indices))
                    excess_hours_per_project_sum = sum(excess_hours_per_project)
                    for j in range(len(excess_indices)):
                        if excess_hours_per_project_sum > excess_hours:
                            excess_hours_per_project[j] = excess_hours_per_project[j] - excess_hours_per_project_sum + excess_hours
                            excess_hours_per_project_sum = excess_hours
                        else:
                            excess_hours_per_project[j] = excess_hours_per_project[j] + (excess_hours - excess_hours_per_project_sum)/len(excess_indices)
                            excess_hours_per_project_sum = excess_hours
                    for j in range(len(excess_indices)):
                        project_hours[code][excess_indices[j]] = excess_hours_per_project[j]
        df = pd.DataFrame(project_hours, index=day_names, columns=project_codes)
        df_transposed = df.transpose()

        # Round the DataFrame after adding the missing hours
        df_rounded = df_transposed.round()

        # Display the timesheet
        st.dataframe(df_rounded)

if __name__ == "__main__":
    main()
