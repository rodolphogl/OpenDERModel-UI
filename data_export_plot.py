import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from tkinter import Label, Entry, Button, Toplevel

def csv_data_without_der(t_data, va_data, vb_data, vc_data, V_rated):
    # Normalize voltage data by the rated voltage
    va_data = va_data / (V_rated * 1E3 / np.sqrt(3))
    vb_data = vb_data / (V_rated * 1E3 / np.sqrt(3))
    vc_data = vc_data / (V_rated * 1E3 / np.sqrt(3))
    # Calculate the mean voltage magnitude
    vm_data = np.mean([va_data, vb_data, vc_data], axis=0)

    # Create a DataFrame with the data
    data = {
        'Time (s)': t_data,
        'Va (pu)': va_data,
        'Vb (pu)': vb_data,
        'Vc (pu)': vc_data,
        'Vm (pu)': vm_data
    }

    df = pd.DataFrame(data)

    # Path to the directory two levels up from the current folder
    two_levels_up = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    docs_dir = os.path.join(two_levels_up, 'docs')  # Path to the 'docs' folder two levels up

    # Check if the 'docs' folder exists; if not, create it
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)

    # Full path to the CSV file
    csv_path = os.path.join(docs_dir, 'data_without_DER.csv')

    # Export the DataFrame to the CSV file in the 'docs' directory
    df.to_csv(csv_path, index=False)

    print(f"File saved at: {csv_path}")

def csv_data_with_der(t_data, p_data, q_data, vm_data, va_data, vb_data, vc_data, status_data, i_data, i_angle_data, control_mode):
    # Extract current and angle data
    ia_data = [sublist[0] for sublist in i_data]
    ib_data = [sublist[1] for sublist in i_data]
    ic_data = [sublist[2] for sublist in i_data]

    ia_angle_data = [sublist[0] for sublist in i_angle_data]
    ib_angle_data = [sublist[1] for sublist in i_angle_data]
    ic_angle_data = [sublist[2] for sublist in i_angle_data]

    # Calculate power factor
    pf_data = np.cos(np.arctan2(np.array(q_data), np.array(p_data)))

    # Create a DataFrame with the data
    data = {
        'Time (s)': t_data,
        'Va (pu)': va_data,
        'Vb (pu)': vb_data,
        'Vc (pu)': vc_data,
        'Vm (pu)': vm_data,
        'P (pu)': p_data,
        'Q (pu)': q_data,
        'PF': pf_data,
        'Ia (pu)': ia_data,
        'Ib (pu)': ib_data,
        'Ic (pu)': ic_data,
        'Ia Angle (rad)': ia_angle_data,
        'Ib Angle (rad)': ib_angle_data,
        'Ic Angle (rad)': ic_angle_data,
        'Status': status_data
    }

    df = pd.DataFrame(data)

    # Path to the directory two levels up from the current folder
    two_levels_up = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    docs_dir = os.path.join(two_levels_up, 'docs')  # Path to the 'docs' folder two levels up

    # Check if the 'docs' folder exists; if not, create it
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)

    # Full path to the CSV file
    csv_path = os.path.join(docs_dir, f'data_{control_mode}.csv')

    # Export the DataFrame to the CSV file in the 'docs' directory
    df.to_csv(csv_path, index=False)

    print(f"File saved at: {csv_path}")

def plotter_without_der(bus):
    # Get the current directory
    current_dir = os.path.abspath(__file__)

    # Path to the CSV file (adjust as needed)
    csv_path = os.path.join(current_dir, f'../docs/data_without_der.csv')

    # Read the CSV file
    data = pd.read_csv(csv_path)

    plt.figure()
    plt.clf()
    plt.plot(data['Time (s)'], data['Va (pu)'], label='Va')
    plt.plot(data['Time (s)'], data['Vb (pu)'], label='Vb')
    plt.plot(data['Time (s)'], data['Vc (pu)'], label='Vc')
    plt.plot(data['Time (s)'], data['Vm (pu)'], label='V Mean')
    plt.tick_params(axis='x', labelsize=16)
    plt.tick_params(axis='y', labelsize=16)
    plt.grid(True)
    plt.legend(fontsize=12)
    plt.ylabel('Voltage (pu)', fontsize=22)
    plt.xlabel('Time (s)', fontsize=22)
    # Overall figure title
    plt.suptitle(f'Voltage at Bus {bus}', fontsize=20, fontweight='bold')
    plt.show()

