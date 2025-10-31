import json, random

softwares = ["Autodesk", "MATLAB", "SolidWorks", "CATIA", "ANSYS", "Revit", "Fusion360", "Creo", "Maya", "3dsMax"]
locations = ["India", "USA", "Germany", "Japan", "UK", "France", "Australia"]
servers = [f"27000@SRV{i:05}" for i in range(10000)]

data = []
for i in range(10000):
    record = {
        "software": random.choice(softwares),
        "server": random.choice(servers),
        "location": random.choice(locations),
        "license": f"{random.randint(80000, 99999)}{random.choice(['ACAD', 'REV', 'SOLID', 'CAT', 'MAYA'])}_E_{random.randint(2018,2024)}_0F",
        "latest_license_issued": random.randint(1, 50),
        "license_day_peak": random.randint(1, 10),
        "license_day_average": random.randint(1, 10),
        "license_work_peak": random.randint(1, 10),
        "license_work_average": random.randint(1, 10),
        "percentage_work_peak": random.randint(10, 100),
        "percentage_work_average": random.randint(5, 90)
    }
    data.append(record)

with open("license_data_sample.json", "w") as f:
    json.dump(data, f, indent=2)

print("✅ Sample dataset with 10,000 records created: license_data_sample.json")
