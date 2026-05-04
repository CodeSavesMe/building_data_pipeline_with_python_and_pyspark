# Data Profiling and Data Quality Summary

## Overview

This summary captures the main findings from the data profiling and data quality checks performed on the Paccafe PostgreSQL dataset. The analysis was focused on understanding table structure, validating selected business-critical columns, and identifying issues that should be cleaned before the data is used for reporting or downstream pipelines.

Overall, the dataset is usable, but it requires targeted cleaning in product pricing fields, categorical columns, and a small number of customer-related records.

## Dataset Overview

The source database contains 6 tables:

| Table | Rows | Columns | Main Notes |
| --- | ---: | ---: | --- |
| `customers` | 204 | 7 | Mostly clean, but has missing phone values and negative loyalty points |
| `employees` | 103 | 7 | Valid structure, but role values are not fully standardized |
| `inventory_tracking` | 162 | 6 | Structurally clean, but reason values contain an invalid label |
| `order_details` | 3022 | 7 | Cleanest transactional table in the dataset |
| `orders` | 1010 | 8 | Has missing `customer_id`, likely for guest orders |
| `products` | 54 | 7 | Highest-risk table due to pricing type and value issues |

## Profiling Results

### Schema and data types

- Most tables have expected data types for identifiers, timestamps, and numeric fields.
- `products.unit_price` and `products.cost_price` are stored as strings, unlike the pricing fields in transactional tables.
- `orders.customer_id` is stored as `float64` because of missing values.

### Unique value checks

The categorical checks found valid business values mixed with invalid labels:

- `employees.role`: `Barista`, `Cashier`, `Manager`, `Waiter`, `Waitress`, plus invalid values `me`, `third`, `today`
- `orders.payment_method`: `Cash`, `Credit Card`, `Debit Card`, plus invalid value `ERROR`
- `inventory_tracking.reason`: `Damaged`, `Expired`, `Restock`, plus invalid value `ERROR`
- `products.category`: all observed values are consistent and valid

## Data Quality Results

### Missing values

Only two meaningful missing-value issues were found:

- `orders.customer_id`: 250 missing values
- `customers.phone`: 4 missing values

No blank-like placeholder values were detected in the checked columns.

### Date validation

All configured date columns passed validation:

- `employees.hire_date`
- `inventory_tracking.change_date`
- `orders.order_date`

This means date formatting is not currently a priority issue.

### Numeric validation

Most checked numeric fields passed validation:

- `orders.total_amount`: valid
- `order_details.unit_price`, `quantity`, `subtotal`: valid
- `inventory_tracking.quantity_change`: valid
- `customers.loyalty_points`: valid as a numeric field

The main failure is in the `products` table:

- `products.unit_price`: 54 out of 54 values flagged as invalid numeric input
- `products.cost_price`: 54 out of 54 values flagged as invalid numeric input

These failures are recoverable because the values appear to be numeric amounts stored as strings with currency symbols such as `$47.00`.

### Negative value validation

Negative values were found in columns where they are not expected:

- `customers.loyalty_points`: 4 negative values
- `products.unit_price`: 2 negative values after parsing
- `products.cost_price`: 3 negative values after parsing

The other checked columns passed negative-value validation.

## Key Issues and Interpretation

### 1. Product pricing fields are the highest-priority issue

The `products` table has both schema and business-rule problems:

- prices are stored as strings instead of numeric types
- all price values need normalization before they can be trusted
- some parsed values are negative, which violates the expected pricing rule

This is the most important issue because it can affect joins, aggregations, margin analysis, and pricing-related reporting.

### 2. Categorical values are not fully standardized

Invalid labels such as `ERROR`, `me`, `third`, and `today` indicate either source data entry problems or bad seed data. These values should not remain in production-facing datasets because they reduce reporting consistency and weaken dimension-based analysis.

### 3. Missing `customer_id` likely reflects guest transactions

The 250 missing `customer_id` values in `orders` should not automatically be treated as bad data. In a cafe sales context, this likely means some orders were made by non-member customers. This is better modeled explicitly than filled with artificial IDs.

