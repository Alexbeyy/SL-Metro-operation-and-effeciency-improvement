import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt

# Load all the GTFS data files
print("Loading GTFS data...")
try:
    agency = pd.read_csv("agency.txt")
    calendar_dates = pd.read_csv("calendar_dates.txt")
    routes = pd.read_csv("routes.txt")
    shapes = pd.read_csv("shapes.txt")
    stop_times = pd.read_csv("stop_times.txt")
    stops = pd.read_csv("stops.txt")
    trips = pd.read_csv("trips.txt")
except FileNotFoundError as e:
    print(f"Error: {e}")
    exit()

# Step 1: Convert and filter the calendar_dates data to include only one week of data
print("Filtering calendar_dates for the specified week...")
calendar_dates["date"] = pd.to_datetime(calendar_dates["date"], format="%Y%m%d")
start_date = pd.Timestamp("2025-04-21")
end_date = pd.Timestamp("2025-04-27")
filtered_calendar_dates = calendar_dates[
    (calendar_dates["date"] >= start_date) & (calendar_dates["date"] <= end_date)
].copy()

# Add a new column "day_name" to the filtered_calendar_dates DataFrame
filtered_calendar_dates["day_name"] = filtered_calendar_dates["date"].dt.day_name()
print("\nFiltered calendar_dates:")
print(filtered_calendar_dates[["service_id", "date", "day_name"]].head())

# Step 2: # Merge trips with calendar_dates to expand by operating days of the week
print("Merging trips with calendar_dates...")
trips_on_operating_days = pd.merge(trips, filtered_calendar_dates, on="service_id", how="inner")
trips_on_operating_days.drop_duplicates(subset=["trip_id", "date"], inplace=True)
print("\nFiltered trips:")
print(trips_on_operating_days[["route_id", "service_id", "trip_id"]].head())

# Step 3: Filter routes for SL Metro (Tunnelbanan)
print("Filtering routes for SL Metro...")
filtered_routes = routes[
    (routes["agency_id"] == 14010000000001001) &
    (routes["route_short_name"].astype(str).isin(["10", "11", "13", "14", "17", "18", "19"])) &
    (routes["route_type"].astype(int) == 401)
]
print("\nFiltered routes:")
print(filtered_routes[["route_id", "route_short_name", "route_long_name"]].head())

# Step 4: Merge filtered routes with filtered trips to get relevant trips
print("Merging filtered trips with filtered routes...")
trips_route = pd.merge(trips_on_operating_days, filtered_routes, on="route_id", how="inner")
print("\nTrips merged with routes:")
print(trips_route[["trip_id", "route_id", "service_id"]].head())

# Step 5: Filter stop_times based on trips for the specified routes
print("Filtering stop_times based on filtered trips...")
filtered_stop_times = stop_times[stop_times["trip_id"].isin(trips_route["trip_id"])]
print("\nFiltered stop_times:")
print(filtered_stop_times[["trip_id", "stop_id", "arrival_time", "departure_time"]].head())

# Step 6: Filter stops based on filtered stop_times
print("Filtering stops based on filtered stop_times...")
filtered_stops = stops[stops["stop_id"].isin(filtered_stop_times["stop_id"])]
print("\nFiltered stops:")
print(filtered_stops[["stop_id", "stop_name", "stop_lat", "stop_lon"]].head())

# Step 7: Filter shapes based on filtered trips
print("Filtering shapes based on filtered trips...")
filtered_shapes = shapes[shapes["shape_id"].isin(trips_route["shape_id"])]
print("\nFiltered shapes:")
print(filtered_shapes[["shape_id", "shape_pt_lat", "shape_pt_lon"]].head())

# Step 8: Count the number of unique trips per day of the week
print("Counting unique trips per day of the week...")
days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
#trip_counts = trips_route.groupby(filtered_calendar_dates["day_name"])["trip_id"].nunique().reindex(days_of_week, fill_value=0)
trip_counts = trips_route.groupby("day_name")["trip_id"].nunique().reindex(days_of_week, fill_value=0)
trip_counts.to_csv("trip_counts.csv", header=True)
print("\nTrip counts (unique trip_id per day):")
print(trip_counts)

# Step Plot the number of unique trips per day of the week
plt.figure(figsize=(10, 6))
trip_counts.plot(kind="bar", color="skyblue")
plt.title("Number of Unique Trips per Day of the Week (Stockholm SL Metro)")
plt.xlabel("Day of the Week")
plt.ylabel("Number of Unique Trips")
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

# Step 9: Plot the geographical paths of the routes
print("Plotting geographical paths of the routes...")
plt.figure(figsize=(10, 8))
sns.scatterplot(x="shape_pt_lon", y="shape_pt_lat", hue="shape_id", data=filtered_shapes, palette="viridis", s=10, legend=None)
plt.title("Geographical Paths of Stockholm SL Metro Routes")
plt.xlabel("Longitude (Degrees)")
plt.ylabel("Latitude (Degrees)")
plt.grid(True)
plt.show()

