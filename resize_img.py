from PIL import Image
import os

directory = "./assets"
files = os.listdir(directory)
png_files = [file for file in files if file.endswith(".png")]

for png_file in png_files:
    file_path = os.path.join(directory, png_file)
    image = Image.open(file_path)
    resized_image = image.resize((30,30))
    resized_file_path = os.path.join("./assets/resized", png_file)
    resized_image.save(resized_file_path)
    resized_image.close()


# wep = Image.open("weapon.png")
# res_wep = wep.resize((30,30))
# res_wep.save("res_wep.png")
# res_wep.close()