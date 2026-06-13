# TASK MENTORING 3

## Task Overview: PySpark ETL Data Pipeline

In this exercise, you will build a data pipeline using PySpark to integrate data from multiple scattered sources (databases and CSV files) into a PostgreSQL Data Warehouse. You will create an efficient ETL (Extract, Transform, Load) process to consolidate and prepare the data for analysis.

---

## Environment & Infrastructure

You will use Docker Compose to run the required containers (refer to the provided repository):

* **PySpark Service:** Runs a Jupyter Notebook server for developing and executing Spark-based data transformations and Python scripts.
* **Source Database Service:** A PostgreSQL service acting as the raw data source.
* **Data Warehouse Service:** A PostgreSQL service acting as the central repository to integrate data from the source database and files.

---

## Data Sources

**1. Source Database (PostgreSQL)**

* **Context:** Data regarding phone-based direct marketing campaigns conducted by a bank to promote term deposit products. Multiple calls were often needed to determine if a client would subscribe ('yes' or 'no').
* **Tables included:** `education_status`, `marital_status`, and `marketing_campaign_deposit`.

**2. CSV File (`new_bank_transactions.csv`)**

* **Context:** Transactional and demographic data for over 800,000 banking customers, including account balances and transaction details.
* **Access:** Located in the provided directory. Use the PySpark function `spark.read.csv("data/new_bank_transactions.csv", header=True)` to extract it.

---

## Expected Deliverables

1. **Documentation:** A comprehensive Project Description and Data Pipeline Design written in `README.md` or Google Docs.
2. **Code Repository:** The complete Data Pipeline source code pushed to GitHub.

---

## Your Tasks

### Phase 1: Project Documentation

Create documentation covering the following aspects:

* **Project Description:** Explain the overarching purpose of this project.
* **Data Sources:** Detail the data sources originating from both the database and the CSV file.
* **Problem Statement:** Identify existing challenges, such as:
* Data being spread across multiple sources.
* Massive file sizes straining computational resources.
* Data currently unorganized and unsuitable for immediate analysis.


* **Solution Approach:** Describe your ETL process strategy.
* **Data Pipeline Design:** Create a simple architectural diagram illustrating the flow of data from source to destination.

### Phase 2: Data Exploration (EDA)

Before building the pipeline, you must explore and understand the dataset.

* Create a Jupyter Notebook inside the `script` directory.
* Perform basic checks, such as counting rows/columns and identifying missing values.

### Phase 3: Data Pipeline Construction

Your Python scripts must follow a predefined transformation process based on the provided **Source-to-Target Mapping Documentation**. Compile the process into structured scripts:

* **1. Helper Functions Script:**
* *Objective:* Create reusable support functions.
* *Requirement:* Implement a robust logging system. Ensure all execution logs are comprehensively captured and safely stored for every step of the ETL process to maintain a complete historical record of the pipeline's activity.


* **2. Extract:**
* *Objective:* Create functions to read data from the PostgreSQL source and the CSV folder.


* **3. Transform:**
* *Objective:* Clean, process, and standardize the data to ensure strict consistency with the warehouse schema.


* **4. Load:**
* *Objective:* Insert new data while maintaining the integrity of the Data Warehouse.
* *Method:* Truncate the target table before loading new data, then use the `append` method to load the processed data into the warehouse.


* **5. Main Script:**
* *Objective:* Create a `main()` function that executes the Extract, Transform, and Load steps sequentially.



---

## Important Notes & Tips

**Handling Legacy Date Formats**
Some date formats in the dataset may be inconsistent. Use the following configuration in your Spark session to handle legacy time parsing:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("AppName").getOrCreate()
# Handle legacy time parser
spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")

```

**Development Approach**

* **Notebook-First Approach:** If writing the Python pipeline scripts directly feels difficult, start by testing and verifying your transformations in a Jupyter Notebook first. Once successful, convert those cells into modular Python scripts.
* **Reference Architecture:** Check out this example Data Pipeline structure for guidance: [Ecommerce Data Integration Repo](https://github.com/Kurikulum-Sekolah-Pacmann/ecommerce-data-integration/)