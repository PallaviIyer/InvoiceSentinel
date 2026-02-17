import time
import json
import schedule
import pandas as pd
from datetime import datetime, timedelta
import requests
import smtplib
from email.message import EmailMessage

# --- HELPERS (Mirrored from app.py for consistency) ---

def load_config():
    """Reads the configuration saved by the Streamlit App."""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def calculate_total(row):
    """Calculates Total = Quantity * Amount."""
    try:
        return float(row.get('Quantity', 0)) * float(row.get('Amount', 0))
    except:
        return 0.0

def send_tg_reminder(token, chat_id, message):
    """Direct API call to Telegram to avoid ScriptRunContext issues."""
    url = f"https://api.telegram.org/bot{str(token).strip()}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
        return True
    except:
        return False

def send_email_reminder(recipient_email, row, config):
    """Sends the formatted billing email."""
    total_due = calculate_total(row)
    msg = EmailMessage()
    msg['Subject'] = f"Invoice Reminder: {row['EndCustomerName']}"
    msg['From'] = config['email_user']
    msg['To'] = recipient_email
    
    content = f"""Dear {row['EndCustomerName']} Team,

This is an automated billing reminder for your active subscription.

DETAILS:
--------------------------------------------------
Product:        {row['Subscription name']}
Contract Type:  {row['Subscription period']}
Billing Cycle:  {row['Billing period']}
Quantity:       {row.get('Quantity', 0)}
Unit Price:     ${row.get('Amount', 0):,.2f}
TOTAL DUE:      ${total_due:,.2f}
--------------------------------------------------
Next Renewal:   {row['Renewal date']}

Please ensure payment is processed to avoid service interruption.
"""
    msg.set_content(content)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(config['email_user'], config['email_pass'])
            smtp.send_message(msg)
        return True
    except:
        return False

# --- MAIN AUTOMATION LOGIC ---

def check_and_send_reminders():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Scanning data.xlsx for triggers...")
    
    config = load_config()
    if not config:
        print("⚠️ Waiting for configuration... (Please save settings in the App)")
        return

    try:
        df = pd.read_excel("data.xlsx")
        df.columns = [col.strip() for col in df.columns]
        today = datetime.now().date()

        # Filter for ACTIVE only
        active_df = df[df['Status'].str.upper() == 'ACTIVE']

        for _, row in active_df.iterrows():
            customer = row['EndCustomerName']
            expiry = pd.to_datetime(row['Expiration date']).date()
            billing_freq = str(row['Billing period']).strip().lower()
            renewal_date = pd.to_datetime(row['Renewal date']).date()
            
            # Condition 1: Must not be expired
            if today > expiry:
                continue

            # Condition 2: Check frequency trigger
            should_send = False
            if billing_freq == 'daily':
                should_send = True
            elif billing_freq == 'monthly' and today.day == renewal_date.day:
                should_send = True
            elif billing_freq == 'annually' and today == renewal_date:
                should_send = True

            if should_send:
                total_due = calculate_total(row)
                
                # 1. Send Telegram
                tg_msg = (f"💳 *Auto-Billing Alert*\n"
                          f"━━━━━━━━━━━━━━━\n"
                          f"*Customer:* {customer}\n"
                          f"*Total Due:* ${total_due:,.2f}\n"
                          f"*Frequency:* {billing_freq.capitalize()}")
                send_tg_reminder(config['tg_token'], config['tg_chat_id'], tg_msg)
                
                # 2. Send Email
                contact = str(row['Client Contact'])
                if "@" in contact:
                    send_email_reminder(contact, row, config)
                
                print(f"✅ Reminder sent to {customer}")

    except Exception as e:
        print(f"❌ Error during scan: {e}")

# --- SCHEDULER INITIALIZATION ---

# TESTING MODE: Runs every 10 seconds
schedule.every(10).seconds.do(check_and_send_reminders)

# PRODUCTION MODE: (Uncomment this and comment the line above when going live)
# schedule.every().day.at("09:00").do(check_and_send_reminders)

if __name__ == "__main__":
    print("🛡️ License Sentinel Automation Engine is LIVE")
    print("Mode: TESTING (Scanning every 10 seconds)")
    while True:
        schedule.run_pending()
        time.sleep(1)