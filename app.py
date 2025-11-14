import pandas as pd
import matplotlib.pyplot as plt
from shiny import App, render, ui, reactive

# Load the dataset
attendance = pd.read_csv('attendance_anonymised-1.csv')

# Data Cleaning

# Set "Planned End Date" as an unnecessary column to be removed 
unnecessary_cols = ["Planned End Date"]

# Remove columns that are not necessary
attendance.drop(columns=unnecessary_cols, inplace=True)

# Rename columns
attendance.rename(columns={

    'Person Code' : 'Person Code',
    'Unit Instance Code' : 'Module Code',
    'Calocc Code' : 'Year',
    'Surname' : 'Surname',
    'Forename' : 'Forename',
    'Long Description' : 'Module Name',
    'Register Event ID' : 'Event ID',
    'Object ID' : 'Object ID',
    'Register Event Slot ID' : 'Event Slot ID',
    'Planned Start Date' : 'Date',
    'is Positive' : 'Has Attended',
    'Postive Marks' : 'Attended',
    'Negative Marks' : 'Not Attended',
    'Usage Code' : 'Attendance Code'

}, inplace=True)

# Convert the 'Date' column from object dtype to datetime format
attendance['Date'] = pd.to_datetime(attendance['Date'])

# Build choices for the dropdown: unique module names
module_choices = sorted(attendance["Module Name"].unique())

# Build dataframe for graphs
algorithms_attendance = attendance[attendance["Module Name"] == "Algorithms"] 
algorithms_daily_attendance = algorithms_attendance.groupby('Date')['Attended'].mean().reset_index()
algorithms_daily_attendance["Attendance_Percent"] = algorithms_daily_attendance["Attended"] * 100

# UI
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select(
            "module",
            "Select module",
            choices=module_choices,
            selected="Algorithms",  # default selection
        )
    ),
    ui.h1("Module Attendance"),
    ui.card(
        ui.card_header("Average Attendance Over Time"),
        ui.output_plot("attendance_plot"),
        style="width: 100%; height: 1250px;"
    ),
)

# Server
def server(input, output, session):

    @reactive.Calc
    def module_daily_attendance():
        # Get selected module
        module_name = input.module()

        # Filter data
        module_attendance = attendance[attendance["Module Name"] == module_name]

        # Group and convert to percent
        df = module_attendance.groupby("Date")["Attended"].mean().reset_index()
        df["Attendance_Percent"] = df["Attended"] * 100
        return df

    @output
    @render.plot
    def attendance_plot():
        # get reactive df
        df = module_daily_attendance()

        plt.figure(figsize=(10, 12))

        # Line graph
        plt.subplot(2, 1, 1)
        plt.plot(
            df["Date"],
            df["Attendance_Percent"],
            marker="o"
        )
        plt.title(f"Average Attendance Over Time\n{input.module()} Module")
        plt.xlabel("Date")
        plt.ylabel("Attendance Rate (% of those invited)")
        plt.xticks(rotation=45)
        plt.grid(True)

        # Bar graph
        ax2 = plt.subplot(2, 1, 2)
        plt.bar(df["Date"], df["Attendance_Percent"])
        plt.xlabel("Date")
        plt.ylabel("Attendance Rate (% of those invited)")
        plt.title(f"Average Attendance\n{input.module()} Module")
        plt.xticks(rotation=45)
        plt.grid(True, axis="y")
        # Give extra space at the bottom for x-axis labels
        fig = plt.gcf()
        fig.subplots_adjust(bottom=0.25, hspace=0.4)
        return ax2
    
# app
app = App(app_ui, server)