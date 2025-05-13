from PIL import Image, ImageOps

# 打开四张图片
image1 = Image.open('1.png')
image2 = Image.open('2.png')
image3 = Image.open('3.png')
image4 = Image.open('4.png')

# 创建一个新的正方形画布
size = (2295, 1458)
square_image1 = Image.new('RGBA', size, (0, 0, 0, 0))
square_image2 = Image.new('RGBA', size, (0, 0, 0, 0))
square_image3 = Image.new('RGBA', size, (0, 0, 0, 0))
square_image4 = Image.new('RGBA', size, (0, 0, 0, 0))

# 计算每张图片需要放置的位置
left1 = (size[0] - image1.width) // 2
top1 = (size[1] - image1.height) // 2
left2 = (size[0] - image2.width) // 2
top2 = (size[1] - image2.height) // 2
left3 = (size[0] - image3.width) // 2
top3 = (size[1] - image3.height) // 2
left4 = (size[0] - image4.width) // 2
top4 = (size[1] - image4.height) // 2

# 将图片放置在正方形画布中央
square_image1.paste(image1, (left1, top1))
square_image2.paste(image2, (left2, top2))
square_image3.paste(image3, (left3, top3))
square_image4.paste(image4, (left4, top4))

# 保存处理后的图片
square_image1.save('1_square.png')
square_image2.save('2_square.png')
square_image3.save('3_square.png')
square_image4.save('4_square.png')
