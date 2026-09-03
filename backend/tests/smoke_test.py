"""
Smoke test — Verifica que los 3 endpoints principales responden correctamente.
Correr con: python backend/tests/smoke_test.py
El backend debe estar corriendo en http://localhost:8000
"""

import sys
import json
import base64
import httpx

BASE_URL = "http://localhost:8000"

GUAYAQUIL_LAT = -2.1894
GUAYAQUIL_LNG = -79.8891


def check(label: str, condition: bool, detail: str = "") -> bool:
    icon = "OK" if condition else "FAIL"
    print(f"  [{icon}] {label}" + (f" — {detail}" if detail else ""))
    return condition


def test_health():
    print("\n--- /health ---")
    r = httpx.get(f"{BASE_URL}/health", timeout=5)
    data = r.json()
    ok = check("Status 200", r.status_code == 200)
    ok &= check("healthy", data.get("status") == "healthy")
    ok &= check("features_loaded > 0", data.get("features_loaded", 0) > 0,
                str(data.get("features_loaded")))
    return ok


def test_get_foci():
    print("\n--- GET /api/foci ---")
    r = httpx.get(f"{BASE_URL}/api/foci", timeout=5)
    data = r.json()
    features = data.get("features", [])
    ok = check("Status 200", r.status_code == 200)
    ok &= check("GeoJSON FeatureCollection", data.get("type") == "FeatureCollection")
    ok &= check("Al menos 40 focos cargados", len(features) >= 40, str(len(features)))
    if features:
        props = features[0].get("properties", {})
        ok &= check("ire_score presente", "ire_score" in props)
        ok &= check("risk_level presente", "risk_level" in props)
    return ok


def test_create_report():
    print("\n--- POST /api/reports ---")
    payload = {
        "latitude": GUAYAQUIL_LAT,
        "longitude": GUAYAQUIL_LNG,
        "notes": "Smoke test — llanta con agua estancada",
    }
    r = httpx.post(f"{BASE_URL}/api/reports", json=payload, timeout=10)
    data = r.json()
    ok = check("Status 201", r.status_code == 201)
    ok &= check("ID generado", "id" in data, data.get("id", ""))
    ok &= check("risk_assessment presente", "risk_assessment" in data)
    ok &= check("climate presente", "climate" in data)
    ok &= check("classification presente", "classification" in data)
    if "risk_assessment" in data:
        ra = data["risk_assessment"]
        ok &= check("ire_score numerico", isinstance(ra.get("ire_score"), (int, float)),
                    str(ra.get("ire_score")))
        ok &= check("risk_level valido", ra.get("risk_level") in {"LOW", "MEDIUM", "CRITICAL"},
                    ra.get("risk_level", ""))
    return ok


def test_dispatch():
    print("\n--- POST /api/routes/dispatch ---")
    payload = {
        "depot_coordinates": [GUAYAQUIL_LNG, GUAYAQUIL_LAT],
        "max_foci": 5,
    }
    r = httpx.post(f"{BASE_URL}/api/routes/dispatch", json=payload, timeout=10)
    data = r.json()
    ok = check("Status 200", r.status_code == 200)
    ok &= check("brigade_id presente", "brigade_id" in data)
    ok &= check("itinerary presente", "itinerary" in data)
    ok &= check("route_geometry presente", "route_geometry" in data)
    ok &= check("total_distance_km > 0", data.get("total_distance_km", 0) > 0,
                str(data.get("total_distance_km")))
    return ok


if __name__ == "__main__":
    print("=" * 50)
    print("AedesGuard — Smoke Test")
    print("=" * 50)

    results = [
        test_health(),
        test_get_foci(),
        test_create_report(),
        test_dispatch(),
    ]

    passed = sum(results)
    total = len(results)
    print(f"\n{'=' * 50}")
    print(f"Resultado: {passed}/{total} tests pasaron")

    if passed == total:
        print("Backend listo para el hackathon.")
        sys.exit(0)
    else:
        print("Hay errores — revisar los logs del servidor.")
        sys.exit(1)
