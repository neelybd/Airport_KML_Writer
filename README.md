# Airport_KML_Writer

This program creates a KML file from a list of IATA codes or from its own internal list, filtered.
The resulting KML file can be used with software like Tableau to create curved flight paths instead of straight line with ease.

  To use with list of IATA codes
    Open either the main.exe or main.py
    Question: Upload File of IATA Codes (y/n): 
      Input: y
    Popup: Select the csv containing the IATA codes.
    A select column input will appear, select the column contianing IATA codes. (Note: Invalid Codes will be skipped)
    Question: Only include commercial flight routes (Recommended) (y/n): 
      Input: Yes or No depending on if you want to filter the results to known commercial routes.
    Popup: Input save file location.
    Input: [Enter]

  To use without list of IATA Codes
    Open either the main.exe or main.py
    Question: Upload File of IATA Codes (y/n): 
      Input: n
    Question: Create KML of all airports (Warning: This action will take a long time and create a large file) (y/n):
      Input: Yes or No depending if you want to fliter the results by country.
      If No:
          A select country input will appear, select the countries you wish to include by number separted by spaces.
    Question: Only include airports with commercial flight routes (Recommended) (y/n):
      Input: Yes or No depending if you want to fliter the smaller airports without commerical flights.
    Question: Only include commercial flight routes (Recommended) (y/n): 
      Input: Yes or No depending on if you want to filter the results to known commercial routes.
    Popup: Input save file location.
    Input: [Enter]

  How to use KML with Tableau
    Open Tableau
    Drag KML file into Tablaeu 
    With the new data source, drag Geometry onto the canvas
    Drag Name to Detail
    Using a data blend with existing data, set a relationship between Name and Flight Path from the other data set
    Within the other dataset's Flight Path, filter null flights paths.

