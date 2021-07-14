# Teamviewer Log Parsers

## simple_ci_parser.py

This script will take the connections_incoming.txt log file, parse the contents and write them to a csv file for further analysis.

example usage: 

> #python ./simple_ci_parser.py -i /path/to/connections_incoming.txt -o results.csv


## teamviewer_ci_parser.py

This script will take the contents of the connections_incoming.txt log file, parse them and save them to an SQL Database which can then be written to CSV or HTML. It allows you to add a case reference if required. Data in SQL DB is stored and can be queried at a later date

example usage:

> #python ./teamviewer_ci_parser.py 0126457 -i /path/to/connections_incoming.txt -o results.csv/results.html

## teamviwer_oldlog_parser.py

This script will take the contents of TeamViewer_Logfile_OLD.txt log file, parse them and write them to a csv file for further analysis. It will also parse all the IP address related logs seperately which can then be resolved through a tool such as Abeebus (13cubed)

example usage:

> #python ./teamviewer_oldlog_parser.py -i /path/to/TeamViewer_logfile_OLD.txt


I hope these are helpful and if you have any suggestions for amendments or changes, please feel free to get in contact.

Written using Python 3.8.5
