# check_version.py
import importlib.util
import os

file_path = os.path.join("lithops", "lithops", "version.py")
spec = importlib.util.spec_from_file_location("version_module", file_path)
version_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(version_module)

print("Contents of version.py:", dir(version_module))
print("Attributes:", [attr for attr in dir(version_module) if not attr.startswith("__")])