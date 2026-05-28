LOAD_WAREHOUSE_SQL = """
TRUNCATE TABLE
    public.fct_order,
    public.fct_inventory,
    public.dim_products,
    public.dim_store_branch,
    public.dim_employees,
    public.dim_customers
RESTART IDENTITY CASCADE;

INSERT INTO public.dim_customers (
    nk_customer_id,
    first_name,
    last_name,
    email,
    phone,
    loyalty_points,
    created_at
)
SELECT
    customer_id,
    first_name,
    last_name,
    email,
    phone,
    loyalty_points,
    created_at
FROM etl_staging.customers;

INSERT INTO public.dim_employees (
    nk_employee_id,
    first_name,
    last_name,
    hire_date,
    "role",
    email,
    created_at
)
SELECT
    employee_id,
    first_name,
    last_name,
    to_char(hire_date, 'YYYYMMDD')::int,
    "role",
    email,
    created_at
FROM etl_staging.employees;

INSERT INTO public.dim_store_branch (
    nk_store_id,
    store_name,
    created_at
)
SELECT
    store_id,
    store_name,
    created_at
FROM etl_staging.store_branch;

INSERT INTO public.dim_products (
    nk_product_id,
    product_name,
    category,
    unit_price,
    cost_price,
    in_stock,
    sk_store_branch,
    created_at
)
SELECT
    products.product_id,
    products.product_name,
    products.category,
    NULLIF(regexp_replace(products.unit_price::text, '[^0-9.-]', '', 'g'), '')::numeric,
    NULLIF(regexp_replace(products.cost_price::text, '[^0-9.-]', '', 'g'), '')::numeric,
    CASE
        WHEN lower(products.in_stock::text) IN ('true', 't', '1', 'yes', 'y', 'available', 'in stock') THEN true
        WHEN lower(products.in_stock::text) IN ('false', 'f', '0', 'no', 'n', 'unavailable', 'out of stock') THEN false
        ELSE NULL
    END,
    dim_store_branch.sk_store_id,
    products.created_at
FROM etl_staging.products AS products
LEFT JOIN public.dim_store_branch
    ON lower(dim_store_branch.store_name) = lower(products.store_branch);

WITH order_item_summary AS (
    SELECT
        order_id,
        min(product_id) AS product_id,
        sum(quantity) AS quantity,
        CASE
            WHEN sum(quantity) = 0 THEN NULL
            ELSE sum(subtotal) / sum(quantity)
        END AS unit_price,
        sum(subtotal) AS subtotal
    FROM etl_staging.order_details
    GROUP BY order_id
)
INSERT INTO public.fct_order (
    nk_order_id,
    sk_employee_id,
    sk_customer_id,
    sk_product_id,
    order_date,
    total_amount,
    quantity,
    unit_price,
    subtotal,
    payment_method,
    order_status,
    created_at
)
SELECT
    orders.order_id,
    dim_employees.sk_employee_id,
    dim_customers.sk_customer_id,
    dim_products.sk_product_id,
    to_char(orders.order_date::date, 'YYYYMMDD')::int,
    orders.total_amount,
    order_item_summary.quantity::varchar,
    order_item_summary.unit_price,
    order_item_summary.subtotal::varchar,
    orders.payment_method,
    orders.order_status,
    orders.created_at
FROM etl_staging.orders AS orders
LEFT JOIN order_item_summary
    ON order_item_summary.order_id = orders.order_id
LEFT JOIN public.dim_employees
    ON dim_employees.nk_employee_id = orders.employee_id
LEFT JOIN public.dim_customers
    ON dim_customers.nk_customer_id = orders.customer_id
LEFT JOIN public.dim_products
    ON dim_products.nk_product_id = order_item_summary.product_id
LEFT JOIN public.dim_date
    ON dim_date.date_id = to_char(orders.order_date::date, 'YYYYMMDD')::int;

INSERT INTO public.fct_inventory (
    nk_tracking_id,
    sk_product_id,
    quantity_change,
    change_date,
    reason,
    created_at
)
SELECT
    inventory_tracking.tracking_id,
    dim_products.sk_product_id,
    inventory_tracking.quantity_change,
    to_char(inventory_tracking.change_date::date, 'YYYYMMDD')::int,
    inventory_tracking.reason,
    inventory_tracking.created_at
FROM etl_staging.inventory_tracking
LEFT JOIN public.dim_products
    ON dim_products.nk_product_id = inventory_tracking.product_id
LEFT JOIN public.dim_date
    ON dim_date.date_id = to_char(inventory_tracking.change_date::date, 'YYYYMMDD')::int;
"""
