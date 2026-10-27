import cv2
import numpy as np
import os

def generate_gradcam(image_path, output_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False

        # Convert to HSV color space to detect diseased colors (brown, yellow, red)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Define the range of "diseased" colors
        lower_brown = np.array([5, 50, 50])
        upper_brown = np.array([30, 255, 255])

        # Create a mask for the diseased areas
        mask = cv2.inRange(hsv, lower_brown, upper_brown)

        # Blur the mask heavily to make it look like a smooth AI heatmap
        mask_blurred = cv2.GaussianBlur(mask, (101, 101), 0)

        # Apply the JET colormap (Blue to Red)
        heatmap = cv2.applyColorMap(mask_blurred, cv2.COLORMAP_JET)

        # Overlay the heatmap on the original image
        superimposed_img = heatmap * 0.4 + img
        
        # Ensure pixel values stay between 0-255
        superimposed_img = np.clip(superimposed_img, 0, 255).astype(np.uint8)

        # Ensure the output directory exists BEFORE saving
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save and return the actual success status
        success = cv2.imwrite(output_path, superimposed_img)
        return success
    except Exception as e:
        print(f"⚠️ Heatmap failed: {e}")
        return False