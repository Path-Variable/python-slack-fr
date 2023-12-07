import cv2

haar_cascade = "haarcascade_frontalface_default.xml"
detector = cv2.CascadeClassifier(haar_cascade)

image = cv2.imread("/home/isaric/Downloads/20231207114056.png", cv2.IMREAD_GRAYSCALE)

rectangles = detector.detectMultiScale(image, scaleFactor=1.05, 
                        minNeighbors=3, minSize=(1, 1),
                        flags=cv2.CASCADE_SCALE_IMAGE)

print(len(rectangles))
if (len(rectangles) == 0):
    exit(0)
for ((top, right, bottom, left)) in rectangles:
    cv2.rectangle(image, (left, top), (right, bottom),(0, 255, 225), 2)
    y = top - 15 if top - 15 > 15 else top + 15
cv2.imshow("Faces found", image)
k = cv2.waitKey(0)
cv2.destroyAllWindows()
