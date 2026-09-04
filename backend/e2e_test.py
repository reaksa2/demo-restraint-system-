"""
End-to-end smoke test against the running API.
Builds the exact scenario from the spec and checks every permission
boundary + zone-pricing rule. Run with: python3 e2e_test.py
"""
import sys
import requests

BASE = "http://localhost:8000"
failures = []


def check(label, condition):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        failures.append(label)


def login(email, password):
    r = requests.post(f"{BASE}/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, f"login failed for {email}: {r.status_code} {r.text}"
    return r.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------
# 1. Level 1 logs in, creates Group A / Group B
# ---------------------------------------------------------------
level1_token = login("owner@example.com", "change-me-now")

r = requests.post(f"{BASE}/api/groups", json={"name": "Group A"}, headers=auth(level1_token))
check("Level1 creates Group A", r.status_code == 201)
group_a = r.json()

r = requests.post(f"{BASE}/api/groups", json={"name": "Group B"}, headers=auth(level1_token))
check("Level1 creates Group B", r.status_code == 201)
group_b = r.json()

# ---------------------------------------------------------------
# 2. Level 1 creates Brand A (Group A), Brand D (Group B)
# ---------------------------------------------------------------
r = requests.post(
    f"{BASE}/api/brands",
    json={"group_id": group_a["id"], "slug": "brand-a", "name_en": "Brand A", "name_kh": "ម៉ាកអេ"},
    headers=auth(level1_token),
)
check("Level1 creates Brand A in Group A", r.status_code == 201)
brand_a = r.json()

r = requests.post(
    f"{BASE}/api/brands",
    json={"group_id": group_a["id"], "slug": "brand-b", "name_en": "Brand B", "name_kh": "ម៉ាកប៊ី"},
    headers=auth(level1_token),
)
check("Level1 creates Brand B in Group A", r.status_code == 201)
brand_b = r.json()

r = requests.post(
    f"{BASE}/api/brands",
    json={"group_id": group_b["id"], "slug": "brand-d", "name_en": "Brand D", "name_kh": "ម៉ាកឌី"},
    headers=auth(level1_token),
)
check("Level1 creates Brand D in Group B", r.status_code == 201)
brand_d = r.json()

# ---------------------------------------------------------------
# 3. Level 1 creates a Level2 user for Group A
# ---------------------------------------------------------------
r = requests.post(
    f"{BASE}/api/users",
    json={
        "email": "manager_a@example.com",
        "password": "password123",
        "full_name": "Manager A",
        "role": "level2",
        "group_id": group_a["id"],
    },
    headers=auth(level1_token),
)
check("Level1 creates Level2 user for Group A", r.status_code == 201)

level2_token = login("manager_a@example.com", "password123")

# ---------------------------------------------------------------
# 4. Level2 (Group A) permission boundaries
# ---------------------------------------------------------------
r = requests.get(f"{BASE}/api/brands", headers=auth(level2_token))
brand_ids_seen = {b["id"] for b in r.json()}
check("Level2 sees Brand A + Brand B (their group)", {brand_a["id"], brand_b["id"]} <= brand_ids_seen)
check("Level2 does NOT see Brand D (other group)", brand_d["id"] not in brand_ids_seen)

r = requests.get(f"{BASE}/api/brands/{brand_d['id']}", headers=auth(level2_token))
check("Level2 blocked from reading Brand D directly (403)", r.status_code == 403)

r = requests.post(
    f"{BASE}/api/brands",
    json={"group_id": group_a["id"], "slug": "brand-x", "name_en": "X", "name_kh": "X"},
    headers=auth(level2_token),
)
check("Level2 cannot create brands (403)", r.status_code == 403)

r = requests.post(f"{BASE}/api/groups", json={"name": "Group C"}, headers=auth(level2_token))
check("Level2 cannot create groups (403)", r.status_code == 403)

# ---------------------------------------------------------------
# 5. Level2 sets up zones + a Level3 manager for Brand A
# ---------------------------------------------------------------
r = requests.post(
    f"{BASE}/api/brands/{brand_a['id']}/zones",
    json={"name_en": "Inside", "name_kh": "ខាងក្នុង"},
    headers=auth(level2_token),
)
check("Level2 creates INSIDE zone for Brand A", r.status_code == 201)
zone_inside = r.json()

r = requests.post(
    f"{BASE}/api/brands/{brand_a['id']}/zones",
    json={"name_en": "Outside", "name_kh": "ខាងក្រៅ"},
    headers=auth(level2_token),
)
check("Level2 creates OUTSIDE zone for Brand A", r.status_code == 201)
zone_outside = r.json()

r = requests.post(
    f"{BASE}/api/users",
    json={
        "email": "brandmgr_a@example.com",
        "password": "password123",
        "full_name": "Brand A Manager",
        "role": "level3",
        "brand_id": brand_a["id"],
    },
    headers=auth(level2_token),
)
check("Level2 creates Level3 manager for Brand A", r.status_code == 201)
level3_token = login("brandmgr_a@example.com", "password123")

# Level2 tries to create a Level3 manager for Brand D (other group) -> blocked
r = requests.post(
    f"{BASE}/api/users",
    json={
        "email": "brandmgr_d@example.com",
        "password": "password123",
        "full_name": "Brand D Manager",
        "role": "level3",
        "brand_id": brand_d["id"],
    },
    headers=auth(level2_token),
)
check("Level2 cannot create Level3 user for brand outside their group (403)", r.status_code == 403)

# ---------------------------------------------------------------
# 6. Level3 (Brand A) permission boundaries
# ---------------------------------------------------------------
r = requests.get(f"{BASE}/api/brands/{brand_b['id']}", headers=auth(level3_token))
check("Level3 blocked from Brand B, same group (403)", r.status_code == 403)

r = requests.get(f"{BASE}/api/brands/{brand_a['id']}", headers=auth(level3_token))
check("Level3 CAN access their own Brand A", r.status_code == 200)

r = requests.post(
    f"{BASE}/api/brands",
    json={"group_id": group_a["id"], "slug": "brand-y", "name_en": "Y", "name_kh": "Y"},
    headers=auth(level3_token),
)
check("Level3 cannot create brands (403)", r.status_code == 403)

# ---------------------------------------------------------------
# 7. Category + Food + zone pricing setup on Brand A
# ---------------------------------------------------------------
r = requests.post(
    f"{BASE}/api/brands/{brand_a['id']}/categories",
    json={"name_en": "Chicken", "name_kh": "មាន់"},
    headers=auth(level3_token),
)
check("Level3 creates category on their own brand", r.status_code == 201)
category = r.json()

r = requests.post(
    f"{BASE}/api/brands/{brand_a['id']}/foods",
    json={
        "category_id": category["id"],
        "name_en": "Fried Chicken",
        "name_kh": "មាន់បំពង",
        "description_en": "Delicious crispy fried chicken",
        "description_kh": "មាន់បំពងរសជាតិឆ្ងាញ់",
        "is_available": True,
    },
    headers=auth(level3_token),
)
check("Level3 creates food on their own brand", r.status_code == 201)
food = r.json()

r = requests.put(
    f"{BASE}/api/brands/{brand_a['id']}/foods/{food['id']}/prices",
    json={"zone_id": zone_inside["id"], "regular_price": "5.00"},
    headers=auth(level3_token),
)
check("Level3 sets INSIDE price = $5.00", r.status_code == 200)

r = requests.put(
    f"{BASE}/api/brands/{brand_a['id']}/foods/{food['id']}/prices",
    json={"zone_id": zone_outside["id"], "regular_price": "4.00"},
    headers=auth(level3_token),
)
check("Level3 sets OUTSIDE price = $4.00", r.status_code == 200)

# Admin view should show BOTH prices
r = requests.get(f"{BASE}/api/brands/{brand_a['id']}/foods/{food['id']}", headers=auth(level3_token))
prices = r.json()["prices"]
check("Admin view shows both zone prices", len(prices) == 2)

# ---------------------------------------------------------------
# 8. Level3 creates Staff A (INSIDE) and Staff B (OUTSIDE)
# ---------------------------------------------------------------
r = requests.post(
    f"{BASE}/api/users",
    json={
        "email": "staff_a@example.com",
        "password": "password123",
        "full_name": "Staff A",
        "role": "staff",
        "brand_id": brand_a["id"],
        "zone_id": zone_inside["id"],
    },
    headers=auth(level3_token),
)
check("Level3 creates Staff A (INSIDE)", r.status_code == 201)

r = requests.post(
    f"{BASE}/api/users",
    json={
        "email": "staff_b@example.com",
        "password": "password123",
        "full_name": "Staff B",
        "role": "staff",
        "brand_id": brand_a["id"],
        "zone_id": zone_outside["id"],
    },
    headers=auth(level3_token),
)
check("Level3 creates Staff B (OUTSIDE)", r.status_code == 201)

staff_a_token = login("staff_a@example.com", "password123")
staff_b_token = login("staff_b@example.com", "password123")

# ---------------------------------------------------------------
# 9. THE CRITICAL TEST: zone-based pricing, one price only
# ---------------------------------------------------------------
r = requests.get(f"{BASE}/api/menu", headers=auth(staff_a_token))
menu_a = r.json()
fried_chicken_a = next(f for f in menu_a["foods"] if f["name_en"] == "Fried Chicken")
check("Staff A (INSIDE) sees price = 5.00", fried_chicken_a["price"]["price"] == "5.00" or float(fried_chicken_a["price"]["price"]) == 5.0)
check("Staff A response contains only ONE price field (no outside_price)", "outside_price" not in fried_chicken_a and "inside_price" not in fried_chicken_a)

r = requests.get(f"{BASE}/api/menu", headers=auth(staff_b_token))
menu_b = r.json()
fried_chicken_b = next(f for f in menu_b["foods"] if f["name_en"] == "Fried Chicken")
check("Staff B (OUTSIDE) sees price = 4.00", float(fried_chicken_b["price"]["price"]) == 4.0)

# Raw payload check: dump the JSON and make sure "4.00"/"5.00" (the OTHER zone's price) never appears
import json
raw_a = json.dumps(menu_a)
raw_b = json.dumps(menu_b)
check("Staff A's raw response never contains OUTSIDE price 4.00", "4.00" not in raw_a and '"4.0"' not in raw_a)
check("Staff B's raw response never contains INSIDE price 5.00", "5.00" not in raw_b and '"5.0"' not in raw_b)

# Bilingual check: Khmer above English is a frontend concern, but both must be present
check("Menu food includes Khmer name", fried_chicken_a["name_kh"] == "មាន់បំពង")
check("Menu food includes English name", fried_chicken_a["name_en"] == "Fried Chicken")

# Staff cannot manage anything
r = requests.post(
    f"{BASE}/api/brands/{brand_a['id']}/foods",
    json={"name_en": "Hack Food", "name_kh": "X"},
    headers=auth(staff_a_token),
)
check("Staff cannot create foods (403)", r.status_code == 403)

r = requests.get(f"{BASE}/api/users", headers=auth(staff_a_token))
check("Staff cannot list users (403)", r.status_code == 403)

# ---------------------------------------------------------------
# 10. Clone Food List: Brand A -> Brand B (same group)
#     Brand B needs its own matching zones first (zones are per-brand;
#     clone matches them by name so prices carry over).
# ---------------------------------------------------------------
r = requests.post(
    f"{BASE}/api/brands/{brand_b['id']}/zones",
    json={"name_en": "Inside", "name_kh": "ខាងក្នុង"},
    headers=auth(level2_token),
)
check("Level2 creates INSIDE zone for Brand B", r.status_code == 201)
r = requests.post(
    f"{BASE}/api/brands/{brand_b['id']}/zones",
    json={"name_en": "Outside", "name_kh": "ខាងក្រៅ"},
    headers=auth(level2_token),
)
check("Level2 creates OUTSIDE zone for Brand B", r.status_code == 201)

r = requests.post(
    f"{BASE}/api/clone/foods",
    json={"source_brand_id": brand_a["id"], "target_brand_id": brand_b["id"]},
    headers=auth(level2_token),
)
check("Level2 clones Brand A -> Brand B", r.status_code == 200)
clone_result = r.json()
check("Clone reports 1 food cloned", clone_result["foods_cloned"] == 1)
check("Clone reports 1 category created", clone_result["categories_created"] == 1)
check("Clone has no warnings (zones matched by name)", clone_result["warnings"] == [])

r = requests.get(f"{BASE}/api/brands/{brand_b['id']}/foods", headers=auth(level2_token))
cloned_foods = r.json()
check("Brand B now has the cloned food", len(cloned_foods) == 1 and cloned_foods[0]["name_en"] == "Fried Chicken")
cloned_food_id = cloned_foods[0]["id"]
cloned_food_prices = {p["zone_name_en"]: float(p["regular_price"]) for p in cloned_foods[0]["prices"]}
check("Cloned food kept original prices (Inside=5, Outside=4)", cloned_food_prices.get("Inside") == 5.0 and cloned_food_prices.get("Outside") == 4.0)

# Independence check: change Brand B's cloned food price, verify Brand A unaffected
r = requests.get(f"{BASE}/api/brands/{brand_b['id']}/zones", headers=auth(level2_token))
brand_b_zones = {z["name_en"]: z["id"] for z in r.json()}
r = requests.put(
    f"{BASE}/api/brands/{brand_b['id']}/foods/{cloned_food_id}/prices",
    json={"zone_id": brand_b_zones["Inside"], "regular_price": "6.00"},
    headers=auth(level2_token),
)
check("Level2 changes Brand B's cloned food price to 6.00", r.status_code == 200)

r = requests.get(f"{BASE}/api/brands/{brand_a['id']}/foods/{food['id']}", headers=auth(level2_token))
brand_a_food_after = r.json()
inside_price_a = next(p["regular_price"] for p in brand_a_food_after["prices"] if p["zone_name_en"] == "Inside")
check("Brand A's original price UNCHANGED (still 5.00) — clone is independent", float(inside_price_a) == 5.0)

# Clone into a brand with NO zones at all -> food still clones, price is
# skipped and reported as a warning (never silently dropped without saying so)
r = requests.post(
    f"{BASE}/api/brands",
    json={"group_id": group_a["id"], "slug": "brand-c", "name_en": "Brand C", "name_kh": "ម៉ាកស៊ី"},
    headers=auth(level1_token),
)
brand_c = r.json()
r = requests.post(
    f"{BASE}/api/clone/foods",
    json={"source_brand_id": brand_a["id"], "target_brand_id": brand_c["id"]},
    headers=auth(level2_token),
)
check("Clone into brand with no zones still succeeds", r.status_code == 200)
clone_result_c = r.json()
check("Clone into zone-less brand reports a warning", len(clone_result_c["warnings"]) == 2)

# Level2 cannot clone across groups
r = requests.post(
    f"{BASE}/api/clone/foods",
    json={"source_brand_id": brand_a["id"], "target_brand_id": brand_d["id"]},
    headers=auth(level2_token),
)
check("Level2 cannot clone into a brand outside their group (403)", r.status_code == 403)

# ---------------------------------------------------------------
# Summary
# ---------------------------------------------------------------
print("\n" + "=" * 60)
if failures:
    print(f"{len(failures)} FAILURE(S):")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("ALL CHECKS PASSED")
