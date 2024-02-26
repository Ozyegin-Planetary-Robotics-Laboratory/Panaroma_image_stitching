import cv2


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


def main():
    image = cv2.imread('C:/Users/taalp/Documents/GitHub/Panaroma_image_stitching/unstitchedImages/1.jpeg')
    placeSymbol(image, "N")
    # Display the image
    cv2.imshow('Image with symbol', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
