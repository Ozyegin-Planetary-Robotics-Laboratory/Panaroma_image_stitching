import cv2
import glob
import numpy as np
import pyzed.sl as sl
from PIL import Image


def placeSymbol(image, symbol):
    # Define the coordinates where you want to place the symbol
    x, y = 760, 50

    # Define the font settings
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 4
    font_thickness = 7
    font_color = (0, 255, 0)  # Green color

    # Get the size of the symbol text
    text_size = cv2.getTextSize(symbol, font, font_scale, font_thickness)[0]

    # Calculate the position to place the text so that it's centered at (x, y)
    text_x = x - text_size[0] // 2
    text_y = y + text_size[1] // 2

    # Place the symbol on the image
    cv2.putText(image, symbol, (text_x, text_y), font, font_scale, font_color, font_thickness)


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


# Basic class to handle the timestamp of the different sensors to know if it is a new sensors_data or an old one
class TimestampHandler:
    def __init__(self):
        self.t_imu = sl.Timestamp()
        self.t_baro = sl.Timestamp()
        self.t_mag = sl.Timestamp()

    ##
    # check if the new timestamp is higher than the reference one, and if yes, save the current as reference
    def is_new(self, sensor):
        if isinstance(sensor, sl.IMUData):
            new_ = (sensor.timestamp.get_microseconds() > self.t_imu.get_microseconds())
            if new_:
                self.t_imu = sensor.timestamp
            return new_
        elif isinstance(sensor, sl.MagnetometerData):
            new_ = (sensor.timestamp.get_microseconds() > self.t_mag.get_microseconds())
            if new_:
                self.t_mag = sensor.timestamp
            return new_
        elif isinstance(sensor, sl.BarometerData):
            new_ = (sensor.timestamp.get_microseconds() > self.t_baro.get_microseconds())
            if new_:
                self.t_baro = sensor.timestamp
            return new_


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
    magnetometerdata = []

    while i < 10:
        # Grab an image, a RuntimeParameters object must be given to grab()
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:

            # Used to store the sensors timestamp to know if the sensors_data is a new one or not
            ts_handler = TimestampHandler()

            # Get Sensor Data for 5 seconds
            sensors_data = sl.SensorsData()
            if zed.get_sensors_data(sensors_data, sl.TIME_REFERENCE.CURRENT) == sl.ERROR_CODE.SUCCESS:
                # Check if the data has been updated since the last time
                # IMU is the sensor with the highest rate
                if ts_handler.is_new(sensors_data.get_imu_data()):

                    # Check if Magnetometer data has been updated (not the same frequency than IMU)
                    if ts_handler.is_new(sensors_data.get_magnetometer_data()):
                        magnetic_heading = sensors_data.get_magnetometer_data().magnetic_heading
                        magnetometerdata.append(magnetic_heading)

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
            print(magnetometerdata)

    # Magnetometerdata array and images array matched with index.
    # After finding the "northest" angle,N symbol placed to the image with the most north angle
    placeSymbol(images_all[findNorthestPicturesIndex(magnetometerdata)], "N")

    # Close the camera
    zed.close()


def findNorthestPicturesIndex(angles):
    # Normalize angles to be in the range [0, 180]
    normalized_angles = [(angle % 360) if angle <= 180 else (angle % 360 - 360) for angle in angles]

    # Find the maximum normalized angle
    max_angle = max(normalized_angles)

    # Convert the maximum normalized angle back to the original range [0, 360]
    northest_angle = (max_angle + 360) % 360

    # Return the northest picture's index
    return normalized_angles.index(max_angle)


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
    main()
