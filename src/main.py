import cv2
import glob
import numpy as np
import pyzed.sl as sl
from PIL import Image


def rgba2rgb(rgba, background=(255, 255, 255)):
    row, col, ch = rgba.shape

    if ch == 3:
        return rgba

    assert ch == 4, 'RGBA image has 4 channels.'

    rgb = np.zeros((row, col, 3), dtype='float32')
    r, g, b, a = rgba[:, :, 0], rgba[:, :, 1], rgba[:, :, 2], rgba[:, :, 3]

    a = np.asarray(a, dtype='float32') / 255.0

    R, G, B = background

    rgb[:, :, 0] = r * a + (1.0 - a) * R
    rgb[:, :, 1] = g * a + (1.0 - a) * G
    rgb[:, :, 2] = b * a + (1.0 - a) * B

    return np.asarray(rgb, dtype='uint8')


def main():
    # Create a Camera object
    zed = sl.Camera()

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD2K  # Use HD2K video mode
    init_params.camera_fps = 15  # Set fps at 15

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Camera Open : " + repr(err) + ". Exit program.")
        exit()

    # Capture 5 frames and stop
    i = 0
    image = sl.Mat()
    runtime_parameters = sl.RuntimeParameters()
    images_all = np.array([])

    while i < 150:
        # Grab an image, a RuntimeParameters object must be given to grab()
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            # A new image is available if grab() returns SUCCESS
            print(i)
            zed.retrieve_image(image, sl.VIEW.LEFT)
            images_all = np.append(images_all, image.get_data())
            im = Image.fromarray(rgba2rgb(image.get_data()))
            image_path = "C:/Users/taalp/Documents/GitHub/Panaroma_image_stitching/unstitchedImages"
            im.save(f"{image_path}/" + str(i + 1) + '.jpeg')
            timestamp = zed.get_timestamp(
                sl.TIME_REFERENCE.CURRENT)  # Get the timestamp at the time the image was captured
            print("Image resolution: {0} x {1} || Image timestamp: {2}\n".format(image.get_width(), image.get_height(),
                                                                                 timestamp.get_milliseconds()))
            i = i + 1

    # Close the camera
    zed.close()


def stitch():
    image_paths = glob.glob('C:/Users/taalp/Documents/GitHub/Panaroma_image_stitching/unstitchedImages/*.jpeg')
    images = []

    for image in image_paths:
        img = cv2.imread(image)
        images.append(img)

    imageStitcher = cv2.Stitcher_create()

    error, stitched_img = imageStitcher.stitch(images)

    if not error:
        cv2.imwrite("stitchedOutput.png", stitched_img)
        cv2.imshow("Stitched Image", stitched_img)


if __name__ == "__main__":
    stitch()