# Step 10: Plot the locations of the stops
print("Plotting the locations of the stops...")
plt.figure(figsize=(10, 10))
sns.scatterplot(x="stop_lon", y="stop_lat", data=filtered_stops, color="red", s=50, marker="o")
plt.title("Geographical Distribution of Stockholm SL Metro Stops")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)
plt.show()

# Step 11: Analyze stop connectivity
print("Analyzing stop connectivity...")
stops_with_routes = pd.merge(pd.merge(filtered_stop_times, trips_route, on="trip_id"), filtered_routes, on="route_id")
stop_route_count = stops_with_routes.groupby("stop_id")["route_id"].nunique().reset_index()
stop_route_count.rename(columns={"route_id": "number_of_routes"}, inplace=True)
stop_route_count = pd.merge(stop_route_count, filtered_stops, on="stop_id")

# Step  12: Plot the number of routes per stop
print("Plotting the number of routes per stop...")
plt.figure(figsize=(10, 10))
sns.scatterplot(x="stop_lon", y="stop_lat", size="number_of_routes", hue="number_of_routes",
                sizes=(50, 500), alpha=0.5, palette="coolwarm", data=stop_route_count)
plt.title("Number of Routes per SL Metro Stop in Stockholm")
plt.xlabel("Longitude (Degrees)")
plt.ylabel("Latitude (Degrees)")
plt.legend(title="Number of Routes")
plt.grid(True)
plt.show()

# Step 13: Convert the filtered_stop_times "arrival time" (now string)to datetime format for easier manipulation
#Time converting Function to be applied on filtered_stop_times "arrival time" column
def convert_to_time(time_str):
    try: #For normal parsing for times from 00:00:00 to 23:59:59
        parsed_time=dt.datetime.strptime(time_str, "%H:%M:%S").time()
        hour=parsed_time.hour #Capture the hour part from the parsed time for Later use
        return parsed_time, hour
    except ValueError: #Manual parsing for times >=24:00:00 to
        hour, minute, second=map(int, time_str.split(":")) #Apply the int() function for the string list resulted from time_str.splt()
        return dt.time(hour%24, minute, second), hour #return the corrected parsed time for time>=24:00:00 and capure hour part for later use

#Apply the function to the filtered_stop_times "arrival time" column
filtered_stop_times[["converted_arrival_time", "original_hour"]]=filtered_stop_times["arrival_time"].apply(lambda x: pd.Series(convert_to_time(x)))
#Check the first five rows of the filtered_stop_times DataFrame
print("\nFiltered stop_times with converted arrival time:")
print(filtered_stop_times[["arrival_time", "converted_arrival_time", "original_hour"]].head())

# Step 14: Sort filtered_stop_times by "arrival_time" and "stop_id"
filtered_stop_times_sorted= filtered_stop_times.sort_values(by=["stop_id", "converted_arrival_time"]).copy()
#Check the first five rows of the sorted filtered_stop_times DataFrame
print("\nSorted filtered stop_times:")
print(filtered_stop_times_sorted[["stop_id", "arrival_time", "converted_arrival_time"]].head())

#Step 15: Shift the arrival_time column to get the next arrival time for each stop
filtered_stop_times_sorted["next_arrival_time"]=filtered_stop_times_sorted.groupby("stop_id")["converted_arrival_time"].shift(-1)
#Check the first five rows of the filtered_stop_times_sorted DataFrame
print("\nFiltered stop_times with next arrival time:")
print(filtered_stop_times_sorted[["stop_id", "arrival_time", "converted_arrival_time", "next_arrival_time"]].head(10))

#Step 16: Calculate the time difference between the current and the next arrival time
#First develop a small function to calculate the time difference between two times
def calculate_time_difference(T1, T2):
    if pd.isna(T1) or pd.isna(T2): #Check if either of the times is NaN
        return None
    else:
        T1_dt=dt.datetime.combine(dt.datetime.today(), T1) # Combine the date and time to create full datetime objects
        T2_dt=dt.datetime.combine(dt.datetime.today(), T2)  
        return (T2_dt- T1_dt).seconds/60 # Calculate the difference in minutes
    
#Apply the function to the filtered_stop_times_sorted DataFrame
filtered_stop_times_sorted["interval_minutes"]=filtered_stop_times_sorted.apply(lambda row: calculate_time_difference(row["converted_arrival_time"], row["next_arrival_time"]), axis=1)
#Check the first five rows of the filtered_stop_times_sorted DataFrame
print("\nFiltered stop_times with interval time:")
print(filtered_stop_times_sorted[["stop_id", "arrival_time", "converted_arrival_time", "next_arrival_time", "interval_minutes"]].head(10))

# Step 17 : Remove the NAN values from the interval_minutes column(occurs in the last trip of the day)
filtered_stop_times_interval=filtered_stop_times_sorted.dropna(subset=["interval_minutes"]).copy()
#Check the first five rows of the filtered_stop_times_interval DataFrame
print("\nFiltered stop_times with interval time (NaN values removed):")
print(filtered_stop_times_interval[["stop_id", "arrival_time", "converted_arrival_time", "next_arrival_time", "interval_minutes"]].head(10))

