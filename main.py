from PIL import Image
import cv2
import matplotlib.pyplot as plt
import pathlib
import urllib.request


def fix(image, x, y):
    dimensions = image.shape
    if dimensions[0] < y or dimensions[1] < x :
	    return error_handle("Input Image should be of minimum dimensions {}*{}!".format(x, y))
    image = automatic_brightness_and_contrast(image)
    return cv2.resize(image, (x, y), interpolation = cv2.INTER_AREA)


def automatic_brightness_and_contrast(image, clip_hist_percent=1):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray],[0],None,[256],[0,256])
    hist_size = len(hist)
    accumulator = []
    accumulator.append(float(hist[0]))
    for index in range(1, hist_size):
	    accumulator.append(accumulator[index -1] + float(hist[index]))
    maximum = accumulator[-1]
    clip_hist_percent *= (maximum/100.0)
    clip_hist_percent /= 2.0
    minimum_gray = 0
    while accumulator[minimum_gray] < clip_hist_percent:
	    minimum_gray += 1
    maximum_gray = hist_size -1
    while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
     	maximum_gray -= 1
    alpha = 255 / (maximum_gray - minimum_gray)
    beta = -minimum_gray * alpha
    auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return auto_result


def main(xa = 660, ya = 420):
	url1 = 'https://atfin-files.s3.ap-south-1.amazonaws.com/Prabir_Saha_65/4oxe83oo7nIMG_20210426_232939%281%29.jpg'
	file_extension = pathlib.Path(url1).suffix
	f1 = "AadhaarF{}".format(file_extension)
	urllib.request.urlretrieve(url1, f1)
	aad_f = cv2.imread(f1)
	aad_f = fix(aad_f, xa, ya)
	temp = cv2.cvtColor(aad_f, cv2.COLOR_BGR2RGB)
	aad_f_pil = Image.fromarray(temp)

	url2 = 'https://atfin-files.s3.ap-south-1.amazonaws.com/Prabir_Saha_65/ydPDhaCEcmIMG_20210426_233016%281%29.jpg'
	file_extension = pathlib.Path(url2).suffix
	f2 = "AadhaarB{}".format(file_extension)
	urllib.request.urlretrieve(url2, f2)
	aad_b = cv2.imread(f2)
	aad_b = fix(aad_b, xa, ya)
	temp = cv2.cvtColor(aad_b, cv2.COLOR_BGR2RGB)
	aad_b_pil = Image.fromarray(temp)

	w = xa
	h = 2*ya
	out = Image.new("RGBA", (w, h), (255, 255, 255, 255))
	out.paste(aad_f_pil, box=(0,0,w,ya))
	out.paste(aad_b_pil, box=(0,ya,w,2*ya))

	plt.imshow(out)
	plt.waitforbuttonpress(0)


if __name__ == '__main__':
	main()