import os
import pathlib
import numpy as np
from opender import DER, DER_PV
import py_dss_interface
import data_export_plot

def data_processing(plot):
    # Obtaining the current directory
    current_dir = os.path.abspath(__file__)

    # Relative path to DER.txt file
    file_path = os.path.join(current_dir, '../docs/DER.txt')

    # Dictionary to store DER.txt values
    der_data = {}

    # Reading the DER.txt file
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split()  # Split line into key and value
            der_data[key] = convert_value(value)  # Convert and store in dictionary

    # Accessing corresponding variables
    simulation_time = der_data.get('simulation_time')
    number_steps = der_data.get('number_steps')
    pts_per_steps = der_data.get('pts_per_steps')
    DER = der_data.get('DER')
    bus = der_data.get('bus')
    V_rated = der_data.get('V_rated')
    line = der_data.get('line')
    control_mode = der_data.get('control_mode')
    S_rated = der_data.get('S_rated')
    PF_rated = der_data.get('PF_rated')
    CONST_Q = der_data.get('CONST_Q')
    normal_op_CAT = der_data.get('normal_op_CAT')
    abnormal_op_CAT = der_data.get('abnormal_op_CAT')

    if number_steps != 0:
        npts = pts_per_steps * number_steps
        aux = pts_per_steps
    else:
        npts = 24
        aux = 0

    S_rated = S_rated * 1E6
    P_rated = S_rated * PF_rated
    Q_rated = np.sqrt(S_rated ** 2 - P_rated ** 2)

    # Set maximum injection and absorption based on operation category
    if normal_op_CAT == 'B':
        max_inj = 0.44  # Maximum injection for Category B
        max_abs = 0.44  # Maximum absorption for Category B
    else:
        max_inj = 0.44  # Maximum injection for Category A
        max_abs = 0.25  # Maximum absorption for Category A

    # Create DER PV object with defined parameters
    der_obj = DER_PV(NP_VA_MAX=S_rated,
                     NP_P_MAX=S_rated,
                     NP_Q_MAX_INJ=S_rated*max_inj,
                     NP_Q_MAX_ABS=S_rated*max_abs)

    # Enable the selected control mode
    if control_mode == 'constant_pf':
        der_obj.der_file.CONST_PF_MODE_ENABLE = True
        der_obj.der_file.CONST_PF = PF_rated
        der_obj.der_file.CONST_PF_EXCITATION = 'INJ'
        title = 'Constant Power Factor Mode'
    elif control_mode == 'volt_var':
        der_obj.der_file.QV_MODE_ENABLE = True
        title = f'Voltage-Reactive Power Mode - CAT {normal_op_CAT}'
    elif control_mode == 'watt_var':
        der_obj.der_file.QP_MODE_ENABLE = True
        title = f'Active Power-Reactive Power Mode - CAT {normal_op_CAT}'
    elif control_mode == 'constant_var':
        der_obj.der_file.CONST_Q_MODE_ENABLE = True
        der_obj.der_file.CONST_Q = CONST_Q
        title = 'Constant Reactive Power Mode'
    elif control_mode == 'volt_watt':
        der_obj.der_file.PV_MODE_ENABLE = True
        title = 'Voltage-Active Power Mode'
    else:
        der_obj.der_file.PF_MODE_ENABLE = True
        title = 'Frequency-Active Power Mode'

    # Set DER nominal voltage
    der_obj.der_file.NP_AC_V_NOM = V_rated * 1000

    # Update DER inputs
    der_obj.update_der_input(f=60, p_dc_w=P_rated)
    der_obj.der_file.NP_NORMAL_OP_CAT = f'CAT_{normal_op_CAT}'
    der_obj.der_file.NP_ABNORMAL_OP_CAT = f'CAT_{abnormal_op_CAT}'

    # Run the OpenDSS feeder simulation
    if DER == 'True':
        feeder(simulation_time, number_steps, npts, bus, V_rated, line, S_rated,
               PF_rated, P_rated, Q_rated, der_obj, control_mode)

        if plot == True:
            data_export_plot.plotter_with_der(control_mode, title, der_obj, aux)
    else:
        feeder(simulation_time, number_steps, npts, bus, V_rated, line,
               None, None, None, None, None, None)

        if plot == True:
            data_export_plot.plotter_without_der(bus)

