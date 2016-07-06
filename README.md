# Description

[inteltool][inteltool] was designed to scrape all data from publicly available killboards into a database and run various reports / analysis on the data. The purpose of most of this was to understand an enemy corporation / alliance in several ways:

- General online times / activity
- Capital online times / activity
- Average gang size
- Identification of Cyno bait / blingy tackles
- Hotdrop peak times

Data is exported in spreadsheet / csv format and then can be used by tables and graphs as a data source.

![General Charts](https://s3.amazonaws.com/inteltool.github.io/static/inteltool_graphs_general.png)
![Blingy Tackler Table](https://s3.amazonaws.com/inteltool.github.io/static/inteltool_table_blingtackle.png)
![Cap Pilot Activity Table](https://s3.amazonaws.com/inteltool.github.io/static/inteltool_table_cappilots.png)

The tool was also expanded to gain an economic understanding of what items would be in demand the most in a region with the data provided on the killboard. This could then be used to import items to tradehubs for an often solid profit margin.

The tool may need some newer data imported into it to be useful, but most of what is needed to do basic scraping, importing and analysis is already available.

# Dependencies

- Python3.X
- SQLAlchemy
- openpyxl


[eve]: https://www.eveonline.com
[inteltool]: https://github.com/csvance/inteltool
