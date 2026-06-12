from order_service.bootstrap.factory import create_order_service_from_settings
from order_service.config.settings import load_settings
from order_service.domain.exceptions import InvalidOrderRequestError, OrderNotFoundError
from graft_pypi_graftcode_homework.pricingservicegraft import PricingServiceGraft
from graft_pypi_graftcode_homework.graft.pypi.graftcode_homework.graft_config import GraftConfig

GraftConfig.host = "ws://localhost/ws"
    
service = PricingServiceGraft()
result = service.calculate_price("laptop", 2, "premium")
print(result)
    

def main() -> None:
    GraftConfig.host = "ws://localhost/ws"
    service = PricingServiceGraft()
    result = service.calculate_price("laptop", 2, "premium")
    print(result)
    
    return
    settings = load_settings()
    service = create_order_service_from_settings(settings)

    print(f"Running with pricing_mode={settings.pricing_mode.value}\n")

    # Scenario 1: Happy path
    print("--- Scenario: happy path ---")
    result = service.place_order(
        product_id="laptop",
        quantity=2,
        customer_type="premium",
    )
    print(result)
    happy_path_order_id = result.order_id

    # Scenario 2: Product not found
    print("\n--- Scenario: product not found ---")
    try:
        service.place_order(
            product_id="unknown_product",
            quantity=1,
            customer_type="regular",
        )
    except InvalidOrderRequestError as exc:
        print(f"InvalidOrderRequestError: {exc}")

    # Scenario 3: Invalid quantity
    print("\n--- Scenario: invalid quantity ---")
    try:
        service.place_order(
            product_id="mouse",
            quantity=0,
            customer_type="regular",
        )
    except InvalidOrderRequestError as exc:
        print(f"InvalidOrderRequestError: {exc}")

    # Scenario 4: Unknown customer type
    print("\n--- Scenario: unknown customer type ---")
    try:
        service.place_order(
            product_id="keyboard",
            quantity=1,
            customer_type="vip",
        )
    except InvalidOrderRequestError as exc:
        print(f"InvalidOrderRequestError: {exc}")

    # Scenario 5: Retrieve placed order
    print("\n--- Scenario: retrieve placed order ---")
    order = service.get_order(happy_path_order_id)
    print(order)

    # Scenario 6: Order not found
    print("\n--- Scenario: order not found ---")
    try:
        service.get_order("nonexistent-id")
    except OrderNotFoundError as exc:
        print(f"OrderNotFoundError: {exc}")


if __name__ == "__main__":
    main()
