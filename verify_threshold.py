import requests

BASE_URL = "http://localhost:5000/api"

def test_product_threshold():
    print("Testing Product Threshold Logic...")
    
    # 1. Create Product with Threshold
    new_p = {
        "name": "Test Threshold Item",
        "sku": "THRESH001",
        "price": 50000,
        "stock_quantity": 5,
        "low_stock_threshold": 8,
        "category_id": 1
    }
    
    try:
        # Get a category first
        cats = requests.get(f"{BASE_URL}/products/categories").json()
        if not cats:
            print("No categories found, creating one.")
            c = requests.post(f"{BASE_URL}/products/categories", json={"name": "Test Cat"})
            new_p["category_id"] = c.json()['id']
        else:
            new_p["category_id"] = cats[0]['id']

        print(f"Creating product: {new_p['name']}")
        resp = requests.post(f"{BASE_URL}/products/", json=new_p)
        if resp.status_code == 201:
            data = resp.json()
            pid = data['id']
            print(f"Created Product ID: {pid}")
            if data.get('low_stock_threshold') == 8:
                print("SUCCESS: low_stock_threshold saved correctly.")
            else:
                print(f"FAILED: low_stock_threshold mismatch: {data.get('low_stock_threshold')}")
            
            # 2. Update Threshold
            print("Updating threshold to 15...")
            up_resp = requests.put(f"{BASE_URL}/products/{pid}", json={"low_stock_threshold": 15})
            if up_resp.status_code == 200:
                up_data = up_resp.json()
                if up_data.get('low_stock_threshold') == 15:
                    print("SUCCESS: Threshold updated to 15.")
                else:
                    print(f"FAILED: Update mismatch: {up_data.get('low_stock_threshold')}")
            else:
                print(f"FAILED to update: {up_resp.status_code}")

            # Cleanup
            requests.delete(f"{BASE_URL}/products/{pid}")
            print("Cleanup: Deleted test product.")
            
        else:
            print(f"FAILED to create product: {resp.status_code} {resp.text}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_product_threshold()
