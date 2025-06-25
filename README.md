# 🚇 SL Metro Optimization Using GTFS Datasets

This project analyzes and optimizes the service frequency of Stockholm’s SL Metro using GTFS timetable data. All processing and analysis are fully automated in Python.

---

## 📌 Project Features

- ✅ Loads and filters GTFS timetable and route data
- ⏱️ Converts and processes arrival times
- 🕒 Categorizes trips by time of day (e.g., Morning Peak, Evening Peak)
- 📉 Calculates average intervals between trips per stop and time period
- 📈 Simulates a new service plan with:
  - ➕ 20% more trips during peak hours
  - ➖ 10% fewer trips during off-peak hours
- 📊 Visualizes frequency patterns and improvements using Matplotlib and Seaborn

---

## 📁 Data Source

⚠️ **GTFS data files are not included** in this repository due to GitHub file size limits.

You can download the official dataset from Samtrafiken’s Trafiklab:

➡️ [https://www.trafiklab.se/api/gtfs-datasets](https://www.trafiklab.se/api/gtfs-datasets)

After downloading, extract the ZIP and place relevant `.txt` files (e.g., `trips.txt`, `stop_times.txt`, `shapes.txt`) in your local project folder (e.g., `GTFS_Datasets/`).

---

## 🧰 Tools & Libraries Used

- **Python**:
  - `pandas`
  - `matplotlib`
  - `seaborn`
  - `datetime`
- **GTFS** (General Transit Feed Specification)
- *(Optional)*: QGIS for geospatial route and stop visualization

---

## 📈 Key Outcomes

- 📍 Charts and heatmaps showing average trip intervals by time of day
- 🚆 Simulated improvements in train capacity and frequency
- 🔍 Demonstration of how GTFS data can support smarter public transit planning — even without real-time passenger data

---

## 👤 Author

**Alemayehu Abadi**  
[www.linkedin.com/in/alemayehu-abadi-beyene-6bb168126](https://www.linkedin.com/in/alemayehu-abadi-beyene-6bb168126)

---

## 📜 License

This project is for educational purposes. Data usage must comply with the terms provided by [trafiklab.se](https://www.trafiklab.se/).

