from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
import pprint

pp = pprint.PrettyPrinter(indent=4)

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
        "hemispheres": mars_hemispheres(browser),
        "last_modified": dt.datetime.now()
        }
    
    # Quit the browser & retrieve the data gathered:
    browser.quit()    
    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)
    
    # Convert the browser html to a soup object
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except to handle any errors encountered
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
    # Visit the NASA Mars site:
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&catagory=Mars'
    browser.visit(url)
    
    # Click on the button to get the full size image:
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()
    browser.is_element_present_by_text('more info', wait_time=1)
    
    # Click on the 'More Info' button:  
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the results:
    html = browser.html
    img_soup = soup(html, 'html.parser')
    
    # find the relative image url
    img_url_rel = img_soup.select_one('figure.lede a img').get('src')

    try:
        # Return the full-size image:    
        img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
        
    except AttributeError:     
        return None
    return img_url

def mars_facts():

    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)
    
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")
    

def mars_hemispheres(browser):
    # Visit the Astrogeology USGS site:
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Create empty list to hold hemisphere url's & titles:
    hemisphere_list = []

    # Find the pictures to click on to get the full size images:
    browser.is_element_present_by_css("thumb", wait_time=2)
    thumbnails = browser.find_by_tag('h3')

    # Create a loop to capture all 4 heisphere images & titles:
    for i in range(0,4):
        
        # Click on the thumbnail for each hemisphere image:
        thumbnails[i].click()

        # Parse the results:
        html = browser.html
        hemisphere_soup = soup(html, 'html.parser')

        # Find the relative image url
        img_url_rel = hemisphere_soup.select_one('.wide-image').get('src')
        hemisphere_title = hemisphere_soup.find('h2', class_='title').get_text()
        img_url = f'https://astrogeology.usgs.gov{img_url_rel}'

        # Add the information to the hemishphere_list dictionary
        hemisphere_dictionary = {}
        hemisphere_dictionary['img_url'] = img_url
        hemisphere_dictionary['title'] = hemisphere_title 
        hemisphere_list.append(hemisphere_dictionary)

        # Hit the back button on the browser to go back to the thumbnails:
        browser.back()

        # Find the next thumbnail & go through the process until all 4 are returned:
        browser.is_element_present_by_css("thumb", wait_time=2)
        thumbnails = browser.find_by_tag('h3')

    # Return the completed list with all 4 hemispheres & titles:
    return hemisphere_list

if __name__ == "__main__":

    # If running as script, print scraped data using prettyprint:
    print(scrape_all())