from config import Client, ses

def send_booking_notification(customer_name: str, phone: str, datetime:str, client: Client, history: list[dict]):
    # Convert history to string readable format for the email
    history_str = ""
    for turn in history:
        role = turn.get("role", "unknown").capitalize()
        content = turn.get("content", "")
        history_str += f"{role}: {content}\n\n"

    ses.send_email(
        Source='peakflowaiautomatoins@gmail.com',
        Destination={'ToAddresses': ['eakflowaiautomatoins@gmail.com']},
        Message={
            'Subject': {'Data': f'AI Receptionist booked an appointment: {customer_name}'},
            'Body': {
                'Text': {
                    'Data': f"""New appointment booked by AI Receptionist:\nName: {customer_name}\nPhone: {phone}\nDate Time: {datetime}\nClient: {client.value}\n\nHistory:\n\n {history_str}"""
                }
            }
        }
    )