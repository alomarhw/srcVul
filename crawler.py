import requests
from bs4 import BeautifulSoup
import os

# Function to download a file from a given URL
def download_file(url, destination_folder):
    response = requests.get(url)
    if response.status_code == 200:
        file_name = os.path.join(destination_folder, url.split("/")[-1])
        with open(file_name, 'wb') as f:
            f.write(response.content)
        return file_name
    else:
        return None

# URL of the web page to scrape
web_page_url = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=2a3f7221acddfe1caa9ff09b3a8158c39b2fdeac"

# Send an HTTP GET request and parse the content with BeautifulSoup
response = requests.get(web_page_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Directory to save downloaded files
download_folder = "downloaded_files"
os.makedirs(download_folder, exist_ok=True)

# Loop through all links on the page
for link in soup.find_all('a'):
    href = link.get('href')
    if href and href.startswith("https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"):
        file_name = download_file(href, download_folder)
        if file_name:
            print(f"Downloaded: {file_name}")

if __name__ == "__main__":
    main()
