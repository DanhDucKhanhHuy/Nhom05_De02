"""Kiểm tra lệnh demo độc lập, bao gồm đầu ra tiếng Việt trên Windows."""
import subprocess
import sys
from pathlib import Path

from src.model.predict import MODEL_PATH


def test_demo_runs():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, str(root / "demo.py")], cwd=root,
                            capture_output=True, encoding="utf-8", check=False)
    assert result.returncode == 0, result.stderr
    expected_cnn_status = "đã có artifact" if MODEL_PATH.is_file() else "chưa có mô hình"
    assert f"CN3 — {expected_cnn_status}" in result.stdout
    assert "CN1 — leo đồi: quãng đường" in result.stdout
    assert "Không có số dự đoán mặc định" not in result.stdout
    assert "CN2:" in result.stdout
    assert "CN2 chẩn đoán tích hợp: chưa cài đặt" not in result.stdout
