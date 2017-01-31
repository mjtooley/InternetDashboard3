# InternetDashboard

Dashboard of US-based ISPs using RIPE Atlas probe data to show network outages, interconnection, and performance. Designed to illustrate that all this can be measured using publicly available data without requiring network operators to collect and submit this to a reporting organization or regulator.

The dashboard is written in Python an uses MongoDB to store a local copy of the RIPE measurement results of interest.  An analysis is performed by ASN to derive network outages, interconnection (peering and transit), and performance.  The output of the analysis is written to the MongoDB as JSON formatted documents to make it easy for a website to read in the JSON data and display.  A set of webpages with HTML and Javascript are included that render the JSON data.  

Prequisites:
- MongoDB installation 
- Python 2.6
- Web server (i.e. Apache)

Installation:
- Download Python code to a working directory
- Copy the three website directories to the webserver
- Configure configuration.ini

Run:
Latest updates:
- python Internetdashboard.py -c configuration.ini

Backfill database for the dates in the configuration.ini:
- python Mongodbsave.py -c configuration.ini