### 4. Customer data needs minor but important cleanup

The `customers` table is mostly healthy, but:

- 4 missing phone values affect contact completeness
- 4 negative loyalty point values require business clarification or correction

## Recommendations

### Priority 1: Normalize product prices

- strip currency symbols from `products.unit_price` and `products.cost_price`
- cast both fields to a numeric type such as `NUMERIC(10,2)`
- reject or quarantine negative price values
- add a validation rule to ensure `cost_price <= unit_price`, unless the business explicitly allows exceptions

Example execution:

```sql
UPDATE products
SET
  unit_price = REPLACE(unit_price, '$', ''),
  cost_price = REPLACE(cost_price, '$', '');

ALTER TABLE products
ALTER COLUMN unit_price TYPE NUMERIC(10,2) USING unit_price::NUMERIC,
ALTER COLUMN cost_price TYPE NUMERIC(10,2) USING cost_price::NUMERIC;

SELECT product_id, product_name, unit_price, cost_price
FROM products
WHERE unit_price < 0
   OR cost_price < 0
   OR cost_price > unit_price;
```

This execution first cleans the currency symbol, then converts the column type, and finally isolates rows that still break the pricing rule for manual review.

### Priority 2: Standardize categorical columns

- clean `employees.role`
- clean `orders.payment_method`
- clean `inventory_tracking.reason`
- use lookup tables or `CHECK` constraints to prevent invalid values from reappearing

Example execution:

```sql
UPDATE employees
SET role = 'Unknown'
WHERE role IN ('me', 'third', 'today');

UPDATE orders
SET payment_method = 'Unknown'
WHERE payment_method = 'ERROR';

UPDATE inventory_tracking
SET reason = 'Unknown'
WHERE reason = 'ERROR';
```

For a stricter implementation, valid values can be limited with a constraint such as `CHECK (payment_method IN ('Cash', 'Credit Card', 'Debit Card', 'Unknown'))`.

### Priority 3: Handle guest orders explicitly

- do not fill missing `orders.customer_id` with fake customer IDs
- add a business flag such as `is_guest_order`
- document the rule so future analysts interpret these records correctly

Example execution:

```sql
ALTER TABLE orders
ADD COLUMN is_guest_order BOOLEAN;

UPDATE orders
SET is_guest_order = customer_id IS NULL;
```

With this approach, orders without a member record remain traceable without introducing fake customer keys.

### Priority 4: Review negative business values

- investigate why some customers have negative loyalty points
- confirm whether negative balances are valid business behavior or data errors
- review negative parsed product prices and correct them at source or during ingestion

Example execution:

```sql
SELECT customer_id, first_name, last_name, loyalty_points
FROM customers
WHERE loyalty_points < 0;

SELECT product_id, product_name, unit_price, cost_price
FROM products
WHERE unit_price < 0 OR cost_price < 0;
```

These queries separate suspicious records for investigation before deciding whether the values should be corrected, reset, or documented as valid exceptions.

### Priority 5: Strengthen pipeline validation

- add post-load validation checks for pricing, categories, and null-sensitive fields
- add business-rule checks such as `orders.total_amount = sum(order_details.subtotal)` where appropriate
- keep profiling and quality reports as repeatable outputs for every dataset refresh

Example execution:

```sql
SELECT
  o.order_id,
  o.total_amount,
  SUM(od.subtotal) AS detail_total
FROM orders o
JOIN order_details od ON o.order_id = od.order_id
GROUP BY o.order_id, o.total_amount
HAVING o.total_amount <> SUM(od.subtotal);
```

This validation can be added as a scheduled quality check after every load so broken transactional totals are detected immediately.

## Conclusion

The dataset is in reasonably good shape for an exercise dataset, and most core transactional fields are structurally valid. The main exceptions are product price formatting, a few invalid categorical labels, missing `customer_id` for guest-like orders, and a small number of negative business values.

If the pricing fields are normalized and the categorical anomalies are cleaned, the dataset will be much more reliable for analysis, reporting, and downstream data engineering work.
