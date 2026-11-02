import json
from fastapi.testclient import TestClient
from src.main import app

def run_verification():
    print("==================================================")
    print(" LIVE FAKESTORE API INTEGRATION VERIFICATION")
    print("==================================================")
    
    with TestClient(app) as client:
        # 1. Health check
        print("\n[1] Testing /health ...")
        res = client.get("/health")
        print(f"Status: {res.status_code}")
        print(f"Body: {res.json()}")
        assert res.status_code == 200

        # 2. List products with limit
        print("\n[2] Testing GET /api/v1/products?limit=2 ...")
        res = client.get("/api/v1/products?limit=2")
        print(f"Status: {res.status_code}")
        products = res.json()
        print(f"Fetched {len(products)} products:")
        for p in products:
            print(f"  - ID {p['id']}: {p['title'][:40]}... (${p['price']}) Category: {p['category']}")
        assert res.status_code == 200
        assert len(products) == 2

        # 3. Get single product by ID
        print("\n[3] Testing GET /api/v1/products/1 ...")
        res = client.get("/api/v1/products/1")
        print(f"Status: {res.status_code}")
        prod = res.json()
        print(f"Product: ID={prod['id']}, Title={prod['title']}, Rating={prod['rating']}")
        assert res.status_code == 200
        assert prod["id"] == 1

        # 4. List categories
        print("\n[4] Testing GET /api/v1/products/categories ...")
        res = client.get("/api/v1/products/categories")
        print(f"Status: {res.status_code}")
        categories = res.json()
        print(f"Categories: {categories}")
        assert res.status_code == 200
        assert "jewelery" in categories

        # 5. List products by category
        print("\n[5] Testing GET /api/v1/products/category/jewelery?limit=2 ...")
        res = client.get("/api/v1/products/category/jewelery?limit=2")
        print(f"Status: {res.status_code}")
        jewelery_items = res.json()
        print(f"Fetched {len(jewelery_items)} items in 'jewelery':")
        for item in jewelery_items:
            print(f"  - {item['title'][:40]}... (${item['price']})")
        assert res.status_code == 200
        assert all(item["category"] == "jewelery" for item in jewelery_items)

        # 6. Non-existent product (404 test)
        print("\n[6] Testing GET /api/v1/products/99999 (Non-existent ID) ...")
        res = client.get("/api/v1/products/99999")
        print(f"Status: {res.status_code}")
        print(f"Detail: {res.json()}")
        assert res.status_code == 404

    print("\n==================================================")
    print(" ALL LIVE VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_verification()
