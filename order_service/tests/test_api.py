from decimal import Decimal
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from order_service.api.app import create_app
from order_service.domain.exceptions import (
    InvalidOrderRequestError,
    PricingServiceUnavailableError,
)
from order_service.services.order_service import OrderService
from order_service.tests.fakes.fake_pricing_provider import FakePricingProvider


class InvalidRequestPricingProvider:
    def calculate_price(self, product_id, quantity, customer_type):
        raise InvalidOrderRequestError("bad request")


class UnavailablePricingProvider:
    def calculate_price(self, product_id, quantity, customer_type):
        raise PricingServiceUnavailableError("pricing down")


def _client_with(provider):
    app = create_app()
    fake_service = OrderService(provider)
    with patch(
        "order_service.api.app.create_order_service_from_settings",
        return_value=fake_service,
    ):
        with TestClient(app) as c:
            yield c


@pytest.fixture()
def client():
    yield from _client_with(FakePricingProvider())


@pytest.fixture()
def invalid_client():
    yield from _client_with(InvalidRequestPricingProvider())


@pytest.fixture()
def unavailable_client():
    yield from _client_with(UnavailablePricingProvider())


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


def test_place_order_returns_400_on_invalid_request(invalid_client):
    response = invalid_client.post(
        "/orders",
        json={"product_id": "nonexistent", "quantity": 1, "customer_type": "regular"},
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
