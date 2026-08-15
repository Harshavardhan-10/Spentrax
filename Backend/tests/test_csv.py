"""CSV import/export endpoint tests."""

VALID_CSV = (
    "Date,Description,Merchant,Category,Amount,Payment Method\n"
    "2026-08-01,Coffee,Starbucks,Food,180,UPI\n"
    "2026-08-02,Cab ride,Uber,Transportation,220,UPI\n"
)

MALFORMED_CSV = (
    "Date,Description,Merchant,Category,Amount,Payment Method\n"
    "2026-08-01,Coffee,Starbucks,Food,180,UPI\n"
    "2026-08-02,,Uber,Transportation,220,UPI\n"
    "2026-08-03,Dinner,,Food,not-a-number,UPI\n"
)

MISSING_COLUMNS_CSV = "Date,Description,Amount\n2026-08-01,Coffee,180\n"


def _upload(client, headers, content, filename="expenses.csv"):
    return client.post(
        "/csv/import",
        headers=headers,
        files={"file": (filename, content.encode("utf-8"), "text/csv")},
    )


def test_import_valid_csv(client, auth_headers):
    response = _upload(client, auth_headers, VALID_CSV)
    assert response.status_code == 200
    summary = response.json()["data"]
    assert summary["total_rows"] == 2
    assert summary["imported"] == 2
    assert summary["failed"] == 0
    assert summary["duplicates"] == 0

    expenses = client.get("/expenses", headers=auth_headers).json()["data"]
    assert expenses["total"] == 2


def test_import_detects_duplicates_on_reimport(client, auth_headers):
    _upload(client, auth_headers, VALID_CSV)
    response = _upload(client, auth_headers, VALID_CSV)
    summary = response.json()["data"]
    assert summary["imported"] == 0
    assert summary["duplicates"] == 2


def test_import_reports_bad_rows(client, auth_headers):
    response = _upload(client, auth_headers, MALFORMED_CSV)
    assert response.status_code == 200
    summary = response.json()["data"]
    assert summary["total_rows"] == 3
    assert summary["imported"] == 1
    assert summary["failed"] == 2
    assert len(summary["errors"]) == 2
    row_numbers = {error["row"] for error in summary["errors"]}
    assert row_numbers == {3, 4}


def test_import_missing_columns_rejected(client, auth_headers):
    response = _upload(client, auth_headers, MISSING_COLUMNS_CSV)
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["error_code"] == "CSV_MISSING_COLUMNS"


def test_import_invalid_file(client, auth_headers):
    response = _upload(client, auth_headers, "not csv at all", filename="bad.txt")
    assert response.status_code == 400
    assert response.json()["success"] is False


def test_import_requires_auth(client):
    response = _upload(client, {}, VALID_CSV)
    assert response.status_code == 401


def test_export_csv(client, auth_headers):
    _upload(client, auth_headers, VALID_CSV)
    response = client.get("/csv/export", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    content = response.text
    assert content.startswith("Date,Description,Merchant,Category,Amount,Payment Method")
    assert "Coffee" in content
    assert "Starbucks" in content
    assert "Transportation" in content


def test_export_empty(client, auth_headers):
    response = client.get("/csv/export", headers=auth_headers)
    assert response.status_code == 200
    assert "Date,Description" in response.text


def test_csv_user_isolation(client, users):
    _upload(client, users["headers_a"], VALID_CSV)
    response = client.get("/csv/export", headers=users["headers_b"])
    assert "Coffee" not in response.text