import streamlit as st
import pandas as pd
import smtplib
import json
import requests
from email.message import EmailMessage
from datetime import datetime, timedelta
from validator import validate_excel 

# --- PAGE CONFIG ---
st.set_page_config(page_title="License Sentinel Pro", page_icon="🛡️", layout="wide")

# --- SHARED LOGIC ---

def calculate_total(row):
    """Calculates Total = Quantity * Amount."""
    try:
        return float(row.get('Quantity', 0)) * float(row.get('Amount', 0))
    except:
        return 0.0

def should_send_reminder(row):
    """
    Logic: Triggers based on 'Billing period' if 'Status' is ACTIVE.
    Subscription period defines the contract, Billing period defines frequency.
    """
    try:
        today = datetime.now().date()
        expiry = pd.to_datetime(row['Expiration date']).date()
        status = str(row['Status']).upper().strip()

        if status == 'ACTIVE' and today <= expiry:
            billing_freq = str(row['Billing period']).strip().lower()
            renewal_date = pd.to_datetime(row['Renewal date']).date()

            if billing_freq == 'daily':
                return True
            if billing_freq == 'monthly':
                # Match the day of the month
                return today.day == renewal_date.day
            if billing_freq == 'annually':
                # Match the exact date
                return today == renewal_date
    except:
        return False
    return False

# --- MESSAGING ---

def send_email_reminder(recipient_email, row, config):
    total_due = calculate_total(row)
    msg = EmailMessage()
    msg['Subject'] = f"Invoice Reminder: {row['EndCustomerName']} - {row['Subscription name']}"
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

Best regards,
Billing Department"""
    msg.set_content(content)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(config['email_user'], config['email_pass'])
            smtp.send_message(msg)
        return True
    except:
        return False

def send_tg_reminder(token, chat_id, message):
    url = f"https://api.telegram.org/bot{str(token).strip()}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
        return True
    except:
        return False

# --- UI LAYOUT ---
tab1, tab2 = st.tabs(["📊 Dashboard", "⚙️ Settings"])

with tab2:
    st.header("Service Configuration")
    col1, col2 = st.columns(2)
    with col1:
        email_user = st.text_input("Sender Gmail", value=st.session_state.get('email_user', ''))
        email_pass = st.text_input("Gmail App Password", type="password")
    with col2:
        tg_token = st.text_input("Telegram Bot Token", type="password")
        tg_chat_id = st.text_input("Telegram Chat ID")

    if st.button("Save Configuration"):
        config = {'email_user': email_user, 'email_pass': email_pass, 'tg_token': tg_token, 'tg_chat_id': tg_chat_id}
        with open("config.json", "w") as f:
            json.dump(config, f)
        st.session_state.update(config)
        st.session_state['configured'] = True
        st.success("Settings Saved & Synced with Engine!")

with tab1:
    st.title("License Management & Billing Portal")
    uploaded_file = st.file_uploader("Upload Reseller/Subscription Excel", type=["xlsx"])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df.to_excel("data.xlsx", index=False) # Sync for Background Engine
        
        is_valid, message = validate_excel(df)
        if is_valid:
            active_df = df[df['Status'].str.upper() == 'ACTIVE'].copy()
            
            st.subheader("🤖 Automation Status")
            is_auto = st.toggle("Enable Auto-Pilot Preview")
            
            if is_auto:
                to_send_today = active_df[active_df.apply(should_send_reminder, axis=1)]
                st.metric("Invoices Due Today (Auto)", len(to_send_today))
                if not to_send_today.empty:
                    st.dataframe(to_send_today[['EndCustomerName', 'Subscription name', 'Billing period', 'Amount']])
            
            st.divider()
            st.subheader("🚀 Manual Campaign Settings")
            channel = st.radio("Channel", ["Email Only", "Telegram Only", "Both Channels"], horizontal=True)
            
            if st.button("🚀 Run Manual Campaign Now"):
                if not st.session_state.get('configured'):
                    st.warning("⚠️ Configure settings first.")
                else:
                    progress_bar = st.progress(0)
                    for i, (idx, row) in enumerate(active_df.iterrows()):
                        if "Email" in channel or "Both" in channel:
                            contact = str(row['Client Contact'])
                            if "@" in contact: send_email_reminder(contact, row, st.session_state)
                        
                        if "Telegram" in channel or "Both" in channel:
                            total = calculate_total(row)
                            tg_msg = f"💰 *Billing Alert*\n*Client:* {row['EndCustomerName']}\n*Amount:* ${total:,.2f}"
                            send_tg_reminder(st.session_state['tg_token'], st.session_state['tg_chat_id'], tg_msg)
                        progress_bar.progress((i + 1) / len(active_df))
                    st.success("Manual Campaign Complete!")
            
            st.dataframe(df)
        else:
            st.error(f"❌ {message}")