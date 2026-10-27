"""
Tests for reports API endpoints.
"""
import pytest


class TestReportsEndpoints:
    """Test suite for quarterly and monthly report endpoints."""

    def test_get_quarterly_reports(self, client):
        """Test getting quarterly reports."""
        response = client.get("/api/reports/quarterly")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        for quarter in data:
            assert "quarter" in quarter
            assert "total_orders" in quarter
            assert "total_revenue" in quarter
            assert "avg_order_value" in quarter
            assert "fulfillment_rate" in quarter
            assert 0 <= quarter["fulfillment_rate"] <= 100

    def test_get_monthly_trends(self, client):
        """Test getting monthly trends sorted by month."""
        response = client.get("/api/reports/monthly-trends")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        months = [m["month"] for m in data]
        assert months == sorted(months)
        for month in data:
            assert "order_count" in month
            assert "revenue" in month

    def test_quarterly_reports_by_warehouse(self, client):
        """Test that quarterly totals match warehouse-filtered orders."""
        orders = client.get("/api/orders?warehouse=Tokyo").json()
        data = client.get("/api/reports/quarterly?warehouse=Tokyo").json()

        assert sum(q["total_orders"] for q in data) == len(orders)
        expected_revenue = sum(o["total_value"] for o in orders)
        assert abs(sum(q["total_revenue"] for q in data) - expected_revenue) < 0.01

    def test_quarterly_reports_by_quarter(self, client):
        """Test filtering quarterly reports to a single quarter."""
        response = client.get("/api/reports/quarterly?month=Q2-2025")
        assert response.status_code == 200

        data = response.json()
        assert all(q["quarter"] == "Q2-2025" for q in data)

    def test_quarterly_reports_by_status(self, client):
        """Test that a Delivered-only filter yields 100% fulfillment."""
        data = client.get("/api/reports/quarterly?status=Delivered").json()

        for quarter in data:
            assert quarter["fulfillment_rate"] == 100

    def test_monthly_trends_by_month(self, client):
        """Test filtering monthly trends to a single month."""
        response = client.get("/api/reports/monthly-trends?month=2025-03")
        assert response.status_code == 200

        data = response.json()
        assert all(m["month"] == "2025-03" for m in data)

    def test_monthly_trends_multiple_filters(self, client):
        """Test that monthly trends match orders under combined filters."""
        query = "warehouse=San Francisco&category=Sensors&status=Shipped"
        orders = client.get(f"/api/orders?{query}").json()
        data = client.get(f"/api/reports/monthly-trends?{query}").json()

        assert sum(m["order_count"] for m in data) == len(orders)
