```python
    try:
        object_count, annotated_image = self.detect_objects(image_path)
        if annotated_image is not None:
            return object_count
    except Exception as e:
        print(f"Error during object detection: {e}")
        return 0

```
