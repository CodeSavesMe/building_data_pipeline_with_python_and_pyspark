from pathlib import Path

from paccafe_pipeline.staging.jobs import read_store_branch_spreadsheet_copy


def test_read_store_branch_spreadsheet_copy() -> None:
    rows = read_store_branch_spreadsheet_copy(Path("data/source/store_branch_paccofee.csv"))

    assert rows == [
        {"store_id": "1", "store_name": "Dapur Kenangan", "created_at": "2025-01-31 20:43:18"},
        {"store_id": "2", "store_name": "Laci Coffee", "created_at": "2025-01-31 20:43:18"},
        {"store_id": "3", "store_name": "Setara Coffee", "created_at": "2025-01-31 20:43:18"},
    ]
