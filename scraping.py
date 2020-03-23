import sys
import pandas as pd
from splinter import Browser
from bs4 import BeautifulSoup
import datetime as dt

#if we dont want to see browser running we # lines 7-8 and 129-131
executable_path= {'executable_path': 'chromedriver.exe'} #{file path to chromedriver: chromedriver.exe}
browser = Browser('chrome', **executable_path, headless = False) #command to use 'chrome' with chromedriver from executable_path

def scrape_all():
       # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser) 
    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(browser),
      "last_modified": dt.datetime.now(),
      "hires_hemisphere": hires_hemisphere(browser)}
      
    browser.quit() #we need to enable that if we dont want to see browser running(# lines 129-131)
    return data
    
def mars_news(browser):
    
   # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
   # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=2)

   # Convert the browser html to a soup object and then quit the browser
    html = browser.html

    try:
        news_soup = BeautifulSoup(html, 'html.parser')
        slide_elem = news_soup.select_one('ul.item_list li.slide')
   # Use the parent element to find the first <a> tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
   # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

# "### Featured Images" 
def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

# Find and click the full image button, we already found in web page that id=full_image holds full size image
    full_image_elem = browser.find_by_id('full_image') 
    full_image_elem.click() 

# Find the more info button and click that, searching by text
    browser.is_element_present_by_text('more info', wait_time=2)
    more_info_elem = browser.find_link_by_partial_text('more info') #, changed per VS code suggestion
    #more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

# Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

# Find the most recent image url
    try:
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
        img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    except AttributeError:
        return None, None
    return img_url

def hires_hemisphere(browser):
    try:
        # Visit the USGS Astrogeology Science Center Site
        url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
        browser.visit(url)

        hemisphere_image_urls = []
        mock_hemispheres = [{
            "title": "kitty1",
            "img_url": "https://live.staticflickr.com/3397/3551189653_501acccd41_b.jpg"},
        {
            "title": "kitty2",
            "img_url": "https://live.staticflickr.com/3397/3551189653_501acccd41_b.jpg"
        },
        {
            "title": "kitty3",
            "img_url": "https://live.staticflickr.com/3397/3551189653_501acccd41_b.jpg"
        },
        {
            "title": "kitty4",
            "img_url": "https://live.staticflickr.com/3397/3551189653_501acccd41_b.jpg"}]

    
    # getting list of all images of hemisphere
        links = browser.find_by_css("a.product-item h3")
        for item in range(len(links)):
            hemisphere = {}
        
        # finding 'h3' which contains hemisphere images, and ging to the page
            browser.find_by_css("a.product-item h3")[item].click()
        
        # each hemisphere image link contains "Sample" tex & extracting link
            sample_element = browser.find_link_by_text("Sample").first
            hemisphere["img_url"] = sample_element["href"]
        
        # Extracint hemisphere title
            hemisphere["title"] = browser.find_by_css("h2.title").text
        
        # adding dict. hemisphere key and item to the list
            hemisphere_image_urls.append(hemisphere)
        
        # return to previous page 
            browser.back()
    
    except (AttributeError,BaseException,KeyError):
        print("error:", sys.exc_info()[0])
        return None

    if len(hemisphere_image_urls) == 0:
        hemisphere_image_urls = mock_hemispheres.copy()

    return hemisphere_image_urls


def mars_facts(browser):
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None
    # Assign columns and set index of dataframe
    df.columns=['Description', 'Value']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

mars_news(browser)
featured_image(browser)
mars_facts(browser)
hires_hemisphere(browser)
scrape_all()


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
#close the browser
browser.quit() 



