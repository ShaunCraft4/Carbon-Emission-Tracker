import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import openai

openai.api_key = 'YOUR_OPENAI_KEY'  #Replace with your actual API key

def Inputs():
    vehicle_driven = vehicle_var.get()
    miles_driven = int(miles_entry.get())
    electricity_usage = int(electricity_entry.get())
    diet = diet_var.get()
    calorie_intake = int(calories_entry.get())
    return [miles_driven, electricity_usage, calorie_intake, vehicle_driven, diet]

def Output(I):
    #Electricity
    co2_electricity = (I[1] * 500) / 1000  #Unit of CF(500) is gCO2/mile
    if co2_electricity < 200:
        electricity_feedback = "Electricity: Good"
    elif co2_electricity <= 600:
        electricity_feedback = "Electricity: Average"
    else:
        electricity_feedback = "Electricity: Bad"

    #Calories
    diet = I[-1]
    if diet == "Plant":
        CF = 0.4 #Unit is gCo2/mile
    elif diet == "Mixed":
        CF = 0.75
    elif diet == "Meat":
        CF = 1.5
    co2_calorie = (I[2] * CF) / 1000  
    if co2_calorie < 1:
        calorie_feedback = "Calories: Good"
    elif co2_calorie <= 2.5:
        calorie_feedback = "Calories: Average"
    else:
        calorie_feedback = "Calories: Bad"

    #Miles
    vehicle_driven = I[-2]
    if vehicle_driven == "Electric":
        CF = 0.025  #Unit is kgCO2/mile
    elif vehicle_driven == "Gasoline":
        CF = 0.15  
    elif vehicle_driven == "Diesel":
        CF = 0.11  
    co2_miles = (I[0] * CF) #Already in kg
    if co2_miles < 20:
        miles_feedback = "Miles: Good"
    elif co2_miles <= 60:
        miles_feedback = "Miles: Average"
    else:
        miles_feedback = "Miles: Bad"

    advice_text.set("")
    result_text.set(f"{electricity_feedback}\n{calorie_feedback}\n{miles_feedback}\n"
                     f"Electricity CO2 Emissions (kg): {co2_electricity:.6f}\n"
                     f"Calories CO2 Emissions (kg): {co2_calorie:.6f}\n"
                     f"Miles CO2 Emissions (kg): {co2_miles:.6f}")

    return [co2_electricity, co2_calorie, co2_miles]

def Graphs(C):
    for widget in graph_frame.winfo_children():
        widget.destroy()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    #Pie Chart
    Values = np.array([C[0], C[1], C[2]])
    Labels = ["Electricity Usage", "Calorie Intake", "Miles Driven"]
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    axes[0].pie(Values, labels=Labels, autopct='%1.1f%%', startangle=140, colors=colors, shadow=True)
    axes[0].set_title('Carbon Emissions Breakdown')

    #Bar Graph
    Labels = ["Electricity Usage", "Calorie Intake", "Miles Driven"]
    bars = axes[1].bar(Labels, C, color=colors)
    for bar in bars:
        yval = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 6), ha='center', va='bottom', fontsize=10)
    axes[1].set_title('Carbon Emissions (kg CO2)')
    
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

def Advice(C):
    for widget in graph_frame.winfo_children():
        widget.destroy()
    
    prompt = f"What short and sweet advice can you give based on electricity CO2 emission of {C[0]} kg, Food calorie CO2 emission of {C[1]} kg and driving CO2 emission of {C[2]} kg?Please make sure to analyze each value properly and give a proper output that is short and consise for each emission. Within the output for each also mention how bad the CO2 emission is and how it can be overcome."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    result_text.set("")
    advice_text.set(response.choices[0].message['content'])

def calculate():
    advice_text.set("")
    I = Inputs()
    C = Output(I)
    Graphs(C)

def ask_advice():
    result_text.set("")
    I = Inputs()
    C = Output(I)
    Advice(C)

root = tk.Tk()
root.title("Carbon Footprint Tracker")
root.configure(bg='#f0f4f7')
root.attributes('-fullscreen', True)

frame = tk.Frame(root, bg='#ffffff', highlightbackground="#b3cde0", highlightthickness=2)
frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
title_label = tk.Label(frame, text="Carbon Footprint Tracker", bg='#ffffff', fg='#2a4d69', font=('Arial', 28, 'bold'))
title_label.pack(pady=(10, 20))
input_frame = tk.Frame(frame, bg='#ffffff')
input_frame.pack(pady=10)
tk.Label(input_frame, text="Vehicle Driven:", bg='#ffffff', fg='#4b86b4', font=('Arial', 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
vehicle_var = tk.StringVar(value="Electric")
tk.OptionMenu(input_frame, vehicle_var, "Electric", "Gasoline", "Diesel").grid(row=0, column=1, padx=10)
tk.Label(input_frame, text="Miles Driven:", bg='#ffffff', fg='#4b86b4', font=('Arial', 14)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
miles_entry = tk.Entry(input_frame, font=('Arial', 14))
miles_entry.grid(row=1, column=1, padx=10)
tk.Label(input_frame, text="Electricity Usage (kWh):", bg='#ffffff', fg='#4b86b4', font=('Arial', 14)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
electricity_entry = tk.Entry(input_frame, font=('Arial', 14))
electricity_entry.grid(row=2, column=1, padx=10)
tk.Label(input_frame, text="Diet Type:", bg='#ffffff', fg='#4b86b4', font=('Arial', 14)).grid(row=3, column=0, padx=10, pady=10, sticky="w")
diet_var = tk.StringVar(value="Plant")
tk.OptionMenu(input_frame, diet_var, "Plant", "Mixed", "Meat").grid(row=3, column=1, padx=10)
tk.Label(input_frame, text="Calorie Intake:", bg='#ffffff', fg='#4b86b4', font=('Arial', 14)).grid(row=4, column=0, padx=10, pady=10, sticky="w")
calories_entry = tk.Entry(input_frame, font=('Arial', 14))
calories_entry.grid(row=4, column=1, padx=10)
button_frame = tk.Frame(frame, bg='#ffffff')
button_frame.pack(pady=20)
calculate_button = tk.Button(button_frame, text="Calculate", command=calculate, bg='#2a4d69', fg='white', font=('Arial', 14), relief='raised', padx=10)
calculate_button.pack(side=tk.LEFT, padx=10)
advice_button = tk.Button(button_frame, text="Get Advice", command=ask_advice, bg='#b3cde0', fg='white', font=('Arial', 14), relief='raised', padx=10)
advice_button.pack(side=tk.LEFT, padx=10)
output_frame = tk.Frame(frame, bg='#ffffff')
output_frame.pack(pady=20)
result_text = tk.StringVar()
result_label = tk.Label(output_frame, textvariable=result_text, bg='#ffffff', fg='#00796b', font=('Arial', 16), justify="left")
result_label.pack()
advice_text = tk.StringVar()
advice_label = tk.Label(output_frame, textvariable=advice_text, bg='#ffffff', fg='#00796b', font=('Arial', 16), justify="left", wraplength=800)
advice_label.pack()
graph_frame = tk.Frame(frame, bg='#ffffff')
graph_frame.pack(pady=20)
exit_button = tk.Button(frame, text="X", command=root.destroy, bg='red', fg='white', font=('Arial', 14), width=3, relief='flat')
exit_button.place(relx=0.97, rely=0.02, anchor="ne")

root.mainloop()
