import os

s3_objects_response = None

with open(
    os.path.join(os.path.dirname(__file__), "s3_objects.xml"), "r", encoding="utf-8"
) as f:
    s3_objects_response = f.read()
