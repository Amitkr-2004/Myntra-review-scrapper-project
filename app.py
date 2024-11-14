import pandas as pd
import streamlit as st
from src.cloud_io import MongoIO
from src.constants import *
from src.scrapper.scrape import ScrapeReviews

st.set_page_config(
    "myntra-review-scrapper"
)

st.title('Myntra Review Scrapper')
st.session_state['data']=False  #This basically keeps the record of data during ongoing running applications

def form_input():

    product = st.text_input("Search Products")

    st.session_state[SESSION_PRODUCT_KEY]=product

    no_of_products=st.number_input("No. of products",step=1,min_value=1)

    if st.button('Scrape Reviews'):
        
        scrapper = ScrapeReviews(product_name=product,no_of_products=int(no_of_products))

        scrapper_data = scrapper.get_review_data()

        if scrapper_data is not None:
            st.session_state['data']=True  #store the data for ongoing application

            mongoio=MongoIO()      #instance of connection to mongoDB

            mongoio.store_reviews(product_name=product,reviews=scrapper_data)   #store every reviews in mongoDB

            print("stored data in MongoDB")

        st.dataframe(scrapper_data)     #finally display the comments in frontend
    
if __name__=='__main__':
    data= form_input()


