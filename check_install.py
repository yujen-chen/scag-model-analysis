"""
Quick script to check if the package is installed in editable mode
檢查 package 是否以可編輯模式安裝
"""

try:
    import src
    print("[OK] 'src' package is importable!")
    print(f"   Package location: {src.__file__}")

    from src.data_loader import DataLoader
    print("[OK] Can import DataLoader from src")

    from src import config
    print("[OK] Can import config from src")

    print("\n[SUCCESS] Your package is correctly installed!")

except ImportError as e:
    print(f"[FAIL] Import failed: {e}")
    print("\n[ACTION] You need to run: uv pip install -e .")
