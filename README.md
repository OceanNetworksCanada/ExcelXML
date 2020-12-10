# ExcelXML
Updated version of Joe's ONC_StationXML. Moved into a separate repository to avoid confusion
Created by: Jacob Kukovica, Scientific Data Specialist, Data Team

Most detailed description on how to use the application and manage StationXML files can be found here: https://internal.oceannetworks.ca/display/ONCData/IRIS+StationXML+Management

This application expands on most of the features Joe had implemented and extends to features that were enabled in Obspy 1.2.1.

For easy of operation, keep the main application file (ExcelXML_app.py) in a single parent directory. Within this parent directory, ensure there is a _bin, _dataloggerRESP, _Inventories, and _sensorRESP.

In bin, the ChangeLog.txt file is contained to track any changes that have been made to the master inventory file. The FlatResponseXML.xml file is a flat instrument response file that can be formated based on instrument calibrations.

In dataloggerRESP and sensorRESP, these will contain the different instrument response files that can be applied to different channels.

In Inventories, folders of different inventories. This is intended to store various XML file edits, master files, etc...