def feeder(simulation_time, number_steps, npts, bus, V_rated, line, S_rated, PF_rated, P_rated, Q_rated, der_obj, control_mode):
    # Prepare arrays for storing simulation results
    t_data = []
    vm_data = []
    va_data = []
    vb_data = []
    vc_data = []
    p_data = []
    q_data = []
    status_data = []
    i_data = []
    i_angle_data = []

    # Determine the path to the OpenDSS DSS file
    script_path = os.path.dirname(os.path.abspath(__file__))
    dss_file = pathlib.Path(script_path).joinpath("feeders", "8500-Node", "Master.dss")

    # Initialize the OpenDSS interface
    dss = py_dss_interface.DSS()
    dss.text(f'compile [{dss_file}]')  # Compile the DSS file

    # Add and configure various elements in the simulation
    dss.text('New Energymeter.m1 Line.ln5815900-1 1')  # Add an energy meter
    dss.text('batchedit capacitor..* enabled=no')      # Disable all capacitors
    dss.text('batchedit load..* mode=1')               # Set load mode
    dss.text('batchedit load..* vmaxpu=1.25')          # Set maximum voltage per unit for loads
    dss.text('batchedit load..* vminpu=0.75')          # Set minimum voltage per unit for loads
    dss.text('set maxiterations=100')                  # Set maximum iterations
    dss.text('set maxcontrolit=100')                    # Set maximum control iterations
    dss.text('AddBusMarker bus=l3104830 color=red size=8 code=15')  # Add a bus marker for visualization

    # Define performance and efficiency curves for the PV system
    dss.text('New XYCurve.PvsT npts=4 xarray=[0 25 75 100] yarray=[1.2 1 .8 .6]')
    dss.text('New XYCurve.Eff npts=4 xarray=[.1 .2 .4 1.0] yarray=[.86 .9 .93 .97]')

    if S_rated is not None:
        if number_steps == 0:
            # Configuration for dynamic simulation
            t_s = simulation_time
            DER.t_s = t_s

            # Define irradiance and temperature profiles
            dss.text('New Loadshape.Irrad npts=24 interval=1')
            dss.text('~ mult=[0 0 0 0 0 0 .1 .2 .3 .5 .8 .9 1 1 .99 .9 .7 .4 .1 0 0 0 0 0]')
            dss.text('New Tshape.Temp npts=24 interval=1')
            dss.text('~ temp=[25 25 25 25 25 25 25 25 35 40 45 50 60 60 55 40 35 30 25 25 25 25 25 25]')

            # Configure the PV system
            dss.text(f'New PVSystem.PV phases=3 bus1={bus} kV={V_rated} kva={S_rated / 1000} kvar={Q_rated / 1000} Pmpp={S_rated / 1000} PF={PF_rated / 1000}')
            dss.text("~ irradiance=0.98 %cutin=0.1 %cutout=0.1 effcurve=Eff P-TCurve=PvsT daily=Irrad Tdaily=Temp")

            # Add monitors for voltage and power
            dss.text('New Monitor.DER_voltage element=PVSystem.PV terminal=1 mode=0')
            dss.text('New Monitor.DER_power element=PVSystem.PV terminal=1 mode=1 ppolar=no')

            per_load = generate_output(-0.2, 24, 'list')
        else:
            # Configuration for dynamic simulation
            t_s = simulation_time / npts
            DER.t_s = t_s

            # Define irradiance and temperature profiles
            dss.text(f'New Loadshape.Irrad npts={npts} interval=1')
            Irrad = generate_output(1, npts, 'string')
            dss.text(f'~ mult=[{Irrad}]')
            dss.text(f'New Tshape.Temp npts={npts} interval=1')
            Temp = generate_output(25, npts, 'string')
            dss.text(f'~ temp=[{Temp}]')

            # Configure the PV system
            dss.text(f'New PVSystem.PV phases=3 bus1=l3104830 kV={V_rated} kva={S_rated / 1000} kvar={Q_rated / 1000} Pmpp={S_rated / 1000} PF={PF_rated / 1000}')
            dss.text("~ irradiance=0.98 %cutin=0.1 %cutout=0.1 effcurve=Eff P-TCurve=PvsT daily=Irrad Tdaily=Temp")

            # Add monitors for voltage and power
            dss.text('New Monitor.DER_voltage element=PVSystem.PV terminal=1 mode=0')
            dss.text('New Monitor.DER_power element=PVSystem.PV terminal=1 mode=1 ppolar=no')

            per_load = generate_numbers(0.5, -0.2, 1.2, number_steps, npts)  # Generate load data
    else:
        if number_steps == 0:
            t_s = simulation_time

            # Add a monitor for bus voltage
            dss.text(f'New Monitor.BUS_voltage element=LINE.{line} terminal=1 mode=0')

            per_load = generate_output(-0.2, 24, 'list')
        else:
            t_s = simulation_time / npts

            # Add a monitor for bus voltage
            dss.text(f'New Monitor.BUS_voltage element=LINE.{line} terminal=1 mode=0')

            per_load = generate_numbers(0.5, -0.2, 1.2, number_steps, npts)

    # Set simulation mode to daily and configure step size
    dss.text('set mode=daily')
    dss.text(f'set stepsize={t_s / 3600}h')
    dss.text('set number=1')

    if der_obj is not None:
        for i in range(npts):
            # Set load condition based on per_load data
            dss.text(f'set loadmult={per_load[i]}')

            # Solve the simulation
            dss.solution.solve()

            # Determine the active power based on control mode
            if number_steps != 0 and (der_obj.der_file.CONST_PF_MODE_ENABLE == True or der_obj.der_file.QP_MODE_ENABLE == True or der_obj.der_file.CONST_Q_MODE_ENABLE == True):
                if i < npts / 4:
                    per = 0.3
                elif i > npts * 3 / 4:
                    per = 0
                elif i < npts / 2:
                    per = 1
                else:
                    per = 0.6
                p_dc_w = P_rated * per  # Active power adjusted
            else:
                p_dc_w = P_rated  # Use rated power if no control mode is enabled

            # Retrieve monitoring data
            dss.monitors.first()
            V = [dss.monitors.channel(1), dss.monitors.channel(3), dss.monitors.channel(5)]
            Theta = [np.deg2rad(dss.monitors.channel(2)), np.deg2rad(dss.monitors.channel(4)), np.deg2rad(dss.monitors.channel(6))]

            dss.monitors.next()
            P = -np.array(dss.monitors.channel(1)) - np.array(dss.monitors.channel(3)) - np.array(dss.monitors.channel(5))
            Q = -np.array(dss.monitors.channel(2)) - np.array(dss.monitors.channel(4)) - np.array(dss.monitors.channel(6))

            # Update DER input with monitoring data
            der_obj.update_der_input(v=[V[0][i], V[1][i], V[2][i]],
                                     theta=[Theta[0][i], Theta[1][i], Theta[2][i]],
                                     p_dc_w=p_dc_w)
            der_obj.run()

            # Recover current from DER
            I, angle = der_obj.get_der_output('I_pu')

            # Update the PV system settings
            dss.pvsystems.pf = np.cos(np.arctan2(np.array(der_obj.q_out_pu), np.array(der_obj.p_out_pu)))  # Set power factor
            dss.pvsystems.kvar = der_obj.q_out_kvar  # Set reactive power

            # Save simulation results
            t_data.append(i * t_s)
            p_data.append(der_obj.p_out_pu)
            q_data.append(der_obj.q_out_pu)
            vm_data.append(der_obj.der_input.v_meas_pu)
            va_data.append(der_obj.der_input.v_a_pu)
            vb_data.append(der_obj.der_input.v_b_pu)
            vc_data.append(der_obj.der_input.v_c_pu)
            status_data.append(der_obj.der_status)
            i_data.append(I)
            i_angle_data.append(angle)

            # Plot feeder
            if i == (number_steps - 1):
                dss.text('Interpolate')
                dss.text('plot circuit Power max=2000 n n C1=$00FF0000')

        if number_steps == 0:
            # If number_steps is zero, compute results from steady-state simulation
            p_data = 1000 * P / S_rated
            q_data = 1000 * Q / S_rated

        # Export data to CSV
        data_export_plot.csv_data_with_der(t_data, p_data, q_data, vm_data, va_data, vb_data, vc_data,
                                           status_data, i_data, i_angle_data, control_mode)
    else:
        for i in range(npts):
            # Set load condition based on per_load data
            dss.text(f'set loadmult={per_load[i]}')

            # Solve the simulation
            dss.solution.solve()

            # Plot feeder
            if i == (number_steps - 1):
                dss.text('Interpolate')
                dss.text('plot circuit Power max=2000 n n C1=$00FF0000')

            # Save simulation results
            t_data.append(i * t_s)

        # Retrieve bus voltage data
        va_data = dss.monitors.channel(1)
        vb_data = dss.monitors.channel(3)
        vc_data = dss.monitors.channel(5)

        # Export data to CSV
        data_export_plot.csv_data_without_der(t_data, va_data, vb_data, vc_data, V_rated)

