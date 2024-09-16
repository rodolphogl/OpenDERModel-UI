import tkinter as tk
from tkinter import ttk
import os
import opender_opendss_integration

class SimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenDERModel UI")

        # Simulation Configuration
        self.simulation_frame = ttk.LabelFrame(root, text="Simulation Configuration", padding="10")
        self.simulation_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.sim_type_var = tk.StringVar(value='2')
        ttk.Label(self.simulation_frame, text="Simulation Type").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(self.simulation_frame, text="24-hour Simulation", variable=self.sim_type_var,
                        value='1', command=self.update_simulation_mode).grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(self.simulation_frame, text="Rectangular Voltage Pulses", variable=self.sim_type_var,
                        value='2', command=self.update_simulation_mode).grid(row=2, column=0, sticky="w")

        self.sim_time_entry = ttk.Entry(self.simulation_frame, width=15)
        self.sim_time_entry.insert(0, '90')
        self.sim_time_entry.grid(row=3, column=1, sticky="w")
        ttk.Label(self.simulation_frame, text="Total Simulation Time (s):").grid(row=3, column=0, sticky="w")

        self.steps_entry = ttk.Entry(self.simulation_frame, width=15)
        self.steps_entry.insert(0, '7')
        self.steps_entry.grid(row=4, column=1, sticky="w")
        ttk.Label(self.simulation_frame, text="Number of Steps:").grid(row=4, column=0, sticky="w")

        self.points_entry = ttk.Entry(self.simulation_frame, width=15)
        self.points_entry.insert(0, '30')
        self.points_entry.grid(row=5, column=1, sticky="w")
        ttk.Label(self.simulation_frame, text="Points per Step:").grid(row=5, column=0, sticky="w")

        # DER Configuration
        self.der_frame = ttk.LabelFrame(root, text="DER Configuration", padding="10")
        self.der_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.use_der_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.der_frame, text="Use DER", variable=self.use_der_var,
                        command=self.toggle_der_config).grid(row=0, column=0, sticky="w")

        ################################################################################################################

        # Feeder Data
        ttk.Label(self.der_frame, text="DER Bus").grid(row=1, column=0, sticky="w")
        self.bus_entry = ttk.Entry(self.der_frame, width=15)
        self.bus_entry.insert(0, 'l3104830')
        self.bus_entry.grid(row=2, column=0, sticky="w")

        ttk.Label(self.der_frame, text="Rated Voltage (kV)").grid(row=1, column=1, sticky="w")
        self.v_rated_entry = ttk.Entry(self.der_frame, width=15)
        self.v_rated_entry.insert(0, '12.47')
        self.v_rated_entry.grid(row=2, column=1, sticky="w")

        ttk.Label(self.der_frame, text="Downstream Line to Bus").grid(row=1, column=2, sticky="w")
        self.line_entry = ttk.Entry(self.der_frame, width=15)
        self.line_entry.insert(0, 'LN5563901-2')
        self.line_entry.grid(row=2, column=2, sticky="w")

        ttk.Label(self.der_frame, text="DER Control Mode").grid(row=3, column=0, columnspan=3, sticky="ew")

        # Create a combobox with control modes
        # Dictionary to map displayed options to internal values
        self.der_mode_mapping = {
            "Constant Power Factor": "constant_pf",
            "Voltage-Reactive Power (Volt-VAr)": "volt_var",
            "Active Power-Reactive Power (Watt-VAr)": "watt_var",
            "Constant Reactive Power": "constant_var",
            "Voltage-Active Power (Volt-Watt)": "volt_watt"
        }

        # Combobox with user-visible values
        self.der_mode_combobox = ttk.Combobox(self.der_frame, values=list(self.der_mode_mapping.keys()),
                                              state="readonly")
        self.der_mode_combobox.grid(row=4, column=0, columnspan=3, sticky="ew")
        self.der_mode_combobox.set("Constant Power Factor")

        # PVSystem Data
        ttk.Label(self.der_frame, text="Apparent Power (MVA)").grid(row=5, column=0, sticky="w")
        self.s_rated_entry = ttk.Entry(self.der_frame, width=15)
        self.s_rated_entry.insert(0, '2')
        self.s_rated_entry.grid(row=6, column=0, sticky="w")

        ttk.Label(self.der_frame, text="Power Factor").grid(row=5, column=1, sticky="w")
        self.pf_rated_entry = ttk.Entry(self.der_frame, width=15)
        self.pf_rated_entry.insert(0, '0.92')
        self.pf_rated_entry.grid(row=6, column=1, sticky="w")

        ttk.Label(self.der_frame, text="Constant Reactive Power").grid(row=5, column=2, sticky="w")
        self.q_constant_entry = ttk.Entry(self.der_frame, width=15)
        self.q_constant_entry.insert(0, '0.3')
        self.q_constant_entry.grid(row=6, column=2, sticky="w")

        # Normal operating performance category
        self.cat_normal = tk.StringVar(value='B')
        ttk.Label(self.der_frame, text="Normal Operating Performance Category").grid(row=7, column=0, columnspan=3,
                                                                                     sticky="ew")
        self.cat_normal_a = ttk.Radiobutton(self.der_frame, text="Category A", variable=self.cat_normal, value='A')
        self.cat_normal_a.grid(row=8, column=0, sticky="w")
        self.cat_normal_b = ttk.Radiobutton(self.der_frame, text="Category B", variable=self.cat_normal, value='B')
        self.cat_normal_b.grid(row=8, column=1, sticky="w")

        # Abnormal operating performance category
        self.cat_abnormal = tk.StringVar(value='III')
        ttk.Label(self.der_frame, text="Abnormal Operating Performance Category").grid(row=9, column=0, columnspan=3,
                                                                                       sticky="ew")
        self.cat_abnormal_1 = ttk.Radiobutton(self.der_frame, text="Category I", variable=self.cat_abnormal, value='I')
        self.cat_abnormal_1.grid(row=10, column=0, sticky="w")
        self.cat_abnormal_2 = ttk.Radiobutton(self.der_frame, text="Category II", variable=self.cat_abnormal,
                                              value='II')
        self.cat_abnormal_2.grid(row=10, column=1, sticky="w")
        self.cat_abnormal_3 = ttk.Radiobutton(self.der_frame, text="Category III", variable=self.cat_abnormal,
                                              value='III')
        self.cat_abnormal_3.grid(row=10, column=2, sticky="w")

        # Updates the state of the Radiobuttons based on DER configuration
        self.update_radiobuttons_state()

        # Configure column weights for expanding
        self.der_frame.grid_columnconfigure(0, weight=1, minsize=150)  # Sets minimum width
        self.der_frame.grid_columnconfigure(1, weight=1, minsize=150)  # Sets minimum width
        self.der_frame.grid_columnconfigure(2, weight=1, minsize=150)  # Sets minimum width

        ################################################################################################################

        # Buttons
        self.plot_button = ttk.Button(root, text="Plot Graphs", command=self.plot_graphs)
        self.plot_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.export_button = ttk.Button(root, text="Export Data", command=self.export_csv)
        self.export_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        # Initialize variables
        self.der_enabled = True
        self.configure_der()

    # Function to access the internal value instead of the displayed text
    def get_der_mode_value(self):
        displayed_value = self.der_mode_combobox.get()  # Gets the displayed value in the combobox
        return self.der_mode_mapping[displayed_value]  # Returns the associated internal value

    def update_simulation_mode(self):
        # Enable or disable widgets based on the selected simulation mode
        if self.sim_type_var.get() == '2':
            # If the simulation mode is "Rectangular Voltage Pulses", disable widgets related to time and steps
            self.sim_time_entry.config(state='normal')
            self.steps_entry.config(state='normal')
            self.points_entry.config(state='normal')
        else:
            # If the simulation mode is "24-hour Simulation", disable widgets
            self.sim_time_entry.config(state='disabled')
            self.steps_entry.config(state='disabled')
            self.points_entry.config(state='disabled')

    def toggle_der_config(self):
        # Enable or disable DER configuration based on the Checkbutton state
        if self.use_der_var.get():
            self.configure_der()
        else:
            self.disable_der()

        # Updates the state of the Radiobuttons
        self.update_radiobuttons_state()

    def update_radiobuttons_state(self):
        state = 'normal' if self.use_der_var.get() else 'disabled'
        for rb in [self.cat_normal_a, self.cat_normal_b, self.cat_abnormal_1, self.cat_abnormal_2, self.cat_abnormal_3]:
            rb.config(state=state)

    def configure_der(self):
        # Enables all DER-related widgets
        self.der_mode_combobox.config(state='normal')
        self.s_rated_entry.config(state='normal')
        self.pf_rated_entry.config(state='normal')
        self.q_constant_entry.config(state='normal')

        # Binds the Combobox selection event to the update method
        self.der_mode_combobox.bind("<<ComboboxSelected>>", self.update_der_mode)

        # Updates the state of the reactive power field
        self.update_der_mode(None)

    def disable_der(self):
        # Disables all DER-related widgets
        self.der_mode_combobox.config(state='disabled')
        self.s_rated_entry.config(state='disabled')
        self.pf_rated_entry.config(state='disabled')
        self.q_constant_entry.config(state='disabled')

        # Unbinds the Combobox selection event
        self.der_mode_combobox.unbind("<<ComboboxSelected>>")

    def update_der_mode(self, event):
        selected_mode = self.der_mode_combobox.get()
        if selected_mode == "Constant Reactive Power":
            self.q_constant_entry.config(state='normal')
        else:
            self.q_constant_entry.config(state='disabled')

    def plot_graphs(self):
        # Function to save the DER configuration to a txt file
        self.save_der_config()

        # Function to plot graphs
        opender_opendss_integration.data_processing(True)
        pass

    def export_csv(self):
        # Function to save the DER configuration to a txt file
        self.save_der_config()

        # Function to export data to CSV
        opender_opendss_integration.data_processing(False)
        pass

    def save_der_config(self):
        # Path to the 'docs' directory
        docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs')

        # Create the directory if it does not exist
        os.makedirs(docs_dir, exist_ok=True)

        # Full path to the DER.txt file
        file_path = os.path.join(docs_dir, 'DER.txt')

        # Write variables to the DER.txt file
        with open(file_path, 'w') as f:
            if self.sim_type_var.get() == '1':
                f.write(f"simulation_time 3600\n")
                f.write(f"number_steps 0\n")
            else:
                f.write(f"simulation_time {self.sim_time_entry.get()}\n")
                f.write(f"number_steps {self.steps_entry.get()}\n")
            f.write(f"pts_per_steps {self.points_entry.get()}\n")
            f.write(f"DER {self.use_der_var.get()}\n")
            f.write(f"bus {self.bus_entry.get()}\n")
            f.write(f"V_rated {self.v_rated_entry.get()}\n")
            f.write(f"line {self.line_entry.get()}\n")
            f.write(f"control_mode {self.get_der_mode_value()}\n")
            f.write(f"S_rated {self.s_rated_entry.get()}\n")
            f.write(f"PF_rated {self.pf_rated_entry.get()}\n")
            f.write(f"CONST_Q {self.q_constant_entry.get()}\n")
            f.write(f"normal_op_CAT {self.cat_normal.get()}\n")
            f.write(f"abnormal_op_CAT {self.cat_abnormal.get()}\n")

        print(f"File saved at: {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimulationApp(root)
    root.mainloop()
