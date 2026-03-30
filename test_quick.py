#!/usr/bin/env python3
"""
Quick API test script — ручная проверка поднятого backend.
Запуск из корня проекта: python test_quick.py
Требуется: pip install requests
"""
from __future__ import annotations

import os
import sys
import time

import requests

BASE_URL = os.environ.get("QUICK_TEST_BASE_URL", "http://127.0.0.1:8000")
ADMIN_KEY = os.environ.get("ADMIN_API_KEY", "dev-admin-key-change-me")


def main() -> int:
    suffix = str(int(time.time()))[-6:]
    username = f"quick_{suffix}"
    password = "test12345"

    try:
        r = requests.get(f"{BASE_URL}/health", timeout=10)
        r.raise_for_status()
        print(f"✓ Health: {r.json()}")
    except requests.RequestException as e:
        print(f"✗ Health failed: {e}")
        return 1

    try:
        r = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"username": username, "password": password},
            timeout=10,
        )
        print(f"✓ Register: {r.status_code} {r.text[:120]}")
        r.raise_for_status()

        r = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": username, "password": password},
            timeout=10,
        )
        r.raise_for_status()
        token = r.json().get("access_token")
        print(f"✓ Login: token={token[:50]}...")

        r = requests.post(
            f"{BASE_URL}/api/prediction",
            json={"video_id": "test", "video_timestamp": 10.5, "event_type": "goal"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        print(f"✓ Prediction: {r.status_code}")
        r.raise_for_status()

        r = requests.get(f"{BASE_URL}/api/leaderboard", timeout=10)
        r.raise_for_status()
        print(f"✓ Leaderboard: {len(r.json())} players")

        r = requests.get(f"{BASE_URL}/api/stats", timeout=10)
        r.raise_for_status()
        print(f"✓ Stats: {r.json()}")

        r = requests.post(
            f"{BASE_URL}/api/event",
            json={"video_id": "test", "timestamp": 12.0, "event_type": "goal"},
            headers={"X-Admin-Key": ADMIN_KEY},
            timeout=10,
        )
        print(f"✓ Event: {r.status_code}")
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"✗ API error: {e}")
        return 1

    print("\n✅ All quick checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