def convert_value(value):
    # Convert the value to an integer or float, or return it as a string if it cannot be converted
    try:
        if '.' in value:
            return float(value)  # Convert to float if decimal point is present
        else:
            return int(value)    # Convert to int if no decimal point
    except ValueError:
        return value  # Return as string if conversion fails

def generate_output(value, npts, output_type='string'):
    # Generate a list or string of a specified value repeated npts times
    numbers = [value] * npts

    if output_type == 'string':
        result = " ".join(map(str, numbers))
    elif output_type == 'list':
        result = numbers
    else:
        raise ValueError("output_type must be 'string' or 'list'")

    return result

def generate_numbers(start_val, min_val, max_val, number_steps, npts):
    # Generate a sequence of numbers between min_val and max_val, with specified number of steps
    pts_per_steps = npts / number_steps
    number_steps = number_steps + 1
    sequence_high = np.linspace(start_val, max_val, number_steps // 2)  # Generate high values
    sequence_low = np.linspace(sequence_high[0], min_val, number_steps // 2)  # Generate low values

    # Interleave high and low sequences
    sequence = np.empty((sequence_high.size + sequence_low.size,), dtype=sequence_high.dtype)
    sequence[0::2] = sequence_high
    sequence[1::2] = sequence_low

    # Append max_val if number_steps is odd
    if number_steps % 2:
        sequence = np.append(sequence, 1)

    result = np.concatenate([[i] * int(pts_per_steps) for i in sequence[1:]])

    return result
