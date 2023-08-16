import CurseWordDetector, time

start = time.time()
detector = CurseWordDetector.detector()
sound = CurseWordDetector.SoundBase()
print(detector.detect("잠만선풍기시발닥쳐"))