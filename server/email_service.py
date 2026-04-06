from config import Client, ses

def send_booking_notification(customer_name: str, phone: str, date: str, time: str, client: Client, history: list[dict]):
    # Convert history to string readable format for the email
    history_str = ""
    for turn in history:
        role = turn.get("role", "unknown").capitalize()
        content = turn.get("content", "")
        history_str += f"{role}: {content}\n"

    ses.send_email(
        Source='jjd2843@rit.edu',
        Destination={'ToAddresses': ['jjd2843@rit.edu']},
        Message={
            'Subject': {'Data': f'AI Receptionist booked an appointment: {customer_name}'},
            'Body': {
                'Text': {
                    'Data': f'''
                        New appointment booked by AI Receptionist:

                        Name: {customer_name}
                        Phone: {phone}
                        Date: {date}
                        Time: {time}
                        Client: {client}
                        History: {history_str}
                    '''
                }
            }
        }
    )