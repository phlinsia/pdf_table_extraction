import pdfplumber
import json
import time

keywords = ['申购', '赎回', '认购', '管理']
result = []
T1 = time.time()
path = r"../in.pdf"
# 打开PDF文件
with pdfplumber.open(path) as pdf:
    # 遍历每一页
    for page in pdf.pages:
        # 提取表格信息
        print(page.page_number)
        tables = page.extract_tables()
        for table in tables:
            # 判断是否提取到表格
            if table:
                # 处理表格数据
                # 在这里进行你需要的操作，比如打印表格数据、保存数据到文件等
                for row in table:
                    for keyword in keywords:
                        if row[0] is None:
                            continue
                        if keyword in row[0]:
                            row[0] = row[0].replace("\n", " ")
                            for k in row[1:]:
                                temp = {}
                                if k:
                                    k = k.replace("\n", " ")
                                temp[row[0]] = str(k)
                                if temp:
                                    result.append(temp)
                print(table)
T2 = time.time()
# 进行json输出前，对含有编码的数据进行编码转换
result_json = json.dumps(result, ensure_ascii=False, indent=2)
print((T2-T1)*1000)
with open('output.json', 'w', encoding='utf-8') as f:
    f.write(result_json)