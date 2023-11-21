# YouTube-Data-Harvesting-and-Warehousing-Using-Sql-Mongodb-and-Streamlit

This is a project that harvests data from YouTube using the YouTube Data API and stores the data in a MongoDB database as a data lake. The data is then migrated from the data lake to a SQL database as tables and displayed in a Streamlit application.

## Data Collection

The first step is to collect data from YouTube. This can be done using the YouTube Data API. The API provides access to a wide range of data, including channel information, video statistics, and comment information etc.

## Data Storage

The collected data can be stored in a variety of ways. In this project, we will use MongoDB and SQL. MongoDB is a NoSQL database that is well-suited for storing large amounts of unstructured data. SQL is a relational database that is well-suited for querying and analyzing structured data.

## Data Warehousing

After you've collected data for multiple channels, you can migrate it to a SQL data warehouse. You can use a SQL database such as MySQL or PostgreSQL for this.You can use SQL queries to join the tables in the SQL data warehouse and retrieve data for specific channels based on user input.

## Streamlit

 Finally, you can display the retrieved data in the Streamlit app.Streamlit is a Python library that can be used to create interactive web applications. Overall, this approach involves building a simple UI with Streamlit, retrieving data from the YouTube API, storing it in a MongoDB data lake, migrating it to a SQL data warehouse, querying the data warehouse with SQL, and displaying the data in the Streamlit app.

## Getting Started

To get started with this project, you will need to do the following:

1. Install and Import the required Python packages like google-api-python-client, streamlit, streamlit-option-menu, pymongo, mysql-connector-python, pandas.
2. Set up a Google Cloud Platform project and enable the YouTube Data API.
4. Set up a MongoDB Atlas cluster.
5. Set up a SQL database(mysql).
6. open the terminal, type streamlit run `yt.py` script to start the Streamlit application in your web browser.

## Key Skills
Python scripting, Data Collection,MongoDB, Streamlit, API integration, Data Management using MongoDB (Atlas) and SQL(mysql).



