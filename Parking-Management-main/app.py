from flask import Flask, render_template, jsonify, request
import serial
import time
import csv

app = Flask(__name__)

entry_times = [None, None, None]
exit_times = [None, None, None]
previous_status = [None, None, None]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parking_lot.html')
def parking_lot():
    return render_template('parking_lot.html')

@app.route('/parking_data')
def parking_data():
    global entry_times, exit_times, previous_status
    cost_per_unit_second = float(request.args.get('costPerUnitSecond', 0))
    try:
        # Open the serial port
        ser = serial.Serial('COM6', 9600, timeout=2)
        print("COM port accessed successfully")

        # Read CSV data from the serial port
        csv_data = ser.readline().decode().strip()
        ser.close()

        print(f"CSV Data: {csv_data}")

        # Parse the received CSV data
        data = csv_data.split(',')
        num_cars = int(data[0])
        slots_status = [int(status) for status in data[1:4]]

        # Initialize elapsed times and costs list
        elapsed_times = [None, None, None]
        costs = [None, None, None]

        # Initialize previous status if it's the first run
        if previous_status[0] is None:
            previous_status = slots_status[:]

        # Check for slot status changes and update entry/exit times
        for i, status in enumerate(slots_status):
            if status == 0 and previous_status[i] == 1:  # Car entered
                entry_times[i] = time.time()
                print(f"Car entered slot {i+1} at {entry_times[i]}")
            elif status == 1 and previous_status[i] == 0:  # Car exited
                exit_times[i] = time.time()
                print(f"Car exited slot {i+1} at {exit_times[i]}")
                if entry_times[i] is not None:
                    elapsed_times[i] = int(exit_times[i] - entry_times[i])
                    costs[i] = elapsed_times[i] * cost_per_unit_second
                    print(f"Elapsed time for slot {i+1}: {elapsed_times[i]} seconds")
                    print(f"Cost for slot {i+1}: {costs[i]}")
                    entry_times[i] = None  # Reset entry time after calculating

        # Write the elapsed times and costs to a CSV file
        with open('elapsed_times.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(elapsed_times + costs)

        # Update previous status for the next iteration
        previous_status = slots_status[:]
        print(f"Previous status updated to: {previous_status}")

        return jsonify({'slots': slots_status, 'cars': num_cars, 'elapsed_times': elapsed_times, 'costs': costs})

    except serial.SerialException as e:
        error_message = f"Error accessing COM port: {str(e)}"
        print(error_message)
        return jsonify({'error': error_message})
    except ValueError as e:
        error_message = f"Data parsing error: {str(e)}"
        print(error_message)
        return jsonify({'error': error_message})
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        print(error_message)
        return jsonify({'error': error_message})

if __name__ == '__main__':
    app.run(debug=True)
