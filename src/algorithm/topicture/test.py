import pdfplumber
from PIL import Image

def extract_table_as_image(pdf_path):
    # 使用pdfplumber打开PDF
    with pdfplumber.open(pdf_path) as pdf:
        for page_number in range(len(pdf.pages)):
            page = pdf.pages[page_number]

            # 检测页面是否包含表格
            tables = page.find_tables()
            if tables:
                for table_num, table in enumerate(tables):
                    # 获取表格的边界坐标
                    table_bbox = table.bbox
                    # 将表格区域转换为图片
                    base = 10 # 15大概是我这个2核4G的服务器的上限
                    img = page.to_image(72 * base) # 我测试得到默认像素是72左右
                    pil_img = img.original  # 获取PIL.Image对象
                    cropped_img = pil_img.crop(((table_bbox[0] - 1.5) * base, (table_bbox[1] - 1.5) * base,
                     (table_bbox[2] + 1.5) * base, (table_bbox[3] + 1.5) * base))
                    cropped_img.save(f"./pictures/table_page_{page_number + 1}_table_{table_num + 1}.png", format="PNG")

# 调用函数提取表格部分为图片
pdf_path = "../6.pdf"
extract_table_as_image(pdf_path)
