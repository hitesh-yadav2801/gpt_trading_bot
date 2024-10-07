# user_data_manager.py
import csv
import logging

USER_DATA_FILE = 'user_data.csv'

# Dictionary to store user data in memory
user_data = {}

# Load CSV file at startup
def load_user_data():
    global user_data
    try:
        with open(USER_DATA_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user_id = int(row['telegram_id'])
                user_data[user_id] = {
                    'isRegistered': row['isRegistered'] == 'True',
                    'hasDeposited': row['hasDeposited'] == 'True'
                }
        logging.info("User data loaded successfully from CSV.")
    except FileNotFoundError:
        logging.warning("CSV file not found. Starting with an empty user data set.")
        user_data = {}

# Save the CSV file when user data is updated
def save_user_data():
    global user_data
    with open(USER_DATA_FILE, mode='w', newline='') as file:
        fieldnames = ['telegram_id', 'isRegistered', 'hasDeposited']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for user_id, data in user_data.items():
            writer.writerow({
                'telegram_id': user_id,
                'isRegistered': data['isRegistered'],
                'hasDeposited': data['hasDeposited']
            })
    logging.info("User data saved to CSV.")

# Function to get user status from the in-memory dictionary
def get_user_status(user_id):
    return user_data.get(user_id, {'isRegistered': False, 'hasDeposited': False})

# Function to update user status
def update_user_status(user_id, isRegistered, hasDeposited):
    global user_data
    user_data[user_id] = {'isRegistered': isRegistered, 'hasDeposited': hasDeposited}
    save_user_data()  # Save changes to the CSV
