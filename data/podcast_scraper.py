from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import json
import re
import pandas as pd 

BASE_URL = "https://chartable.com/charts/itunes/us"



def main():
    webpage_data = fetch_webpage_data(BASE_URL)

    podcast_data = get_podcast_data(webpage_data)
    podcast_final = get_podcast_description(podcast_data)
            
    for category, podcasts in podcast_data.items():
        podcast_cat_list[category] = [{podcast: podcast_final.get(podcast, 'No description available')} for podcast in podcasts]

    write_to_json_file(podcast_cat_list,'podcast_2024.json')


def fetch_webpage_data(url):
    """
    Fetching chartable list on the top popular podcasts 
    """
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req)
    webpageData = webpage.read()
    webpage.close()
    return webpageData

def split_strings_by_delimiter(string_list):
    """
    Process delimiter from the podcast title 
    """
    if "'" in string_list:
        string_list = string_list.replace("'", "")
    pattern = re.compile(r'[-;,/\\?*\\\'"#&!:\s]')
    return pattern.split(string_list)

def get_podcast_data(webpage_data):
    """
    Fetch top podcasts based on category 
    """
    page_soup = BeautifulSoup(webpage_data, 'html.parser')
    podcasts = page_soup.find_all('div', attrs = {"class":"mb3"})
    podcast_lst = ['arts','business','comedy','education','fiction','government','health-fitness','history','kids-family',
                    'leisure','music','news','religion-spirituality','science','society-culture','sports'
                    ,'tv-film','technology','true-crime']
    podcast_cat_list = {}
    for i in podcasts[1].findAll('a'):
        job_element = i['href']
        category_name = job_element.strip().split('/')[-1].split('-')[1]
        if category_name == 'arts':
            podcast_lst_data = fetch_webpage_data(job_element)
            podcast_data_soup = BeautifulSoup(podcast_lst_data, 'html.parser')
            podcast_final = list(set([html_string.get_text() for html_string in tb.find_all('a',attrs= {"class":"link blue"}) for tb in podcast_data_soup.find_all('table')]))
            podcast_cat_list[category_name] = podcast_final
    return podcast_cat_list

def get_podcast_description(podcast_list):
    """
    Fetch top podcasts' description 
    """

    pod_description = {}
    for key,values in podcast_cat_list.items():
        for strings in values:
            actual_value = [ele for ele in split_strings_by_delimiter(strings) if ele]

            try: 
                if strings != "Let's Talk About Myths, Baby! Greek & Roman Mythology Retold":
                    title_element = fetch_webpage_data(f"https://chartable.com/podcasts/{'-'.join(actual_value).lower()}")

                elif strings == "Let's Talk About Myths, Baby! Greek & Roman Mythology Retold":
                    title_element = fetch_webpage_data("https://chartable.com/podcasts/lets-talk-about-myths-baby-a-greek-roman-mythology-podcast")


                podcast_title_soup = BeautifulSoup(title_element, 'html.parser')
                podcast_description = podcast_title_soup.find('div', attrs = {"class":"almost-silver"}).get_text()

            except: 
                print(f"An error occured while processing {actual_value}")
                continue 
            
            pod_description[strings] = podcast_description
    return pod_description


def write_to_json_file(data, write_path):
    with open(write_path,'w') as f:
        json.dump(data, f)

def write_to_yaml_file(data, write_path):
    with open(write_path,'w') as f:
        yaml.dump(data,f)

def load_podcast_json_to_dataframe(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)

    types = []
    podcasts = []
    descriptions = []

    for category, podcasts_info in data.items():
        for podcast_info in podcasts_info:
            for podcast, description in podcast_info.items():
                types.append(category)
                podcasts.append(podcast)
                descriptions.append(description)

    df = pd.DataFrame({'type': types, 'podcast': podcasts, 'description': descriptions})
    
    return df

if __name__ == '__main__':
	main()
