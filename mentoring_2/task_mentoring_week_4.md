
# Mentoring Week 4 — Data Integration and ETL Pipeline

**Program:** Building Data Pipeline with Python and PySpark  
**Job Preparation Program:** Pacmann AI  

---

## Task Description

In the previous week, we already built Data Profiling, Data Quality Checker, and Recommendations for what we can do in our Data Pipeline Project.

Now, the PacCafe Manager wants to do an analysis and create a dashboard based on the available data. However, the problem is that the data is scattered and not stored in one source. Because of this, the owner struggles to perform analysis.

For this week, we will continue building the project. The focus will be on these tasks:

1. **Identify the Data**  
   Identify the data source, sink, and data stack that can be used, and build the documentation for requirements and solutions.

2. **Data Pipeline**  
   Build the data pipeline based on the requirements.

---

## Dataset

Use Docker Compose to run the container from the repository.

> **Important:** Make sure to use the `week-4` branch.

This dataset provides detailed information about:

- Cafe sales
- Employees
- Member customers
- Inventory tracking history
- Store branch data from spreadsheet: `store_branch_paccofee`

For the spreadsheet data:

- Make sure to create a copy of the spreadsheet.
- Create credentials.
- Enable the Spreadsheet API to fetch the data from the spreadsheet.

---

## Output

The expected outputs are:

- Documentation of Requirement Gathering, Solutions, and Data Pipeline Design in `README.md` or Google Docs
- Data Pipeline Repository in GitHub

---

# Your Tasks

## 1. Identify the Data

Create documentation in `README.md` or Google Docs.

Identify the following:

- Data source in this project
- Sink that will be used to dump all the data from the data source
- Tech stack used for building the data pipeline

You also need to:

- Create requirement gathering and solutions based on the given problem
- Create a data pipeline design based on the proposed solutions

For this project, make sure the layers of the data pipeline are:

```text
Source → Staging → Warehouse
````

---

## 2. Data Pipeline

Create a Python script that compiles all the data pipeline processes.

### Helper Function Script

Objective:

Create functions that can be used as helpers for the data pipeline.

Examples:

* Create database connection
* Create logging function
* Read data from SQL file

---

### Staging Script

Objective:

Create a folder called `staging` and a script to perform the Extract and Load process.

---

### Warehouse Script

Objective:

Create a folder called `warehouse` and a script to perform the Extract, Transform, and Load process.

---

### Main Script

Objective:

Create a main function to run all data pipeline processes from the Staging and Warehouse layers.

---

## Example Data Pipeline Structure

Reference repository:

```text
https://github.com/Kurikulum-Sekolah-Pacmann/ecommerce-data-integration/
```

---

## Notes

* The data pipeline must have a logging process to store all information for each data pipeline process.
* The data pipeline must have an error handling process.
* If the process fails, save or dump the failed data into object storage.
* You can use MinIO to store the failed data in object storage.
