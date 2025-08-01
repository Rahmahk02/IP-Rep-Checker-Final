import requests
import tkinter as tk
from tkinter import messagebox, filedialog
import csv

# AbuseIPDB API key
API_KEY = 'your key' # Insert your own API key from AbuseIPDB

results_data = []

# Backend/Functionality

def check_ips():
    global results_data
    results_data = []
    raw_input = ip_entry.get("1.0", tk.END).strip()
    ips = [ip.strip() for ip in raw_input.replace(',', '\n').split('\n') if ip.strip()]

    if not ips:
        messagebox.showwarning("Input Error", "Please enter at least one IP address.")
        return

    result_text.delete(1.0, tk.END)

    for ip in ips:
        try:
            url = "https://api.abuseipdb.com/api/v2/check"
            querystring = {
                'ipAddress': ip,
                'maxAgeInDays': '90'
            }
            headers = {
                'Accept': 'application/json',
                'Key': API_KEY
            }

            response = requests.get(url, headers=headers, params=querystring)
            data = response.json()

            if 'data' in data:
                rep = data['data']
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
                results_data.append(info)

                result_text.insert(tk.END, "\n".join([f"{k}: {v}" for k, v in info.items()]) + "\n\n")
            else:
                result_text.insert(tk.END, f"{ip}: No data found or invalid IP.\n\n")

        except Exception as e:
            result_text.insert(tk.END, f"{ip}: Error - {str(e)}\n\n")


def export_csv():
    if not results_data:
        messagebox.showinfo("Export Error", "No results to export. Please check IPs first.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")],
                                             title="Save as")
    if file_path:
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=results_data[0].keys())
                writer.writeheader()
                for row in results_data:
                    writer.writerow(row)
            messagebox.showinfo("Export Successful", f"Results exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")


# Front end/GUI Setup
root = tk.Tk()
root.title("IP Reputation Checker")

tk.Label(root, text="Enter IP address(es):\n(Separate by comma or newline)").pack(pady=5)
ip_entry = tk.Text(root, height=5, width=50)
ip_entry.pack()

tk.Button(root, text="Check IP(s)", command=check_ips).pack(pady=5)
tk.Button(root, text="Export to CSV", command=export_csv).pack(pady=5)

result_text = tk.Text(root, height=20, width=80)
result_text.pack(pady=10)

root.mainloop()
