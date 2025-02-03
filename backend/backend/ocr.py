from PIL import Image
import numpy as np
import onnxruntime as ort
import cv2


class YOLOv11:
    """YOLOv8 object detection model class for handling inference and visualization."""

    def __init__(self, onnx_model: str, confidence_thres: float, iou_thres: float):
        """
        Initializes an instance of the YOLOv8 class.

        Args:
            onnx_model: Path to the ONNX model.
            input_image: Path to the input image.
            confidence_thres: Confidence threshold for filtering detections.
            iou_thres: IoU (Intersection over Union) threshold for non-maximum suppression.
        """
        self.onnx_model = onnx_model
        self.confidence_thres = confidence_thres
        self.iou_thres = iou_thres

        self.session = ort.InferenceSession(
            self.onnx_model, providers=["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name

    def __call__(self, img: Image.Image):
        """
        Performs inference using an ONNX model and returns the output image with drawn detections.

        Returns:
            output_img: The output image with drawn detections.
        """

        # Preprocess the image data
        img_width, img_height = img.size

        # Resize the image to match the input shape
        img = img.resize((640, 640))

        # Normalize the image data by dividing it by 255.0
        image_data = np.array(img) / 255.0

        # Transpose the image to have the channel dimension as the first dimension
        image_data = np.transpose(image_data, (2, 0, 1))  # Channel first

        # Expand the dimensions of the image data to match the expected input shape
        image_data = np.expand_dims(image_data, axis=0).astype(np.float32)

        # Run inference using the preprocessed image data
        outputs = self.session.run(None, {self.input_name: image_data})

        # Transpose and squeeze the output to match the expected shape
        outputs = np.transpose(np.squeeze(outputs))

        # Get the number of rows in the outputs array
        rows = outputs.shape[0]

        # Lists to store the bounding boxes, scores, and class IDs of the detections
        boxes = []
        scores = []

        # Iterate over each row in the outputs array
        for i in range(rows):
            # Extract the class scores from the current row
            max_score = outputs[i][4]

            # If the maximum score is above the confidence threshold
            if max_score >= self.confidence_thres:

                # Extract the bounding box coordinates from the current row
                x, y, w, h = outputs[i][0], outputs[i][1], outputs[i][2], outputs[i][3]

                # Calculate the scaled coordinates of the bounding box
                left = int(x - w / 2)
                top = int(y - h / 2)
                w = int(w)
                h = int(h)

                # Add the class ID, score, and box coordinates to the respective lists
                scores.append(max_score)
                boxes.append([left, top, w, h])

        # Apply non-maximum suppression to filter out overlapping bounding boxes
        indices = cv2.dnn.NMSBoxes(boxes, scores, self.confidence_thres, self.iou_thres)

        # Iterate over the selected indices after non-maximum suppression
        boxes = [boxes[i] for i in indices]
        scores = [float(scores[i]) for i in indices]

        # Calculate the scaling factors for the bounding box coordinates
        x_factor = img_width / 640
        y_factor = img_height / 640

        return [
            {
                "conf": score,
                "x": box[0] * x_factor,
                "y": box[1] * y_factor,
                "w": box[2] * x_factor,
                "h": box[3] * y_factor,
            }
            for box, score in zip(boxes, scores)
        ]
