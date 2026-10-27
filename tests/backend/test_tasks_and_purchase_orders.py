"""
Tests for task and purchase order API endpoints.
"""
import pytest

import main


@pytest.fixture(autouse=True)
def reset_mutable_state():
    """Restore in-memory tasks and purchase orders so tests stay independent."""
    saved_tasks = list(main.tasks)
    saved_pos = list(main.purchase_orders)
    yield
    main.tasks[:] = saved_tasks
    main.purchase_orders[:] = saved_pos


@pytest.fixture
def new_task():
    return {"title": "Recount sensors", "priority": "high", "dueDate": "2025-12-01"}


@pytest.fixture
def backlog_item_without_po(client):
    """A backlog item that has no purchase order yet."""
    items = client.get("/api/backlog").json()
    return next(item for item in items if not item["has_purchase_order"])


def make_po_request(backlog_item_id):
    return {
        "backlog_item_id": backlog_item_id,
        "supplier_name": "Acme Supply",
        "quantity": 100,
        "unit_cost": 12.5,
        "expected_delivery_date": "2025-12-15",
        "notes": "Expedite",
    }


class TestTasksEndpoints:
    """Test suite for task-related endpoints."""

    def test_get_all_tasks(self, client):
        """Test getting all tasks returns a list."""
        response = client.get("/api/tasks")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_task(self, client, new_task):
        """Test creating a task returns it as pending with a string ID."""
        response = client.post("/api/tasks", json=new_task)
        assert response.status_code == 201

        task = response.json()
        assert isinstance(task["id"], str)
        assert task["title"] == new_task["title"]
        assert task["priority"] == new_task["priority"]
        assert task["dueDate"] == new_task["dueDate"]
        assert task["status"] == "pending"

        all_tasks = client.get("/api/tasks").json()
        assert all_tasks[0]["id"] == task["id"]

    def test_create_task_missing_fields(self, client):
        """Test creating a task without required fields fails validation."""
        response = client.post("/api/tasks", json={"title": "No due date"})
        assert response.status_code == 422

    def test_toggle_task(self, client, new_task):
        """Test toggling a task flips its status both ways."""
        task_id = client.post("/api/tasks", json=new_task).json()["id"]

        response = client.patch(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

        response = client.patch(f"/api/tasks/{task_id}")
        assert response.json()["status"] == "pending"

    def test_delete_task(self, client, new_task):
        """Test deleting a task removes it from the list."""
        task_id = client.post("/api/tasks", json=new_task).json()["id"]

        response = client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 200

        all_tasks = client.get("/api/tasks").json()
        assert all(t["id"] != task_id for t in all_tasks)

    def test_toggle_nonexistent_task(self, client):
        """Test toggling a task that doesn't exist."""
        response = client.patch("/api/tasks/nonexistent-999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_nonexistent_task(self, client):
        """Test deleting a task that doesn't exist."""
        response = client.delete("/api/tasks/nonexistent-999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestPurchaseOrderEndpoints:
    """Test suite for purchase order endpoints."""

    def test_create_purchase_order(self, client, backlog_item_without_po):
        """Test creating a purchase order for a backlog item."""
        request = make_po_request(backlog_item_without_po["id"])
        response = client.post("/api/purchase-orders", json=request)
        assert response.status_code == 201

        po = response.json()
        assert po["id"].startswith("PO-")
        assert po["backlog_item_id"] == request["backlog_item_id"]
        assert po["supplier_name"] == request["supplier_name"]
        assert po["quantity"] == request["quantity"]
        assert abs(po["unit_cost"] - request["unit_cost"]) < 0.01
        assert po["status"] == "pending"
        assert len(po["created_date"]) == 10  # YYYY-MM-DD

    def test_create_purchase_order_marks_backlog_item(self, client, backlog_item_without_po):
        """Test that the backlog reports the item as having a PO after creation."""
        client.post("/api/purchase-orders", json=make_po_request(backlog_item_without_po["id"]))

        items = client.get("/api/backlog").json()
        item = next(i for i in items if i["id"] == backlog_item_without_po["id"])
        assert item["has_purchase_order"] is True

    def test_get_purchase_order_by_backlog_item(self, client, backlog_item_without_po):
        """Test fetching a created purchase order by its backlog item ID."""
        created = client.post(
            "/api/purchase-orders", json=make_po_request(backlog_item_without_po["id"])
        ).json()

        response = client.get(f"/api/purchase-orders/{backlog_item_without_po['id']}")
        assert response.status_code == 200
        assert response.json() == created

    def test_create_duplicate_purchase_order(self, client, backlog_item_without_po):
        """Test that a second PO for the same backlog item is rejected."""
        request = make_po_request(backlog_item_without_po["id"])
        client.post("/api/purchase-orders", json=request)

        response = client.post("/api/purchase-orders", json=request)
        assert response.status_code == 409

    def test_create_purchase_order_unknown_backlog_item(self, client):
        """Test creating a PO for a backlog item that doesn't exist."""
        response = client.post("/api/purchase-orders", json=make_po_request("nonexistent-999"))
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_purchase_order_missing_fields(self, client, backlog_item_without_po):
        """Test creating a PO without required fields fails validation."""
        response = client.post(
            "/api/purchase-orders", json={"backlog_item_id": backlog_item_without_po["id"]}
        )
        assert response.status_code == 422

    def test_get_nonexistent_purchase_order(self, client):
        """Test getting a PO for a backlog item that has none."""
        response = client.get("/api/purchase-orders/nonexistent-999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
