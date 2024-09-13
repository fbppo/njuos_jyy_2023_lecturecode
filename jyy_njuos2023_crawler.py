from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os

# 设置 Chrome 选项
def driver_init():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.binary_location = '/home/anon/Download/edge/chrome-linux64/chrome'
    # 设置 ChromeDriver 路径
    service = Service('/home/anon/Download/edge/chromedriver-linux64/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver
    
def get_html(url, driver):
    driver.get(url)
    html_doc = driver.page_source
    return html_doc

    
def save_to_file(text, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

def fetch_code(link, driver):
    html_doc = get_html(link, driver)
    soup = BeautifulSoup(html_doc, 'lxml')

    # fetch all the file name
    file_dict = {}
    dir = []
    ul_span = soup.select('div > ul[role="tablist"]') 
    for ul in ul_span:
        li_elements = ul.find_all('li')
        if li_elements:
            dir_name = li_elements[0].get_text().strip()
            # solve the problem that 2 examples have same name
            if dir_name in file_dict:
                print(f"Warning: {dir_name} already exists in file_dict")
                dir_name += "-philosopher"
            dir.append(dir_name)
            file_dict[dir_name] = []
            for li in li_elements[1:]:
                file_dict[dir_name].append(li.get_text().strip())
    # delete all the empty key
    file_dict = {k: v for k, v in file_dict.items() if v}
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # dir for saving all the code files of this lecture
    output_dir_name = link.split('/')[-1].split('.')[0]
    output_dir = os.path.join(current_dir, output_dir_name)
    os.makedirs(output_dir, exist_ok=True)
   
    # create seperate dir and file for each small project
    for dir_name in dir:
        dir_path = os.path.join(output_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        for file_name in file_dict[dir_name]:
            file_path = os.path.join(dir_path, file_name)
            save_to_file("", file_path) 

    # fetch all code spans
    code_spans = soup.select('div.widget-html-content > div.highlight > pre')
    
    # insert code into each file 
    while dir:
        dir_name = dir.pop(0)
        if dir_name not in file_dict:
            print(f"Warning: {dir_name} not found in file_dict")
            continue

        while file_dict[dir_name]:
            file_name = file_dict[dir_name].pop(0)
            file_path = os.path.join(output_dir, dir_name, file_name)
            # remove all the line numbers
            span = code_spans.pop(0)
            for lineno_span in span.select('span.linenos'):
                lineno_span.decompose()
            text = span.get_text().strip()
            save_to_file(text, file_path)
        if not file_dict[dir_name]:
            file_dict.pop(dir_name)

def main(): 

    driver = driver_init()

    home_page = get_html("https://jyywiki.cn/OS/2023/index.html",driver)
    home_soup = BeautifulSoup(home_page, 'lxml')
    lecuture_links = home_soup.select('div > ol > li > a')
    build_links = []
    for link in lecuture_links:
        href = link.get('href')
        if 'lab' not in href:
            build_links.append("https://jyywiki.cn/OS/2023/" + href)

    for link in build_links:
        fetch_code(link, driver)

    driver.quit()
    # 关闭 WebDriver

    
if __name__ == "__main__":
    main()