import re
import pandas as pd

def preprocess(data):
    # Open and read the WhatsApp chat file

    # Define the regex pattern to capture date/time and message separately
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}, (?:[01]?\d|2[0-3]):\d{2}(?:\s?[apAP][mM])?) - (.+)'

    # Extract date/time and messages using re.findall
    all_messages = re.findall(pattern, data)

    # Separate messages and date/time into lists
    cleaned_date_time = [item[0].replace('\u202f', ' ') for item in all_messages]
    messages = [item[1] for item in all_messages]

    # Create the DataFrame
    df = pd.DataFrame({'message_date': cleaned_date_time, 'user_message': messages})

    # Convert `message_date` to datetime, handling both 12-hour and 24-hour formats
    date_formats = ['%d/%m/%Y, %I:%M %p', '%d/%m/%Y, %H:%M', '%d/%m/%y, %I:%M %p', '%d/%m/%y, %H:%M']

    for fmt in date_formats:
        try:
            df['message_date'] = pd.to_datetime(df['message_date'], format=fmt)
            break  # Exit loop once a format works
        except ValueError:
            continue

    # Rename the column
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Output the first few rows of the DataFrame
    # print(df.sample(10))


    # Parse user and message content
    user = []
    messages = []
    for message_content in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message_content)
        if entry[1:]:  # User name exists
            user.append(entry[1])
            messages.append(entry[2])
        else:
            user.append('group_notification')
            messages.append(entry[0])

    df['user'] = user
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Add additional columns
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['only_date'] = df['date'].dt.date  # Add only_date column

    # Add period column
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(f"{hour}-00")
        elif hour == 0:
            period.append("00-01")
        else:
            period.append(f"{hour}-{hour + 1}")
    df['period'] = period

    return df
