def quality_result(check_name, failed_rows):
    return {
        "check_name": check_name,
        "status": "PASS" if len(failed_rows) == 0 else "FAIL",
        "offending_count": len(failed_rows),
        "sample_rows": failed_rows.head(5).to_dict("records")
    }