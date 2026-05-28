CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE public.customers (
	customer_id int4 NOT NULL,
	first_name varchar(50) NULL,
	last_name varchar(50) NULL,
	email varchar(100) NULL,
	phone varchar(20) NULL,
	loyalty_points int4 DEFAULT 0 NULL,
	created_at timestamp DEFAULT now() NULL,
	CONSTRAINT customers_email_key UNIQUE (email),
	CONSTRAINT customers_pkey PRIMARY KEY (customer_id)
);

-- public.employees definition

-- Drop table

-- DROP TABLE public.employees;

CREATE TABLE public.employees (
	employee_id int4 NOT NULL,
	first_name varchar(50) NOT NULL,
	last_name varchar(50) NOT NULL,
	hire_date date NOT NULL,
	"role" varchar(50) NOT NULL,
	email varchar(100) NULL,
	created_at timestamp DEFAULT now() NULL,
	CONSTRAINT employees_email_key UNIQUE (email),
	CONSTRAINT employees_pkey PRIMARY KEY (employee_id)
);

-- public.orders definition

-- Drop table

-- DROP TABLE public.orders;

CREATE TABLE public.orders (
	order_id int4 NOT NULL,
	employee_id int4 NULL,
	customer_id int4 NULL,
	order_date timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	total_amount numeric(10, 2) NOT NULL,
	payment_method varchar(50) NOT NULL,
	order_status varchar(50) NOT NULL,
	created_at timestamp DEFAULT now() NULL,
	CONSTRAINT orders_pkey PRIMARY KEY (order_id)
);
CREATE INDEX idx_orders_customer ON public.orders USING btree (customer_id);
CREATE INDEX idx_orders_employee ON public.orders USING btree (employee_id);


-- public.orders foreign keys

-- public.products definition

-- Drop table

-- DROP TABLE public.products;

CREATE TABLE public.products (
	product_id int4 NOT NULL,
	product_name varchar(100) NOT NULL,
	category varchar(50) NOT NULL,
	unit_price varchar NOT NULL,
	cost_price varchar NOT NULL,
	in_stock varchar NULL,
	store_branch varchar NULL,
	created_at timestamp DEFAULT now() NULL,
	CONSTRAINT products_pkey PRIMARY KEY (product_id)
);


-- public.inventory_tracking definition

-- Drop table

-- DROP TABLE public.inventory_tracking;

CREATE TABLE public.inventory_tracking (
	tracking_id int4 NOT NULL,
	product_id int4 NULL,
	quantity_change int4 NOT NULL,
	change_date timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	reason varchar(100) NULL,
	created_at timestamp DEFAULT now() NULL,
	CONSTRAINT inventory_tracking_pkey PRIMARY KEY (tracking_id)
);


-- public.inventory_tracking foreign keys


-- public.order_details definition

-- Drop table

-- DROP TABLE public.order_details;

CREATE TABLE public.order_details (
	order_detail_id int4 NOT NULL,
	order_id int4 NULL,
	product_id int4 NULL,
	quantity int4 NOT NULL,
	unit_price numeric(10, 2) NOT NULL,
	subtotal numeric(10, 2) NOT NULL,
	created_at timestamp DEFAULT now() NULL,
	CONSTRAINT order_details_pkey PRIMARY KEY (order_detail_id)
);
CREATE INDEX idx_order_details_order ON public.order_details USING btree (order_id);
CREATE INDEX idx_order_details_product ON public.order_details USING btree (product_id);


-- public.order_details foreign keys


CREATE TABLE public.store_branch (
	store_id int4 NOT NULL,
	store_name varchar NULL,
	created_at timestamp NULL,
	CONSTRAINT store_branch_pk PRIMARY KEY (store_id)
);