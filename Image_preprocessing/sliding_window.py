import cv2
import imutils
import matplotlib.pyplot as plt


def pyramid(image, scale=1.5, minSize=(30, 30)):
    """
    Generate an image pyramid.

    Parameters:
    - image: Input image (NumPy array, e.g., from OpenCV)
    - scale: Factor by which the image is resized at each layer
    - minSize: Minimum allowed size (width, height) of the image

    Yields:
    - The original image followed by progressively smaller resized versions
    """

    # Yield the original image first
    yield image 

    while True:
        # Compute the new width by reducing it using the scale factor
        w = int(image.shape[1] / scale)

        # Resize the image while maintaining aspect ratio
        image = imutils.resize(image, width=w)

        # Stop if the resized image is smaller than the minimum size
        if image.shape[0] < minSize[1] or image.shape[1] < minSize[0]:
            break 

        # Yield the resized image
        yield image

def sliding_window(image, stepSize=30, windowSize=[45, 45]):
    """
    Slide a fixed-size window across the image.

    Yields:
    - (x_min, y_min, x_max, y_max), window
    """

    for y in range(0, image.shape[0], stepSize):
        for x in range(0, image.shape[1], stepSize):

            x_end = x + windowSize[0]
            y_end = y + windowSize[1]

            # Skip if window goes outside image boundary
            if x_end > image.shape[1] or y_end > image.shape[0]:
                continue

            window = image[y:y_end, x:x_end]

            yield (x, y, x_end, y_end), window

# def sliding_window(image, stepSize, windowSize):
#     for y in range(0, image.shape[0], stepSize):
#         for x in range(0, image.shape[1], stepSize):

#             x_end = min(x + windowSize[0], image.shape[1])
#             y_end = min(y + windowSize[1], image.shape[0])

#             window = image[y:y_end, x:x_end]

#             yield (x, y, x_end, y_end), window

img_path = "img1.jpg"
root_img = cv2.imread(img_path)
root_img = cv2.resize(root_img, (1920, 1080))
# root_img = cv2.resize(root_img, (1920, 1080))
window_size = [128, 128]
step_size = int(window_size[0]*0.8)
is_first = True
coord_first = None
count = 0
for coord, img in sliding_window(root_img, step_size, window_size):
    count+=1
    if is_first:
        is_first = False
        coord_first = coord
    else:
        cv2.rectangle(root_img, coord[:2], coord[2:], (0, 255, 0), 2)
\

cv2.rectangle(root_img, coord_first[:2], coord_first[2:], (255, 0, 0), 2)
cv2.imshow("window", root_img)
cv2.waitKey(0) 
cv2.destroyAllWindows()
print("Number of windows: ", count)