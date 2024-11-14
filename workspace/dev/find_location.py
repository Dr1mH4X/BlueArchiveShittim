import cv2

# 匹配图像中心点
img = cv2.imread('./workspace/dev/test.png')
template = cv2.imread('./workspace/dev/template.png')
h, w = template.shape[:2]
# print(h, w)
result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
top_left = max_loc
bottom_right = (top_left[0] + w, top_left[1] + h)
cx = top_left[0] + w // 2
cy = top_left[1] + h // 2
print(cx, cy)
cv2.rectangle(img, top_left, bottom_right, (0, 0, 255), 2)
cv2.circle(img, (cx, cy), 5, (0, 255, 0), -1)
cv2.imshow('result', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# h, w = img.shape[:2] # 屏幕中心点 640x360
# cx = w // 2
# cy = h // 2
# print(cx, cy)
# cv2.circle(img, (cx, cy), 5, (0, 255, 0), -1)
# cv2.imshow('result', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()