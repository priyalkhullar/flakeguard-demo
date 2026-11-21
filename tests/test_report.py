from inventory.report import Report


def test_report_title():
    assert Report().title() == "Report"
