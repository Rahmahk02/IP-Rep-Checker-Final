import requests
import tkinter as tk
from tkinter import messagebox, filedialog
import csv

# -----------------------------------
# 1️⃣ API Key for AbuseIPDB
# -----------------------------------
# This key is required for authenticating API requests.
# (⚠️ Keep your API key secret! Do NOT commit it to public repos.)
API_KEY = '3f66dd68273c3981daf1c9bd3143f01020cc82f6f855badf018070814b8d0e9a2f089c8095824498'

# Stores the last batch of results for CSV export
results_data = []

# -----------------------------------
# 2️⃣ Function: Check IP reputations
# -----------------------------------
def check_ips():
    global results_data
    results_data = []  # Reset old results

    # Get text from the input box, strip whitespace
    raw_input = ip_entry.get("1.0", tk.END).strip()

    # Split IPs by comma or newline, remove extra spaces
    ips = [ip.strip() for ip in raw_input.replace(',', '\n').split('\n') if ip.strip()]

    if not ips:
        messagebox.showwarning("Input Error", "Please enter at least one IP address.")
        return

    # Clear old output text
    result_text.delete(1.0, tk.END)

    # Loop over each entered IP address
    for ip in ips:
        try:
            # AbuseIPDB API endpoint & parameters
            url = "https://api.abuseipdb.com/api/v2/check"
            querystring = {
                'ipAddress': ip,
                'maxAgeInDays': '90'  # Only check reports within last 90 days
            }
            headers = {
                'Accept': 'application/json',
                'Key': API_KEY
            }

            # Send GET request to API
            response = requests.get(url, headers=headers, params=querystring)
            data = response.json()

            # If valid data is returned
            if 'data' in data:
                rep = data['data']

                # Extract relevant details into a dictionary
                info = {
                    'IP': rep['ipAddress'],
                    'Is Public': rep['isPublic'],
                    'Abuse Score': rep['abuseConfidenceScore'],
                    'Country': rep['countryCode'],
                    'Usage Type': rep.get('usageType', 'N/A'),
                    'ISP': rep.get('isp', 'N/A'),
                    'Domain': rep.get('domain', 'N/A'),
                    'Total Reports': rep['totalReports'],
                    'Last Reported At': rep.get('lastReportedAt', 'N/A')
                }

                # Save result for later CSV export
                results_data.append(info)

                # Display in the output text box
                result_text.insert(tk.END, "\n".join([f"{k}: {v}" for k, v in info.items()]) + "\n\n")
            else:
                # No data found or invalid IP
                result_text.insert(tk.END, f"{ip}: No data found or invalid IP.\n\n")

        except Exception as e:
            # Catch and display any errors during API calls
            result_text.insert(tk.END, f"{ip}: Error - {str(e)}\n\n")


# -----------------------------------
# 3️⃣ Function: Export results to CSV
# -----------------------------------
def export_csv():
    if not results_data:
        messagebox.showinfo("Export Error", "No results to export. Please check IPs first.")
        return

    # Ask user where to save CSV file
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")],
                                             title="Save as")
    if file_path:
        try:
            # Write CSV file
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=results_data[0].keys())
                writer.writeheader()
                for row in results_data:
                    writer.writerow(row)
            messagebox.showinfo("Export Successful", f"Results exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")


# -----------------------------------
# 4️⃣ GUI Setup with Tkinter
# -----------------------------------
root = tk.Tk()
root.title("IP Reputation Checker")

# Input label & text box
tk.Label(root, text="Enter IP address(es):\n(Separate by comma or newline)").pack(pady=5)
ip_entry = tk.Text(root, height=5, width=50)
ip_entry.pack()

# Buttons for check & export
tk.Button(root, text="Check IP(s)", command=check_ips).pack(pady=5)
tk.Button(root, text="Export to CSV", command=export_csv).pack(pady=5)

# Output text box for results
result_text = tk.Text(root, height=20, width=80)
result_text.pack(pady=10)

# Start Tkinter event loop
root.mainloop()

