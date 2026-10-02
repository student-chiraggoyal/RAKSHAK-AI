from ultralytics import YOLO


def main():

    # Load pretrained YOLO model
    model = YOLO("yolo26n.pt")

    # Train the model
    results = model.train(
        data="dataset/data.yaml",
        epochs=100,
        imgsz=640,
        batch=8,
        device=0,
        workers=0,

        # Save training results directly inside:
        # D:\RakshakAI\runs\rakshakai_train
        project=r"D:\RakshakAI\runs",
        name="rakshakai_train",

        exist_ok=True
    )

    print("\nTraining completed!")
    print("Best model saved at:")
    print(r"D:\RakshakAI\runs\rakshakai_train\weights\best.pt")


if __name__ == "__main__":
    main()