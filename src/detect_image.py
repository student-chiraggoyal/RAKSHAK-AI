from ultralytics import YOLO

model = YOLO("yolo26n.pt")

results = model.predict(
    source="images/test.jpg",
    conf=0.40,
    save=True
)

print("Detection completed!")