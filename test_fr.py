import cv2

haar_cascade = "haarcascade_frontalface_default.xml"
detector = cv2.CascadeClassifier(haar_cascade)

image = cv2.imread("test.jpeg", cv2.IMREAD_GRAYSCALE)

rectangles = detector.detectMultiScale(image, scaleFactor=1.1, 
                        minNeighbors=5, minSize=(30, 30),
                        flags=cv2.CASCADE_SCALE_IMAGE)

print(len(rectangles))