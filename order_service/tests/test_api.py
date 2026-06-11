from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from order_service.api.app import create_app
from order_service.api.dependencies import get_order_service
from order_service.bootstrap.factory import create_order_service
from order_service.config.pricing_mode import PricingMode
from order_service.domain.exceptions import PricingServiceUnavailableError
from order_service.services.order_service import OrderService


class UnavailablePricingProvider:
    def calculate_price(self, **_):
        raise PricingServiceUnavailableError("pricing down")


@pytest.fixture()
def client():
    app = create_app()
    order_service = create_order_service(PricingMode.LOCAL)
    app.dependency_overrides[get_order_service] = lambda: order_service
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def unavailable_client():
    app = create_app()
    unavailable = OrderService(UnavailablePricingProvider())
    app.dependency_overrides[get_order_service] = lambda: unavailable
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def test_place_order_success(client):
    response = client.post(
        "/orders",
        json={"product_id": "laptop", "quantity": 1, "customer_type": "regular"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] == "laptop"
    assert data["quantity"] == 1
    assert data["customer_type"] == "regular"
    assert data["status"] == "CREATED"
    assert "order_id" in data
    assert Decimal(data["total_price"]) > 0


def test_place_order_premium_discount(client):
    regular = client.post(
        "/orders",
        json={"product_id": "laptop", "quantity": 1, "customer_type": "regular"},
    )
    premium = client.post(
        "/orders",
        json={"product_id": "laptop", "quantity": 1, "customer_type": "premium"},
    )
    assert regular.status_code == 201
    assert premium.status_code == 201
    assert Decimal(premium.json()["total_price"]) < Decimal(regular.json()["total_price"])


def test_place_order_unknown_product_returns_400(client):
    response = client.post(
        "/orders",
        json={"product_id": "nonexistent", "quantity": 1, "customer_type": "regular"},
    )
    assert response.status_code == 400
    assert "detail" in response.json()


def test_place_order_invalid_quantity_returns_400(client):
    response = client.post(
        "/orders",
        json={"product_id": "laptop", "quantity": 0, "customer_type": "regular"},
    )
    assert response.status_code == 400
    assert "detail" in response.json()


def test_place_order_unknown_customer_type_returns_400(client):
    response = client.post(
        "/orders",
        json={"product_id": "laptop", "quantity": 1, "customer_type": "vip"},
    )
    assert response.status_code == 400
    assert "detail" in response.json()


def test_get_order_success(client):
    post = client.post(
        "/orders",
        json={"product_id": "laptop", "quantity": 2, "customer_type": "regular"},
    )
    assert post.status_code == 201
    order_id = post.json()["order_id"]

    get = client.get(f"/orders/{order_id}")
    assert get.status_code == 200
    assert get.json()["order_id"] == order_id
    assert get.json()["quantity"] == 2


def test_get_order_not_found_returns_404(client):
    response = client.get("/orders/does-not-exist")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_place_order_missing_field_returns_422(client):
    response = client.post("/orders", json={"product_id": "laptop", "quantity": 1})
    assert response.status_code == 422


def test_pricing_service_unavailable_returns_503(unavailable_client):
    response = unavailable_client.post(
        "/orders",
        json={"product_id": "laptop", "quantity": 1, "customer_type": "regular"},
    )
    assert response.status_code == 503
    assert "detail" in response.json()


def test_lifespan_wires_order_service(monkeypatch):
    monkeypatch.setenv("PRICING_MODE", "local")
    app = create_app()
    with TestClient(app) as c:
        response = c.post(
            "/orders",
            json={"product_id": "laptop", "quantity": 1, "customer_type": "regular"},
        )
    assert response.status_code == 201
