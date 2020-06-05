from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

def scrape_all():

    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
        }
    browser.quit()    
    return data
    
def mars_news(browser):
    # Convert the browser html to a soup object and then quit the browser
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)
    
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()    

        

        return news_title, news_p
    except AttributeError:
        return None, None

def featured_image(browser):
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')
    try:
        url = 'https://www.jpl.nasa.gov/spaceimages/?search=&catagory=Mars'
        browser.visit(url)
        # find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

        full_image_elem = browser.find_by_id('full_image')
        full_image_elem.click()

        browser.is_element_present_by_text('more info', wait_time=1)
        more_info_elem = browser.links.find_by_partial_text('more info')
        more_info_elem.click()
    
        img_url_rel = img_soup.select_one('figure.lede a img').get('src')

        img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

        return img_url
    except AttributeError: 
        return None

def mars_facts():

    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]
    
        # Assign columns and set index of dataframe
        df.columns=['Description', 'Mars']
        df.set_index('Description', inplace=True)
    
        # Convert dataframe into HTML format, add bootstrap
        return df.to_html()
    except BaseException:
        return None

    df.to_html()

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
