from flask import request
from src.cloud_io import MongoIO
from src.constants import *
from src.exception import CustomException
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import pandas as pd
import os,sys,time
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote

class ScrapeReviews:
    def __init__(self,product_name,no_of_products):
        option=Options()

        self.driver=webdriver.Chrome(options=option)
        self.product_name=product_name
        self.no_of_products=no_of_products
    
    def scrape_product_url(self,product_name):  #this helps in providing all the product links in a list format
        try:
            search_string = product_name.replace(' ','-')   #this contains only the product name like t-shirts

            #quote the search string(means make it to the url format)
            encoded_query=quote(search_string)  #after that remaining string

            #navigate to url
            self.driver.get(f"https://www.myntra.com/{search_string}?rawQuery={encoded_query}")


            myntra_text=self.driver.page_source

            myntra_html=bs(myntra_text,"html.parser")

            pclass=myntra_html.findAll('ul',{'class':'results-base'})

            product_url=[]

            for i in pclass:
                href=i.findAll('a',href=True)

                for productNo in range(len(href)):
                    t = href[productNo]['href']
                    product_url.append(t)
                
            return product_url

        except Exception as e:
            raise CustomException(e,sys) from e
        
    def extract_reviews(self,product_url): #This helps to get the review page url and all other properties of it
        try:
            product_link = "https://www.myntra.com/" + product_url  #entered in the product url

            self.driver.get(product_link)

            prodRes = self.driver.page_source

            prodRes_html=bs(prodRes,'html.parser')

            title_h = prodRes_html.findAll('title')

            self.product_title=title_h[0].text

            overAllRating = prodRes_html.findAll('div',{'class':'index-overallRating'})

            for i in overAllRating:
                self.product_rating=i.find('div').text
            
            price = prodRes_html.findAll("span", {"class": "pdp-price"})

            for i in price:
                self.product_price = i.text

            product_reviews = prodRes_html.find("a", {"class": "detailed-reviews-allReviews"})

            if product_reviews is None:
                return None
            return product_reviews

        except Exception as e:
            raise CustomException(e,sys) from e
        
    def scroll_to_load_reviews(self):   #This basically helps to load the comment for infinite comments
        # Change the window size to load more data
        self.driver.set_window_size(1920,1080)

        #Get the initial height of the window
        last_height=self.driver.execute_script('return document.body.scrollHeight')

        # Scroll in smaller increments, waiting between scrolls
        while True:
            # Scroll down by a small amount
            self.driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(3)

            # Calculate the new height after scrolling
            new_height=self.driver.execute_script('return document.body.scrollHeight')

            #Now check whether heights are matching or not
            if last_height==new_height:
                break

            last_height=new_height
 
    def extract_products(self,product_reviews:list):  #This basically returns all reviews in a form of dataframe
        try:
            t2 = product_reviews['href']

            Review_link = 'https://www.myntra.com' + t2

            self.driver.get(Review_link)

            self.scroll_to_load_reviews()

            review_page = self.driver.page_source

            review_page_html = bs(review_page,'html.parser')

            review = review_page_html.findAll('div',{'class':"detailed-reviews-userReviewsContainer"})

            for i in review:
                user_rating = i.findAll("div", {"class": "user-review-main user-review-showRating"})
                
                user_comment = i.findAll("div", {"class": "user-review-reviewTextWrapper"})
                
                user_name = i.findAll("div", {"class": "user-review-left"})

            reviews = []

            for i in range(len(user_rating)):
                try:
                    rating = (user_rating[i].find("span", class_="user-review-starRating").get_text().strip())
                except:
                    rating = "No rating Given"

                try:
                    comment = user_comment[i].text
                except:
                    comment = "No comment Given"

                try:
                    name = user_name[i].find("span").text
                except:
                    name = "No Name given"

                try:
                    date = user_name[i].find_all("span")[1].text
                except:
                    date = "No Date given"

                mydict = {
                    "Product Name": self.product_title,
                    "Over_All_Rating": self.product_rating,
                    "Price": self.product_price,
                    "Date": date,
                    "Rating": rating,
                    "Name": name,
                    "Comment": comment,
                }
                reviews.append(mydict)

            review_data = pd.DataFrame(
                reviews,
                columns=[
                    "Product Name",
                    "Over_All_Rating",
                    "Price",
                    "Date",
                    "Rating",
                    "Name",
                    "Comment",
                ],
            )

            return review_data

        except Exception as e:
            raise CustomException(e, sys)
        
    def skip_products(self, search_string, no_of_products, skip_index):
        product_urls: list = self.scrape_product_urls(search_string, no_of_products + 1)

        product_urls.pop(skip_index)

    def get_review_data(self)->pd.DataFrame:
        
        try:
            product_urls=self.scrape_product_url(product_name=self.product_name)    #found links in form of list

            product_details=[]
            review_len=0

            while review_len < self.no_of_products:
                product_url = product_urls[review_len]  #got particular link
                review_link=self.extract_reviews(product_url)       #got the review page link

                if review_link:
                    product_detail = self.extract_products(review_link)     #got all reviews
                    product_details.append(product_detail)      #appended dataframe in list

                    review_len+=1
                else:
                    product_urls.pop(review_len)        #if none then popped out

            self.driver.quit()

            data = pd.concat(product_details,axis=0)    #combined in rows

            data.to_csv('data.csv',index=False)

            return data

        except Exception as e:
            raise CustomException(e,sys) from e