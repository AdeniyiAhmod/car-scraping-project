from flask import Flask, render_template, jsonify, send_file, abort
from cron_job import main as run_cron_job, stop_scraping_flag
import pandas as pd
import os
import threading

app = Flask(__name__)
scraping_thread = None
status_message = "Idle"

def start_scraping():
    global stop_scraping_flag, status_message
    stop_scraping_flag = False
    status_message = "Checking for new hrefs"
    run_cron_job()
    status_message = "Idle"

def stop_scraping():
    global stop_scraping_flag, status_message
    stop_scraping_flag = True
    status_message = "Stopping scraping"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_scraping', methods=['GET'])
def start_scraping_route():
    global scraping_thread
    if scraping_thread is None or not scraping_thread.is_alive():
        scraping_thread = threading.Thread(target=start_scraping)
        scraping_thread.start()
        return jsonify({'message': 'Scraping started'})
    else:
        return jsonify({'message': 'Scraping is already running'})

@app.route('/stop_scraping', methods=['GET'])
def stop_scraping_route():
    stop_scraping()
    return jsonify({'message': 'Scraping stopped'})

@app.route('/status', methods=['GET'])
def status():
    total_hrefs = 0
    total_cars = 0
    last_car = "N/A"
    log = ""

    if os.path.exists("car_hrefs.csv"):
        df_hrefs = pd.read_csv("car_hrefs.csv")
        total_hrefs = len(df_hrefs)

    if os.path.exists("car_data.csv"):
        df_cars = pd.read_csv("car_data.csv")
        total_cars = len(df_cars)
        if total_cars > 0:
            last_car = df_cars.iloc[-1]['Car Name']

    if os.path.exists("scraping.log"):
        with open("scraping.log", "r") as log_file:
            log = log_file.read()
            # Filter out HTTP status logs
            log = "\n".join([line for line in log.split("\n") if "GET /status HTTP/1.1" not in line])

    return jsonify({'total_hrefs': total_hrefs, 'total_cars': total_cars, 'last_car': last_car, 'log': log, 'status_message': status_message})

@app.route('/download_csv', methods=['GET'])
def download_csv():
    if os.path.exists('car_data.csv'):
        return send_file('car_data.csv', as_attachment=True)
    else:
        abort(404, description="Resource not found")
        
if __name__ == '__main__':
    app.run(debug=True)