def plotter_with_der(control_mode, title, der_obj, aux):
    # Get the current directory
    current_dir = os.path.abspath(__file__)

    # Path to the CSV file (adjust as needed)
    csv_path = os.path.join(current_dir, f'../docs/data_{control_mode}.csv')

    # Read the CSV file
    data = pd.read_csv(csv_path)

    # Create a figure and axes with subplots in 2 columns
    fig, axs = plt.subplots(3, 2, figsize=(15, 20), sharex='col')
    fig.tight_layout(pad=3.0)

    # Enable grid for all subplots
    for ax in axs.flat:
        ax.grid(True)

    # First column - Voltages and Currents
    axs[0, 0].plot(data['Time (s)'], data['Va (pu)'], label='Va')
    axs[0, 0].plot(data['Time (s)'], data['Vb (pu)'], label='Vb')
    axs[0, 0].plot(data['Time (s)'], data['Vc (pu)'], label='Vc')
    axs[0, 0].plot(data['Time (s)'], data['Vm (pu)'], label='V Mean')
    axs[0, 0].set_ylabel('Voltage (pu)', fontsize=16)
    axs[0, 0].legend(fontsize=11)
    axs[0, 0].tick_params(axis='x', length=20)
    axs[0, 0].tick_params(axis='y', labelsize=12)

    axs[1, 0].plot(data['Time (s)'], data['Ia (pu)'], label='Ia')
    axs[1, 0].plot(data['Time (s)'], data['Ib (pu)'], label='Ib')
    axs[1, 0].plot(data['Time (s)'], data['Ic (pu)'], label='Ic')
    axs[1, 0].set_ylabel('Current (pu)', fontsize=16)
    axs[1, 0].legend(fontsize=11)
    axs[1, 0].tick_params(axis='x', length=20)
    axs[1, 0].tick_params(axis='y', labelsize=12)

    axs[2, 0].plot(data['Time (s)'], data['Ia Angle (rad)'], label='Ia Angle')
    axs[2, 0].plot(data['Time (s)'], data['Ib Angle (rad)'], label='Ib Angle')
    axs[2, 0].plot(data['Time (s)'], data['Ic Angle (rad)'], label='Ic Angle')
    axs[2, 0].set_xlabel('Time (s)', fontsize=16)
    axs[2, 0].set_ylabel('Current Angle (rad)', fontsize=16)
    axs[2, 0].legend(fontsize=11)
    axs[2, 0].tick_params(axis='x', labelsize=12)
    axs[2, 0].tick_params(axis='y', labelsize=12)

    # Second column - Power, PF, P, Q, and Status
    # Create two y-axes on the same subplot for Active Power (P) and Reactive Power (Q)
    ax1 = axs[0, 1]
    ax2 = ax1.twinx()
    # Plot P and Q on the primary axis (ax1) and Q on the secondary axis (ax2)
    ax1.plot(data['Time (s)'], data['P (pu)'], label='Active Power')
    ax2.plot(data['Time (s)'], data['Q (pu)'], color='#ff7f0e', label='Reactive Power')
    ax1.set_ylabel('Active Power (pu)', fontsize=16)  # Active Power with left axis
    ax2.set_ylabel('Reactive Power (pu)', fontsize=16)  # Reactive Power with right axis
    # Combine legends from both axes
    lines = ax1.get_lines() + ax2.get_lines()
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, fontsize=11)
    axs[0, 1].tick_params(axis='x', length=20)
    ax1.tick_params(axis='y', labelsize=12)
    ax2.tick_params(axis='y', labelsize=12)

    axs[1, 1].plot(data['Time (s)'], data['PF'])
    axs[1, 1].set_ylabel('Power Factor', fontsize=16)
    axs[1, 1].tick_params(axis='x', length=20)
    axs[1, 1].tick_params(axis='y', labelsize=12)

    axs[2, 1].plot(data['Time (s)'], [s.replace(" ", "\n") for s in data['Status']], label='Status')
    axs[2, 1].set_xlabel('Time (s)', fontsize=16)
    axs[2, 1].legend(fontsize=11)
    axs[2, 1].tick_params(axis='x', labelsize=12)
    axs[2, 1].tick_params(axis='y', labelsize=12)

    # Overall figure title
    fig.suptitle(title, fontsize=20, fontweight='bold')

    # Adjust spacing between plots
    plt.subplots_adjust(left=0.05,
                        bottom=0.055,
                        right=0.95,
                        top=0.93,
                        wspace=0.16,
                        hspace=0.06)

    # Function to create a window with fields to adjust y-axis limits
    def create_adjust_window():
        # Tkinter main window
        adjust_window = Toplevel()
        adjust_window.title("Adjust Axis Limits")

        # Current limits
        current_lim_ax1 = ax1.get_ylim()
        current_lim_ax2 = ax2.get_ylim()

        # Labels and entries for the y-axis limits of ax1 (Active Power)
        Label(adjust_window, text="Active Power (Y1)").grid(row=0, column=0, padx=10, pady=5)
        Label(adjust_window, text="Min:").grid(row=1, column=0, padx=10, pady=5)
        y1_min_entry = Entry(adjust_window)
        y1_min_entry.grid(row=1, column=1, padx=10, pady=5)
        y1_min_entry.insert(0, str(current_lim_ax1[0]))

        Label(adjust_window, text="Max:").grid(row=2, column=0, padx=10, pady=5)
        y1_max_entry = Entry(adjust_window)
        y1_max_entry.grid(row=2, column=1, padx=10, pady=5)
        y1_max_entry.insert(0, str(current_lim_ax1[1]))

        # Labels and entries for the y-axis limits of ax2 (Reactive Power)
        Label(adjust_window, text="Reactive Power (Y2)").grid(row=3, column=0, padx=10, pady=5)
        Label(adjust_window, text="Min:").grid(row=4, column=0, padx=10, pady=5)
        y2_min_entry = Entry(adjust_window)
        y2_min_entry.grid(row=4, column=1, padx=10, pady=5)
        y2_min_entry.insert(0, str(current_lim_ax2[0]))

        Label(adjust_window, text="Max:").grid(row=5, column=0, padx=10, pady=5)
        y2_max_entry = Entry(adjust_window)
        y2_max_entry.grid(row=5, column=1, padx=10, pady=5)
        y2_max_entry.insert(0, str(current_lim_ax2[1]))

        # Function to apply the new limits
        def apply_limits():
            try:
                # Read the values entered by the user and apply to the axes
                y1_min = float(y1_min_entry.get())
                y1_max = float(y1_max_entry.get())
                y2_min = float(y2_min_entry.get())
                y2_max = float(y2_max_entry.get())

                ax1.set_ylim([y1_min, y1_max])
                ax2.set_ylim([y2_min, y2_max])

                # Redraw the figure after changing the limits
                fig.canvas.draw()

                # Close the adjust window
                adjust_window.destroy()
            except ValueError:
                # Handle invalid entries if necessary
                pass

        # Button to apply the new limits
        apply_button = Button(adjust_window, text="Apply", command=apply_limits)
        apply_button.grid(row=6, column=0, columnspan=2, pady=10)

    # Function to detect the pressed key and open the adjust window
    def on_key(event):
        if event.key == 'o':  # Key 'o' to open the adjust window
            create_adjust_window()

    # Connect the key event to the function
    fig.canvas.mpl_connect('key_press_event', on_key)

    # Plot configuration based on DER control mode
    if control_mode == 'volt_var' and aux != 0:
        # Volt-var curve data
        v_curve = np.array([0.88,
                            der_obj.der_file.QV_CURVE_V1,
                            der_obj.der_file.QV_CURVE_V2,
                            der_obj.der_file.QV_CURVE_V3,
                            der_obj.der_file.QV_CURVE_V4,
                            1.12])
        q_curve = np.array([der_obj.der_file.QV_CURVE_Q1,
                            der_obj.der_file.QV_CURVE_Q1,
                            der_obj.der_file.QV_CURVE_Q2,
                            der_obj.der_file.QV_CURVE_Q3,
                            der_obj.der_file.QV_CURVE_Q4,
                            der_obj.der_file.QV_CURVE_Q4])

        # Plot Volt-var curve
        plt.figure()
        plt.clf()
        plt.title('Volt-var')
        plt.plot(v_curve, q_curve, color='red', label='Volt-var curve')
        plt.scatter(np.sort(data['Vm (pu)'][(aux-1)::aux]), np.sort(data['Q (pu)'][(aux-1)::aux])[::-1], marker='^', s=60, color='blue')
        plt.grid()
        plt.legend()
        plt.xlabel('Voltage (pu)')
        plt.ylabel('Q_out (pu)')
        plt.tight_layout()

    elif control_mode == 'watt_var' and aux != 0:
        # Watt-var curve data
        p_curve = np.array([der_obj.der_file.QP_CURVE_P3_LOAD,
                            der_obj.der_file.QP_CURVE_P2_LOAD,
                            der_obj.der_file.QP_CURVE_P1_LOAD,
                            der_obj.der_file.QP_CURVE_P1_GEN,
                            der_obj.der_file.QP_CURVE_P2_GEN,
                            der_obj.der_file.QP_CURVE_P3_GEN])
        q_curve = np.array([der_obj.der_file.QP_CURVE_Q3_LOAD,
                            der_obj.der_file.QP_CURVE_Q2_LOAD,
                            der_obj.der_file.QP_CURVE_Q1_LOAD,
                            der_obj.der_file.QP_CURVE_Q1_GEN,
                            der_obj.der_file.QP_CURVE_Q2_GEN,
                            der_obj.der_file.QP_CURVE_Q3_GEN])

        # Plot Watt-var curve
        plt.figure()
        plt.clf()
        plt.title('Watt-var')
        plt.plot(p_curve, q_curve, color='red', label='Watt-var curve')
        plt.scatter(np.sort(data['P (pu)'][51::52]), np.sort(data['Q (pu)'][51::52])[::-1], marker='^', s=60, color='blue')
        plt.grid()
        plt.legend()
        plt.xlabel('P_out (pu)')
        plt.ylabel('Q_out (pu)')
        plt.tight_layout()

    elif control_mode == 'volt_watt' and aux != 0:
        # Volt-watt curve data
        v_curve = np.array([0.82,
                            der_obj.der_file.PV_CURVE_V1,
                            der_obj.der_file.PV_CURVE_V2,
                            1.12])
        p_curve = np.array([der_obj.der_file.PV_CURVE_P1,
                            der_obj.der_file.PV_CURVE_P1,
                            der_obj.der_file.PV_CURVE_P2,
                            der_obj.der_file.PV_CURVE_P2])

        # Plot Volt-watt curve
        plt.figure()
        plt.clf()
        plt.title('Volt-watt')
        plt.plot(v_curve, p_curve, color='red', label='Volt-watt curve')
        plt.scatter(np.sort(data['Vm (pu)'][(aux-1)::aux]), np.sort(data['P (pu)'][(aux-1)::aux])[::-1], marker='^', s=60, color='blue')
        plt.grid()
        plt.legend()
        plt.xlabel('Voltage (pu)')
        plt.ylabel('P_out (pu)')
        plt.tight_layout()

    plt.show()