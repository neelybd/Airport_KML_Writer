from tkinter import Tk
from file_handling import *
from selection import *
import time

print("Program: Airport KLM Writer ")
print("Release: 1.1.1")
print("Date: 2019-11-26")
print("Author: Brian Neely")
print()
print()
print("This program will create a KLM file for airport routes.")
print("The resulting file can be uploaded into Tableau to create great arcs.")
print("Airport and Flight Route Data: https://openflights.org/data.html")
print()
print()

# Hide Tkinter GUI
Tk().withdraw()

# Predefine Country Selection as False
cntry_slctn = False

# Upload a list of IATA Codes
if y_n_question("Upload File of IATA Codes (y/n): "):
    # Declare File Location
    file_in = select_file_in()

    # Set that a file was uploaded to True
    upload_airport_list = True

    # Identify CSV Encoding
    data = open_unknown_csv(file_in, ",")

    # Get header of airports
    airport_list_column = list_selection(list(data), "Select column that contains the airport list.", "column")

    # Get list of airports from data
    airport_list = data[airport_list_column]

    # Get list of unique airport codes and drop NAN's
    airport_unique = airport_list.dropna().unique().tolist()

    # Uppercase list
    airport_unique_list = [x.upper() for x in airport_unique if x.isalpha()]

else:
    # Master Data
    master = pd.read_csv('geolocation.csv')

    # All Airports?
    if y_n_question("Create KML of all airports (Warning: This action will take a long time and create a large file)"
                    " (y/n): "):
        airport_unique_list = master["IATA"].dropna()
    else:
        # List of Countries
        country_list = master["Country"].dropna().unique().tolist()

        # Select form list
        selected_countries = list_selection_multiple(country_list,
                                                     "Select countries to include in KML file.", "country")

        # Get list of IATA codes for selected countries
        airport_unique_list = master.loc[master["Country"].isin(selected_countries)]["IATA"].dropna()

        # Set Country Selection to 1 as an additional filter
        cntry_slctn = True

    # Include only airports with commercial flight routes
    if y_n_question("Only include airports with commercial flight routes (Recommended) (y/n): "):
        # Read routes CSV
        routes = pd.read_csv('routes.csv')

        # Create list of airports
        routes_airports = list()
        routes_airports.extend(list(routes["Origin"]))
        routes_airports.extend(list(routes["Destination"]))

        # Dedupe Routes Airports
        routes_airports_unique = unique(routes_airports)

        # Filter Main List
        airport_unique_list = airport_unique_list[airport_unique_list.isin(routes_airports_unique)]

    # Set file_in location to python folder
    file_in = "../"

# Start time
start_time = time.time()

# Header of KLM
kml_header = list()
kml_header.append('<?xml version="1.0" encoding="UTF-8"?>')
kml_header.append('<kml xmlns="http://www.opengis.net/kml/2.2">')

# Last line of KLM
lst_kml_line = "</kml>"

# Geolocation Data
geo = pd.read_csv('geolocation.csv')

# Drop NaN's
geo = geo.dropna()

# Filter geo list to airport list
airport_geo = geo[geo.IATA.isin(airport_unique_list)]

# Filter based on country if applicable
if cntry_slctn:
    airport_geo = airport_geo[airport_geo.Country.isin(selected_countries)]

# Origin DF
airport_origin = airport_geo[["Latitude Decimal Degrees", "Longitude Decimal Degrees", "IATA"]].reset_index()
airport_origin = airport_origin.rename(
    columns={"Latitude Decimal Degrees": "Origin Lat", "Longitude Decimal Degrees": "Origin Long", "IATA": "Origin"})

# Dest DF
airport_dest = airport_geo[["Latitude Decimal Degrees", "Longitude Decimal Degrees", "IATA"]].reset_index()
airport_dest = airport_dest.rename(
    columns={"Latitude Decimal Degrees": "Dest Lat", "Longitude Decimal Degrees": "Dest Long", "IATA": "Dest"})

# Assign fixed value common key to facilitate cartesian join
airport_origin['key'] = 0
airport_dest['key'] = 0

# Cartesian Join
cart_join_start_time = time.time()
print()
print("(" + str(round(time.time() - start_time,2)) + " s) Performing Cartesian Join on tables...")
airport_cart = airport_origin.merge(airport_dest, on='key').drop(columns='key')
print("(" + str(round(time.time() - start_time,2)) + " s) Cartesian Join complete. Join took: " +
      str(round(time.time() - cart_join_start_time,2)) + "sec")

# Only keep rows with valid commercial flight routes.
if y_n_question("Only include commercial flight routes (Recommended) (y/n): "):
    # Read routes CSV
    routes = pd.read_csv('routes.csv')

    # Create route list
    flight_route_actual = unique([i + " - " + j for i, j in zip(routes["Origin"], routes["Destination"])])
    airport_cart["flight_route"] = [i + " - " + j for i, j in zip(airport_cart["Origin"], airport_cart["Dest"])]

    # Filter List
    airport_cart = airport_cart[airport_cart.flight_route.isin(flight_route_actual)]

# Round and string dataframe
airport_cart = airport_cart.round({'Origin Lat': 3, 'Origin Long': 3, 'Dest Lat': 3, 'Dest Long': 3})

# Change Column type
airport_cart = airport_cart.astype({"Origin Long": str, "Origin Lat": str, "Dest Long": str, "Dest Lat": str})

# Create columns for KML in DF
airport_line = list()
print()
print("(" + str(round(time.time() - start_time, 2)) + " s) Creating rows...")
row_create_strt_time = time.time()
airport_line = ["<Placemark><name>" + i + " - " + j + "</name><LineString><coordinates>" + k + "," + l + " " + m + "," + n + "</coordinates></LineString></Placemark>" for i, j, k, l, m, n in zip(airport_cart["Origin"], airport_cart["Dest"], airport_cart["Origin Long"], airport_cart["Origin Lat"], airport_cart["Dest Long"], airport_cart["Dest Lat"])]
print("(" + str(round(time.time() - start_time, 2)) + " s) Rows created...")

# Select output file
out_path = select_file_out_kml(file_in)

# Erase the original file if exists
while not delete_file(out_path):
    print()
    print("File cannot be deleted. Please check if the file is currently open.")

print()
print("File has been cleared!")

# Open text file
out_file = open(out_path, 'a')

# Write Header
print()
print("(" + str(round(time.time() - start_time, 2)) + " s) Writing Data...")
for i in kml_header:
    out_file.write(str(i) + "\n")

# Write Airport Line
for i in airport_line:
    out_file.write(str(i) + "\n")

# Write Closer
out_file.write(lst_kml_line)

# Close and save file
out_file.close()
print("(" + str(round(time.time() - start_time,2)) + "sec ) File wrote!")

# Closer
input("Program Complete. Press Enter to close...")
