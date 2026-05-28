from paccafe_pipeline.infrastructure.database import postgres_type_sql, qualified_name


def test_qualified_name_quotes_safe_identifiers() -> None:
    assert qualified_name("public", "customers") == '"public"."customers"'


def test_postgres_type_sql_handles_common_source_types() -> None:
    assert postgres_type_sql({"data_type": "integer"}) == "int4"
    assert postgres_type_sql({"data_type": "boolean"}) == "bool"
    assert postgres_type_sql({"data_type": "timestamp without time zone"}) == "timestamp"
    assert postgres_type_sql({"data_type": "character varying", "character_maximum_length": "50"}) == "varchar(50)"
    assert postgres_type_sql({"data_type": "numeric", "numeric_precision": "10", "numeric_scale": "2"}) == "numeric(10, 2)"