# Step 18: Calculate the average interval time for each part of the day and each stop
# First, define a simplae function that creates time of day intervals based on the converted arrival time
def part_of_day(time_obj):
    if 5<= time_obj.hour <12: #time before from 5:00 to 12:00 
        return "Morning"
    elif 12<=time_obj.hour<17:# time between 12:00 and 17:00
        return "Afternoon"
    elif 17<=time_obj.hour<22: # time from 17:00 to 22:00
        return "Evening"
    else:
        return "Night"

# Apply the part_of_day function to the converted arrival time column
filtered_stop_times_interval["part_of_day"]=filtered_stop_times_interval["converted_arrival_time"].apply(part_of_day)

#Define the custom order for the part_of_day column
filtered_stop_times_interval["part_of_day"]=pd.Categorical(filtered_stop_times_interval["part_of_day"], categories=["Morning", "Afternoon", "Evening", "Night"], ordered=True)
# Check the first five rows of the filtered_stop_times_sorted DataFrame
print("\nFiltered stop_times with part of day:")
print(filtered_stop_times_interval[["stop_id", "arrival_time", "converted_arrival_time", "next_arrival_time", "interval_minutes", "part_of_day"]].head(10))

# Step 19: Calculate the average interval time for each stop and part of the day
average_interval=filtered_stop_times_interval.groupby("part_of_day")["interval_minutes"].mean().reset_index()
average_interval.rename(columns={"interval_minutes": "average_interval"}, inplace=True)

# Plot the average intervals per part of the day
plt.figure(figsize=(10,6))
plt.bar(average_interval["part_of_day"], average_interval["average_interval"], color="skyblue")
plt.title("Average Interval between trips per part of day")
plt.xlabel("Part of Day")
plt.ylabel("Average Interval (minutes)")
plt.grid(True)
plt.show()

# Step 20: Fix the part of day categories more precisely
def precise_part_of_day(time_obj):
    if time_obj.hour < 6:
        return "Early Morning"
    elif 6 <= time_obj.hour < 10:
        return "Morning Peak"
    elif 10 <= time_obj.hour < 16:
        return "Midday"
    elif 16 <= time_obj.hour < 20:
        return "Evening Peak"
    else:
        return "Late Evening"

# Apply the new part_of_day function
filtered_stop_times_interval["precise_part_of_day"] = filtered_stop_times_interval["converted_arrival_time"].apply(precise_part_of_day)

# Set categorical order
part_order = ["Early Morning", "Morning Peak", "Midday", "Evening Peak", "Late Evening"]
filtered_stop_times_interval["precise_part_of_day"] = pd.Categorical(filtered_stop_times_interval["precise_part_of_day"], categories=part_order, ordered=True)

# Step 21: Count number of trips per time period
print("Calculating trip counts by precise part of the day...")
trip_counts_precise = filtered_stop_times_interval.groupby("precise_part_of_day")["trip_id"].nunique().reset_index()
trip_counts_precise.rename(columns={"trip_id": "number_of_trips"}, inplace=True)
print("\nTrip counts by part of the day:")
print(trip_counts_precise)

# Step 22: Simulate frequency adjustments
adjustments = {
    "Early Morning": 1.0,       # No change
    "Morning Peak": 1.2,        # +20%
    "Midday": 0.9,              # -10%
    "Evening Peak": 1.2,        # +20%
    "Late Evening": 0.9         # -10%
}

# Apply adjustments
trip_counts_precise["adjusted_trips"] = trip_counts_precise.apply(lambda row: int(row["number_of_trips"] * adjustments[row["precise_part_of_day"]]), axis=1)

# Step 23: Plot before/after adjustment
plt.figure(figsize=(12,6))
bar_width = 0.35
index = range(len(trip_counts_precise))

plt.bar(index, trip_counts_precise["number_of_trips"], bar_width, label="Original Trips", color="skyblue")
plt.bar([i + bar_width for i in index], trip_counts_precise["adjusted_trips"], bar_width, label="Adjusted Trips", color="salmon")
plt.xlabel("Part of Day")
plt.ylabel("Number of Trips")
plt.title("Service Frequency Before and After Adjustment")
plt.xticks([i + bar_width/2 for i in index], trip_counts_precise["precise_part_of_day"], rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Step 24: Plot variability with boxplot (Optional but good)
plt.figure(figsize=(10,6))
sns.boxplot(x="precise_part_of_day", y="interval_minutes", data=filtered_stop_times_interval, palette="pastel")
plt.title("Distribution of Trip Intervals by Part of Day")
plt.xlabel("Part of Day")
plt.ylabel("Interval Between Trips (minutes)")
plt.grid(True)
plt.show()

# Step 25: (Optional) Estimate total system supply
# Assume 700 passengers per trip for estimation
capacity_per_trip = 700
trip_counts_precise["total_capacity_original"] = trip_counts_precise["number_of_trips"] * capacity_per_trip
trip_counts_precise["total_capacity_adjusted"] = trip_counts_precise["adjusted_trips"] * capacity_per_trip

print("\nEstimated system capacity before and after adjustment (assuming 700 passengers/train):")
print(trip_counts_precise[["precise_part_of_day", "total_capacity_original", "total_capacity_adjusted"]])



