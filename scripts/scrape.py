import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

def get_hyperlinks(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href.startswith('view_episode_scripts.php'):
            links.append('https://www.springfieldspringfield.co.uk/' + href)
    
    return links

def get_episode_name(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params['episode'][0]

def scrape_text_from_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    text_container = soup.find('div', class_='scrolling-script-container')
    if text_container:
        return text_container.get_text(strip=True)
    else:
        return None

def main():
    landing_page = 'https://www.springfieldspringfield.co.uk/episode_scripts.php?tv-show=breaking-bad'
    
    hyperlinks = get_hyperlinks(landing_page)
    print(f'Found {len(hyperlinks)} hyperlinks:')
    
    os.makedirs('episodes', exist_ok=True)
    
    for link in hyperlinks:
        episode_name = get_episode_name(link)
        filename = f'episodes/{episode_name}.txt'
        
        print(f'Scraping {link}...')
        text = scrape_text_from_page(link)
        
        if text:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(text)
            print(f'Successfully saved {filename}')
        else:
            print(f'Failed to scrape text from {link}')

if __name__ == '__main__':
    main()
