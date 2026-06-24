"""
Test graft pricing client in inMemory mode directly (no Vision, no gg runtime).
Run: docker exec order-graft python3 /usr/app/test_inmemory.py
"""
import sys
import os

sys.path.insert(0, '/usr/app')
os.environ.setdefault('PRICING_MODE', 'local')

print("=== inMemory mode test ===")

# 1. Verify module is accessible
from graft_pypi_pricing_service_graft.graft.pypi.pricing_service_graft.graft_config import GraftConfig
print(f"GraftConfig.host (default): {GraftConfig.host}")
print(f"GraftConfig.module: {GraftConfig.module}")
import os.path
graft_dir = os.path.join(GraftConfig.module, 'graft')
print(f"Module dir exists: {os.path.isdir(GraftConfig.module)}")
print(f"pricing_service_graft.py exists: {os.path.isfile(os.path.join(graft_dir, 'pricing_service_graft.py'))}")

# 2. Test graft client directly
from graft_pypi_pricing_service_graft.pricingservicegraft import PricingServiceGraft
import json

cases = [
    ("laptop", 2, "premium"),
    ("laptop", 2, "regular"),
    ("laptop", 0, "premium"),      # should fail: invalid quantity
    ("unknown", 1, "premium"),     # should fail: unknown product
    ("laptop", 1, "standard"),     # should fail: unsupported customer type
]

for product_id, quantity, customer_type in cases:
    try:
        client = PricingServiceGraft()
        result = client.calculate_price(product_id, quantity, customer_type)
        data = json.loads(result)
        print(f"[OK] {product_id}/{quantity}/{customer_type} → total={data['total_price']}")
    except Exception as e:
        print(f"[ERR] {product_id}/{quantity}/{customer_type} → {type(e).__name__}: {e}")
    finally:
        GraftConfig.rtm_ctx = None  # reset between calls

print("=== done ===")
