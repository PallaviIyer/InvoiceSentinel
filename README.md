# 🛡️ License Sentinel Pro

License Sentinel Pro is an enterprise-grade license management and automated billing notification suite. It combines a user-friendly **Streamlit Dashboard** for data management with a robust **Background Automation Engine** for "Auto-Pilot" reminders.

---

## 🏗️ System Architecture

The suite consists of two primary services that work in synchronization:
1.  **Management Dashboard (`app.py`):** Used for uploading license data, validating Excel schemas, manual campaign execution, and system configuration.
2.  **Automation Engine (`scheduler.py`):** A lightweight background service that monitors data and executes notifications (Email & Telegram) based on specific billing frequencies.



---

## 🚀 Quick Start (Windows)

1.  **Install Dependencies:**
    Open your terminal and run:
    ```bash
    pip install streamlit pandas openpyxl requests schedule
    ```

2.  **Launch the Suite:**
    Double-click `launch_sentinel.bat`. This will open two windows:
    * **Dashboard:** Accessible at `http://localhost:8501`
    * **Automation Engine:** Running in the background.

---

## ⚙️ Configuration

### 1. Settings Setup
Before automation triggers, you must navigate to the **Settings** tab in the Dashboard:
* **Gmail:** Enter your corporate Gmail and 16-digit **App Password**.
* **Telegram:** Enter your **Bot Token** and **Chat ID**.
* *Note: Saving these settings creates `config.json`, which is required by the Automation Engine.*

### 2. Data Upload
Upload your subscription Excel file in the **Dashboard** tab. The system will automatically sync this to `data.xlsx` for the background engine.

---

## 📊 Data Requirements (Excel Schema)

The system requires specific columns to calculate billing and trigger alerts:

| Column Name | Description |
| :--- | :--- |
| `EndCustomerName` | Name of the customer. |
| `Status` | Must be `ACTIVE` for any notification to trigger. |
| `Expiration date` | The date the service ends (alerts stop after this date). |
| `Renewal date` | The reference date for Monthly/Annual triggers. |
| `Subscription period` | The contract type (e.g., Annual). |
| `Billing period` | **The Trigger:** Set to `Daily`, `Monthly`, or `Annually`. |
| `Quantity` | Number of seats/licenses. |
| `Amount` | Unit price per license. |
| `Client Contact` | Recipient email address. |



---

## 🤖 Automation Logic

The **Automation Engine** executes calculations and sends alerts based on the `Billing period`:

* **Financial Calculation:** The system automatically calculates:
    $$Total Due = Quantity \times Amount$$
* **Trigger Frequency:**
    * **Daily:** Sends an alert every 24 hours (or every 10s in Test Mode).
    * **Monthly:** Sends an alert on the same day of the month as the `Renewal date`.
    * **Annually:** Sends an alert once a year on the specific `Renewal date`.

---

## 🛠️ Maintenance & Deployment

### Switching to Production Mode
By default, the engine is in **Testing Mode** (scanning every 10 seconds). To move to **Production Mode** (daily scan at 09:00 AM):

1.  Open `scheduler.py`.
2.  Navigate to the bottom of the file.
3.  Comment out the 10-second trigger and uncomment the 09:00 AM trigger:
    ```python
    # schedule.every(10).seconds.do(check_and_send_reminders) # Comment this
    schedule.every().day.at("09:00").do(check_and_send_reminders) # Uncomment this
    ```

### Troubleshooting
* **No Telegrams:** Check `config.json` to ensure the Bot Token is correct.
* **Script Errors:** Ensure no hidden spaces exist in the Excel column headers. Use the "Validate" button in the Dashboard to check integrity.

---

**Developed for Enterprise License Management.**
