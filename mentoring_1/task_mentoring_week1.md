# Mentoring Week 2 - Data Profiling and Data Quality

**Program:** Building Data Pipeline with Python and PySpark - Job Preparation Program - Pacmann AI  
**Source image:** Freepik

---

# Task Description

As a Data Engineer, you are tasked with understanding and assessing the quality of a given dataset containing sales data.

Your responsibilities include:

1. **Data Profiling**  
   Explore the dataset to gain insights into its structure and attributes.

2. **Data Quality Check**  
   Assess the validity and consistency of the data. Identify anomalies and missing values.

3. **Recommendations**  
   Based on your findings, provide recommendations for cleaning and improving the dataset.

---

# The Dataset

Use Docker Compose to run the container from the provided repository.

This dataset provides detailed information about:

- Cafe sales
- Employees
- Member customers
- Inventory tracking history

---

# Output

Document your profiling and data quality process in a **Jupyter Notebook**.

---

# Your Tasks

---

# 1. Data Profiling

Create functions to profile the data and build a report.

---

## 1.1 Create a Function to List All Tables in the Database  
**Point:** 5

### Objective

Create a function for retrieving and displaying all tables available in the connected database.

### Hint

You can use an SQL query to access the list of tables.

---

## 1.2 Extract Data  
**Point:** 5

### Objective

Create a function to extract data from all tables in the database and return it in a structured format.

### Output

A dictionary where each key is a table name, and the corresponding value is a pandas DataFrame containing the data for that table.

### Suggested Format

```python
{
    "table_name_1": DataFrame,
    "table_name_2": DataFrame,
    ...
}
````

---

## 1.3 Create a Function to Get Information for Rows and Columns

**Point:** 5

### Objective

Create a function to retrieve the number of rows and columns for a specified table.

### Expected Result

Show the number of rows and columns for all tables.

---

## 1.4 Create a Function to Check Data Types of All Columns

**Point:** 5

### Objective

Create a function that checks the data types of all columns in a specified table.

### Example Dictionary Format

```python
{
    "column_name_1": datatype,
    "column_name_2": datatype,
    ...
}
```

### Expected Result

Show the result for all tables.

```python
{
    "table_name": {
        "column_name_1": datatype,
        "column_name_2": datatype,
        ...
    },
    ...
}
```

---

## 1.5 Create a Function to Check Unique Values in a Column

**Point:** 5

### Objective

Create a function that checks the unique values present in a specific column of a specified table.

### Output

A list of unique values found in the column.

### Data Check

| Table     | Column           |
| --------- | ---------------- |
| employees | `role`           |
| orders    | `payment_method` |
| products  | `category`       |
| inventory | `reason`         |

### Suggested Format

```python
{
    "column_name_1": ["value1", "value2"],
    "column_name_2": ["value1", "value2"],
    ...
}
```

---

## 1.6 Create Data Profiling Report

**Point:** 10

### Objective

Create a function to generate a data profiling report in dictionary format and save it to a JSON file.

### Output

A JSON file.

### Suggested Format

```json
{
  "person_in_charge": "name",
  "date_profiling": "timestamp",
  "result": {
    "table_name_1": {
      "shape": [rows, cols],
      "data_types": {
        "column_name_1": "data_type",
        "column_name_2": "data_type"
      },
      "unique_values": {
        "column_name_1": ["value_1", "value_2"]
      }
    },
    "table_name_2": {}
  }
}
```

---

# 2. Data Quality

Create functions to check data quality and build a report.

---

## 2.1 Check Missing Values

**Point:** 10

### Objective

Count missing values for each column.

---

## 2.2 Date Validation

**Point:** 10

### Objective

Validate date columns based on the expected date format.

### Data Check

| Table              | Column        | Expected Format       |
| ------------------ | ------------- | --------------------- |
| employees          | `hire_date`   | `yyyy-mm-dd`          |
| inventory_tracking | `change_date` | `yyyy-mm-dd`          |
| orders             | `order_date`  | `yyyy-mm-dd hh:mm:ss` |

---

## 2.3 Numeric Validation

**Point:** 10

### Objective

Check whether columns contain valid numeric values.

### Data Check

| Table              | Columns                              |
| ------------------ | ------------------------------------ |
| products           | `unit_price`, `cost_price`           |
| orders             | `total_amount`                       |
| order_details      | `unit_price`, `quantity`, `subtotal` |
| inventory_tracking | `quantity_change`                    |
| customers          | `loyalty_points`                     |

---

## 2.4 Negative Value Validation

**Point:** 10

### Objective

Identify negative values in columns where negative values are not allowed.

### Data Check

| Table              | Columns                              |
| ------------------ | ------------------------------------ |
| products           | `unit_price`, `cost_price`           |
| orders             | `total_amount`                       |
| order_details      | `unit_price`, `quantity`, `subtotal` |
| inventory_tracking | `quantity_change`                    |
| customers          | `loyalty_points`                     |

---

## 2.5 Build Data Quality Report

**Point:** 15

### Objective

Create a function to generate a data quality report in dictionary format and save it to a JSON file.

### Output

A JSON file.

### Suggested Format

```json
{
  "person_in_charge": "name",
  "date_quality_check": "timestamp",
  "result": {
    "table_name_1": {
      "missing_values": {
        "column_name_1": 0,
        "column_name_2": 2
      },
      "date_validity": {
        "column_name_1": "valid",
        "column_name_2": "invalid"
      },
      "numeric_validity": {
        "column_name_1": "valid",
        "column_name_2": "invalid"
      },
      "negative_validity": {
        "column_name_1": "valid",
        "column_name_2": "invalid"
      }
    }
  }
}
```

---

# 3. Recommendations

**Point:** 10

Based on your findings, provide recommendations for cleaning and improving the dataset.

The recommendations may include:

* Handling missing values
* Fixing invalid date formats
* Correcting invalid numeric values
* Investigating negative values
* Standardizing categorical values
* Improving table structure and data consistency
* Documenting assumptions and data quality rules
