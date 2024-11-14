import cv2

img = cv2.imread("./workspace/dev/test.png")
temp1 = cv2.imread("./workspace/dev/template.png")
height, width, c = temp1.shape
img_height, img_width, _ = img.shape
results = cv2.matchTemplate(img, temp1, cv2.TM_CCOEFF_NORMED)
for y in range(results.shape[0]):
    for x in range(results.shape[1]):
        if results[y][x] > 0.80:
            cv2.rectangle(img, (x, y), (x + width, y + height), (255, 0, 0), 2)
            text = f"({x}, {y})"
            text_x = x - 70
            text_y = y + 35
            cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
cv2.imshow("img", img)
cv2.waitKey()
cv2.destroyAllWindows()

"""
任务： [108, 253]
社交： [606, 671]
制造： [700, 674]
邮件： [1178, 14]
"""