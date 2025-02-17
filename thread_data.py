from threading import Event

exit_event = Event()
cameraView = None

recognizer_latency = -1
recognizer_gestures = ''