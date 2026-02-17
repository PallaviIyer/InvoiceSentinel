import smtplib
from email.message import EmailMessage

def send_email_reminder(recipient_email, client_name, amount, due_date, config):
    """
    Sends a professional HTML email reminder.
    config: A dictionary containing 'email_user' and 'email_pass'
    """
    msg = EmailMessage()
    
    # Professional Email Content
    msg['Subject'] = f"Action Required: Invoice Reminder for {client_name}"
    msg['From'] = config['email_user']
    msg['To'] = recipient_email
    
    # Use a clean, professional template
    content = f"""
    Dear {client_name},

    This is a friendly reminder that your invoice of {amount} is currently marked as PENDING.
    The scheduled end date for this billing cycle was {due_date}.

    Please ensure payment is processed at your earliest convenience. 
    If you have already settled this, please ignore this message.

    Best regards,
    Accounts Department
    """
    msg.set_content(content)

    try:
        # Connect to Gmail's SSL SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(config['email_user'], config['email_pass'])
            smtp.send_message(msg)
        return True, "Success"
    except Exception as e:
        return False, str(e)

def send_summary_to_sender(sender_email, pending_df, config):
    """Sends a summary report to the person running the app."""
    msg = EmailMessage()
    msg['Subject'] = f"📊 Summary: Pending Invoice Report ({len(pending_df)} items)"
    msg['From'] = config['email_user']
    msg['To'] = sender_email # Sending it back to the person who logged in
    
    # Create a text-based table for the summary
    table_rows = ""
    for _, row in pending_df.iterrows():
        table_rows += f"- {row['Client Name']}: {row['Amount Due']} (Due: {row['End Date']})\n"

    content = f"""
    Hello,

    The invoice reminder campaign has finished. 
    Below is the list of clients currently marked as PENDING:

    {table_rows}

    Total Pending Amount: {pending_df['Amount Due'].replace(r'[\$,]', '', regex=True).astype(float).sum():,.2f}

    This is an automated report from Invoice Sentinel.
    """
    msg.set_content(content)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(config['email_user'], config['email_pass'])
            smtp.send_message(msg)
        return True
    except:
        return False