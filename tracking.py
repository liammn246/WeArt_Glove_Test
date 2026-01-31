from weartsdk import WeArtCommon
from weartsdk.WeArtClient import WeArtClient
from weartsdk.WeArtTrackingCalibration import WeArtTrackingCalibration
from weartsdk.WeArtTrackingRawData import WeArtTrackingRawData
from weartsdk.TDProStatusListener import TDProStatusListener
from weartsdk.MiddlewareStatusListener import MiddlewareStatusListener
import logging
import time


client = WeArtClient(WeArtCommon.DEFAULT_IP_ADDRESS, WeArtCommon.DEFAULT_TCP_PORT, log_level=logging.INFO)
client.Run()

mwListener = MiddlewareStatusListener()
client.AddMessageListener(mwListener)

tdpListener = TDProStatusListener()
client.AddMessageListener(tdpListener)

middlewareStatus = mwListener.LastStatus()
if len(middlewareStatus.connectedDevices) == 0:
    print("Waiting for device to be connected...")
    while len(middlewareStatus.connectedDevices) == 0:
        time.sleep(0.5)
        middlewareStatus = mwListener.LastStatus()
deviceStatus = tdpListener.LastStatus()
for i, device in enumerate(deviceStatus.devices):
    print(f"Device {i} connected with MAC address {device.macAddress}, hand side {device.handSide} has battery at {device.master.batteryLevel}%")

client.Start()

input("Put on device, enter when done")
calibration = WeArtTrackingCalibration()
client.AddMessageListener(calibration)
client.StartCalibration()
while(not calibration.getResult()):
    time.sleep(1)
print(f"Calibrated: {calibration.getResult()}")
client.StopCalibration()

# Instantiate tracking raw data to read tracking raw data from the thimble's sensors
thumbRawSensorData = WeArtTrackingRawData(WeArtCommon.HandSide.Left, WeArtCommon.ActuationPoint.Thumb)
client.AddMessageListener(thumbRawSensorData)
indexRawSensorData = WeArtTrackingRawData(WeArtCommon.HandSide.Left, WeArtCommon.ActuationPoint.Index)
client.AddMessageListener(indexRawSensorData)
middleRawSensorData = WeArtTrackingRawData(WeArtCommon.HandSide.Left, WeArtCommon.ActuationPoint.Middle)
client.AddMessageListener(middleRawSensorData)
annularRawSensorData = WeArtTrackingRawData(WeArtCommon.HandSide.Left, WeArtCommon.ActuationPoint.Annular)
client.AddMessageListener(annularRawSensorData)
pinkyRawSensorData = WeArtTrackingRawData(WeArtCommon.HandSide.Left, WeArtCommon.ActuationPoint.Pinky)
client.AddMessageListener(pinkyRawSensorData)

client.StartRawData()
ts = thumbRawSensorData.GetLastSample().timestamp
while ts == 0:
    time.sleep(1)
    ts = thumbRawSensorData.GetLastSample().timestamp
for _ in range (120):
    thumbSampleData = thumbRawSensorData.GetLastSample().data
    indexSampleData = indexRawSensorData.GetLastSample().data
    middleSampleData = middleRawSensorData.GetLastSample().data
    annularSampleData = annularRawSensorData.GetLastSample().data
    pinkySampleData = pinkyRawSensorData.GetLastSample().data

    def fmt_sensor(name, sample):
        acc = sample.accelerometer
        gyro = sample.gyroscope
        return (f"{name}:\n\tAcc:\n\t\tX: {acc.x}\n\t\tY: {acc.y}\n\t\tZ: {acc.z}\n\tGyro:\n\t\tX: {gyro.x}\n\t\tY: {gyro.y}\n\t\tZ: {gyro.z}")

    print("\n" + "\n\n".join([
        fmt_sensor('THUMB', thumbSampleData),
        fmt_sensor('INDEX', indexSampleData),
        fmt_sensor('MIDDLE', middleSampleData),
        fmt_sensor('ANNULAR', annularSampleData),
        fmt_sensor('PINKY', pinkySampleData)
    ]))
    time.sleep(0.5)

client.StopRawData()

client.Stop()
client.Close() #Close connection to middleware















