from email import message
import os
import requests
from bs4 import BeautifulSoup
from IPython.display import display, Markdown
from openai import OpenAI

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

system_prompt = """
You are an amazing homecook that analyzed the recipes from a website, 
and provides a short summary of different recipes, ignore any navigation, text and unrelated link. 
Respond in markdown and in English"""

user_prompt = """
Here is the content of the website.
Please translate all extracted content into English and 
provide a summary of recipes from the website in markdown in English.
Ignore any advertisements and navigation text.


"""

# The helper function was built by Ed Donner in UdemyCourse
def fetch_web_contents(url):
    """
    Return the title and contents of the website at the given url;
    truncate to 2,000 characters as a sensible limit
    """
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string if soup.title else "No title found"
    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""
    return (title + "\n\n" + text)[:2_000]
    
def message_for_web(web_content):
    """
    Return the message format for the API from openAI
    It should be a list with dictionaries.
    """
    # API from OpenAI expect the structure above
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt + web_content}
    ]

def summary_web(web_site_url):
    """
    Fetch the content of web then the content summarized by ollama
    """
    web_content = fetch_web_contents(web_site_url)

    ollama = OpenAI(base_url="http://localhost:11434/v1", api_key = "ignore")

    responses = ollama.chat.completions.create(
        model="llama3.2", 
        messages=message_for_web(web_content)
    )

    return responses.choices[0].message.content

def main():
    """Main function for testing"""
    # Example url: https://www.food.com/ideas/quick-easy-pasta-recipes-6078

    flag = True
    while flag:
        url = input("Please enter a url or enter quit to cancle request: ")
        if url != "quit":
            print("Fetching and summarizing web content: ")
            print()
            print(summary_web(url))
        else:
            flag = False
        
if __name__ == "__main__":
    main()