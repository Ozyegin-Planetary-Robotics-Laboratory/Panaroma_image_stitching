import pyzed.sl as sl
import time

# Basic class to handle the timestamp of the different sensors to know if it is a new sensors_data or an old one
class TimestampHandler:
    def __init__(self):
        self.t_imu = sl.Timestamp()
        self.t_baro = sl.Timestamp()
        self.t_mag = sl.Timestamp()

    ##
    # check if the new timestamp is higher than the reference one, and if yes, save the current as reference
    def is_new(self, sensor):
        if (isinstance(sensor, sl.IMUData)):
            new_ = (sensor.timestamp.get_microseconds() > self.t_imu.get_microseconds())
            if new_:
                self.t_imu = sensor.timestamp
            return new_
        elif (isinstance(sensor, sl.MagnetometerData)):
            new_ = (sensor.timestamp.get_microseconds() > self.t_mag.get_microseconds())
            if new_:
                self.t_mag = sensor.timestamp
            return new_
        elif (isinstance(sensor, sl.BarometerData)):
            new_ = (sensor.timestamp.get_microseconds() > self.t_baro.get_microseconds())
            if new_:
                self.t_baro = sensor.timestamp
            return new_

def main():
    # Create a Camera object
    zed = sl.Camera()

    init_params = sl.InitParameters()
    init_params.depth_mode = sl.DEPTH_MODE.NONE

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print(repr(err))
        zed.close()
        exit(1)

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
                print(magnetic_heading)
                magnetic_field_calibrated = sensors_data.get_magnetometer_data().get_magnetic_field_calibrated()
                print(
                    " - Magnetometer\n \t Magnetic Field: [ {0} {1} {2} ] [uT]".format(magnetic_field_calibrated[0],
                                                                                       magnetic_field_calibrated[1],
                                                                                       magnetic_field_calibrated[
                                                                                           2]))
    zed.close()
    return 0


if __name__ == "__main__":
    main()
