import re
import pandas as pd

def preprocess(data):
    # Define the regex pattern
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s?(?:am|pm)?) - (.+)'

    # Match all messages
    all_messages = re.findall(pattern, data)

    # Extract messages and clean dates
    messages = [message[1] for message in all_messages]
    cleaned_date_time = [message[0].replace('\u202f', ' ') for message in all_messages]

    # Create DataFrame
    df = pd.DataFrame({'user_message': messages, 'message_date': cleaned_date_time})
    try:
        df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p')
    except Exception as e:
        print("DateTime Parsing Error:", e)
        raise e

    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Parse user and message content
    user = []
    messages = []
    for message_content in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message_content)
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
