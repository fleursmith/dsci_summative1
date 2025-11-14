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

# Build dataframe for graphs
algorithms_attendance = attendance[attendance["Module Name"] == "Algorithms"] 
algorithms_daily_attendance = algorithms_attendance.groupby('Date')['Attended'].mean().reset_index()
algorithms_daily_attendance["Attendance_Percent"] = algorithms_daily_attendance["Attended"] * 100

# UI
app_ui = ui.page_sidebar(
    ui.sidebar(),  # empty sidebar – nothing interactive yet
    ui.h1("Algorithms Attendance"),
    ui.card(
        ui.card_header("Average Attendance Over Time"),
        ui.output_plot("attendance_plot"),  # this will call the function below
    ),
)

# Server
def server(input, output, session):

    @output
    @render.plot
    def attendance_plot():
         # code from earlier to plot graphs
        # Plot the average attendance over time for the Algorithms module
        plt.figure(figsize=(14,6))  # make figure wider for side by side view

        # Line graph
        plt.subplot(1, 2, 1)  # first subplot (1 row, 2 columns, position 1)
        plt.plot(
            algorithms_daily_attendance["Date"],
            algorithms_daily_attendance["Attendance_Percent"],
            marker="o"
        )
        plt.title("Average Attendance Over Time (Algorithms Module)")
        plt.xlabel("Date")
        plt.ylabel("Average Attendance Rate (% of those invited)")
        plt.xticks(rotation=45)  # rotate x-axis labels for better readability
        plt.grid(True)  # gridlines for readability

        # Bar graph
        ax2 = plt.subplot(1, 2, 2)  # second subplot (1 row, 2 columns, position 2)
        plt.bar(
            algorithms_daily_attendance["Date"],
            algorithms_daily_attendance["Attendance_Percent"],
        )
        plt.xlabel("Date")
        plt.ylabel("Average Attendance Rate (% of those invited)")
        plt.title("Average Attendance (Bar Graph)")
        plt.xticks(rotation=45)  # rotate x-axis labels for better readability
        plt.grid(True, axis="y")  # gridlines for readability

        plt.tight_layout()  # prevent overlap
        return ax2

# app
app = App(app_ui, server)