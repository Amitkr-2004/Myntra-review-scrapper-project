#it helps to get analysis of different pages that will be used in project

import pandas as pd
from src.cloud_io import MongoIO
from src.constants import * 
from src.data_report.generate_data_report import DashboardGenerator
import streamlit as st

mongo_con=MongoIO()         #Instance of the class to get_reviews data that is stored in mongodb

def create_analysis(review_data:pd.DataFrame):      #formed a instance of the class Dashboard Generator inside it to generate analysis
    
    if review_data is not None:
        st.dataframe(review_data)
        
        if st.button("Generate Analysis"):

            dashboard=DashboardGenerator(review_data)

            #Display general information
            dashboard.display_general_info()
            
            #Display Product information
            dashboard.display_product_sections()
    
try:
    if st.session_state.data:   #if session state data is true means first we have scraped data and then we are going to generate analysis page

        data = mongo_con.get_reviews(product_name=st.session_state[SESSION_PRODUCT_KEY])    #session product key contains the product name or we can say our collection name
        
        create_analysis(data)       #called the function which contains the data means stored mongodb data that we get through the previous function 

    else:
        with st.sidebar:        #if not true then it means we have not scrapped data  by our product name
            st.markdown("""No Data Available for analysis. Please Go to search page for analysis.""")

except AttributeError:
    product_name = None
    st.markdown(""" # No Data Available for analysis.""")
