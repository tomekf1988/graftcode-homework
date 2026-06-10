from decimal import Decimal

from pricing_service.domain.product import Product


class ProductCatalog:

    def __init__(self):
        self._products = {
            "laptop": Product(
                id="laptop",
                name="Laptop",
                unit_price=Decimal("5000"),
            ),
            "mouse": Product(
                id="mouse",
                name="Mouse",
                unit_price=Decimal("150"),
            ),
            "keyboard": Product(
                id="keyboard",
                name="Keyboard",
                unit_price=Decimal("300"),
            ),
        }

    def get(self, product_id: str) -> Product | None:
        return self._products.get(product_id)