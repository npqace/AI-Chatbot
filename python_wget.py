import os
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def download_recursive(url, output_dir):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    print(soup.text)
    input()
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Download all HTML files
    for link in soup.find_all("a"):
        # print(link)
        href = link.get("href")
        # if href and href.endswith(".html"):
        if href:
            file_url = urljoin(url, href)
            print("URL: ", file_url)
            file_name = os.path.join(output_dir, os.path.basename(href))
            download_file(file_url, file_name)

def download_file(url, file_path):
    page = requests.get(url)
    soup_page = BeautifulSoup(page.content, "html.parser")
    print(soup_page.text)
    input()
    try: 
        with open(file_path, "wb") as file:
            file.write(page.content)
        print("SAVED TO: ", file_path)
    except:
        print("ERROR PATH: ", file_path)
# Usage example
url = "https://paraceltech.com/"
output_dir = "rtdocs"

download_recursive(url, output_dir)