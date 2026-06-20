# Mentoring Week 8 - Data Integration and ETL Pipeline

**Building Data Pipeline with Python and Pyspark - Job Preparation Program - Pacmann AI**

---

## Task Description

In this exercise, you will develop a Data Pipeline like in the previous week and develop Machine Learning Pipeline that ingests data from the Data Warehouse and use the data for Machine Learning Modeling, then predict the data using Machine Learning model, and dump the model into MinIO.

## The Dataset

Use Docker Compose to run the container: repository

**Source Database Service**

* PostgreSQL services act as the raw data source
* The data contains Car Sales transactions data

**Staging Database Service**

* PostgreSQL service acts as the staging data source for storing all the data from sources data

**Log Database Service**

* PostgreSQL service acts as the log database to store all the log process for each process

**Warehouse Database Service**

* PostgreSQL service acts as the warehouse database to store the clean data after transformations and will be used for machine learning modeling

**MinIO Service**

* This service acts as a Bucket to store the .pkl machine learning model

**Spreadsheet data that contains Brand Car**

* Brand Car Spreadsheet
* You can use this data to mapping the Brand Name with the brand_car_id
* Make sure you create a copy of that Spreadsheet
* Also, don’t forget to create Credentials and enable Spreadsheet API to fetch the data from the Spreadsheet.

**API data**

* API data contains an ID of state, code of state, and the name of state.
* Use this data to map code of state from data source with the ID from API. You can access this API here

## Output

* Documentation of Requirement Gathering, Solutions, and Data Pipeline Design in README.md or Google Docs
* Data Pipeline Repository in GitHub

---

## Your Tasks

### Project Description

**Project Description**

* Describe the purpose of this project.

**Data Sources**

* Describe the data source from the database, API, and Spreadsheet.

**Problem Statement**

* Identify the problems, such as Data might be spread across multiple sources, Data may not be organized in a way that's immediately suitable for machine learning modeling
* Identify the data that can be used for supervised or Unsupervised Learning

**Solution Approach**

* Describe the Data Pipeline and Machine Learning Pipeline
* Pipeline Design: Create a simple diagram illustrating the flow of data from sources to machine learning pipeline

### Data Pipeline

**Data Exploration**
Before building the data pipeline, you must first explore and understand the dataset. Create a Jupyter Notebook for this purpose. Example:

* Checking the number of rows and columns.
* Identifying missing values.
* Identify data types

**Create a Python Script that compiles all the Pipeline process**

* **Helper function script**
Objective: Create reusable functions to support the data pipeline.
Ex: logging, database connection, create timestamp, create connection to spreadsheet
* **Extract**
Objective:
Create functions to extract data from database, spreadsheet, and API
Create function to extract data from staging for transforming data before dump into warehouse
Create function to extract data from warehouse to do a machine learning pipeline
* **Transform**
Objective: Clean and process the data, ensuring consistency with the warehouse schema
* **Load**
Objective: Dump the desired data into database
Dump data into Staging
Dump data into Warehouse
* **Preprocessing:**
Objective: Clean and splitting the data into desired format so you can use the data for modeling Machine Learning. MAKE SURE THE DATA ARE ALREADY IN THE CORRECT FORMAT BEFORE DO A MACHINE LEARNING MODELING!
Ex: OneHotEncoding, LabelEncoder, etc
* **Modeling**
Objective: Do a Machine Learning Modeling based on data you’re already preprocessing. Dump the model into MinIO object storage.
For Machine Learning Model you can choose anything that you like, ex: Linear Regression, Decision Tree Regression, etc
* **Main script**
Objective: Create a main function that runs all steps of the data pipeline in sequence:
1. Extract
2. Load Staging
3. Transform
4. Load Warehouse
5. Extract Warehouse
6. Preprocessing
7. Modeling



---

**Example Data Pipeline Structure:** [https://github.com/Kurikulum-Sekolah-Pacmann/ecommerce-data-integration/](https://github.com/Kurikulum-Sekolah-Pacmann/ecommerce-data-integration/)

**Notes:**

* Data Pipeline must have a logging process to store all the information for each data pipeline process
* Notebook First Approach: If you find it difficult to write the script directly, start by testing your transformations in a Jupyter Notebook before converting them into Python scripts.