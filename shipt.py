#!/usr/bin/python3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from re import sub
from decimal import Decimal
import csv
import time
from bs4 import BeautifulSoup

TWOPLACES = Decimal(10) ** -1

chrome_options = Options()  
chrome_options.add_argument("--headless")  
driver = webdriver.Chrome(chrome_options=chrome_options)
#driver = webdriver.Chrome()

driver.get("https://shop.shipt.com/login") #Opens Login Page

#Explicitly wait for the login element to become present (max 30 seconds)
wait = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "login-email")))

#Fills out login form and submits it
driver.find_element_by_id("login-email").send_keys("my_email")
driver.find_element_by_id ("login-password").send_keys("my_password")
driver.find_element_by_css_selector("button[data-test='LoginForm-log-in-button']").click()

time.sleep(4) #Pauses 4 seconds to be sure its finished

#Dictionaries of categories / links to grab
meats =	{
  "beef": "https://shop.shipt.com/search?categories=Meat%20%26%20Seafood%20%3E%20Beef&on_sale=true",
  "pork": "https://shop.shipt.com/search?categories=Meat%20%26%20Seafood%20%3E%20Poultry%20%3E%20Chicken&on_sale=true",
  "chicken": "https://shop.shipt.com/search?categories=Meat%20%26%20Seafood%20%3E%20Poultry%20%3E%20Chicken&on_sale=true",
  "turkey": "https://shop.shipt.com/search?categories=Meat%20%26%20Seafood%20%3E%20Poultry%20%3E%20Turkey&on_sale=true",
  "fish": "https://shop.shipt.com/search?categories=Meat%20%26%20Seafood%20%3E%20Seafood%20%26%20Sushi%20%3E%20Fish&on_sale=true",
  "shellfish": "https://shop.shipt.com/search?categories=Meat%20%26%20Seafood%20%3E%20Seafood%20%26%20Sushi%20%3E%20Shellfish&on_sale=true",
  "shrimp": "https://shop.shipt.com/search?categories=Meat%20%26%20Seafood%20%3E%20Seafood%20%26%20Sushi%20%3E%20Shrimp&on_sale=true"
}

produce = {
  "frozen_fruit": "https://shop.shipt.com/search?categories=Frozen%20%3E%20Frozen%20Fruits&on_sale=true&query=fruit",
  "frozen_steamer": "https://shop.shipt.com/search?categories=Frozen%20%3E%20Frozen%20Vegetables&on_sale=true&query=steam",
  "fruits": "https://shop.shipt.com/search?categories=Produce%20%3E%20Fruits&on_sale=true",
  "salad": "https://shop.shipt.com/search?categories=Produce%20%3E%20Packaged%20Salad%20Mixes&on_sale=true",
  "veggies": "https://shop.shipt.com/search?categories=Produce%20%3E%20Vegetables&on_sale=true",
  "prepared_produce": "https://shop.shipt.com/search?categories=Produce%20%3E%20Prepared%20Produce&on_sale=true"
}

cans = {
  "canned_veggies": "https://shop.shipt.com/search?categories=Pantry%20%3E%20Canned%20Goods%20%3E%20Canned%20%26%20Jarred%20Vegetables&on_sale=true",
  "canned_fruit": "https://shop.shipt.com/search?categories=Pantry%20%3E%20Canned%20Goods%20%3E%20Canned%20Fruit%20%26%20Applesauce&on_sale=true"
}

#List of all categories
savings_categories = { "meats": meats, "produce": produce, "cans":cans}

for cat_name, big_cat in savings_categories.items():

  #Opens the 3 CSV files and preps them with header rows
  with open(cat_name+'.csv', 'w') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerow(['Category', 'Name','Sale Price','Full Price','Savings','Image'])

  #Handles each of the categories, one by one
  for cat, site in big_cat.items():
    print(cat)
    driver.get(site) #Loads category site
    time.sleep(4) #Pauses 4 seconds to be sure its finished loading

    done = 0
    while done < 1:
      #Sees if there is more to load
      if driver.find_elements_by_css_selector("button[data-test='show-more-button']"):

        show_more = driver.find_element_by_css_selector("button[data-test='show-more-button']")
      
        #Has to scroll since it's off page
        action=ActionChains(driver)
        action.move_to_element(show_more)        
        action.click().perform()

        time.sleep(4) 
      #stops when not found
      else:
        break
  
    page_source = driver.page_source #Gets page source

    #passes source to Beautiful Soup and parses
    content = BeautifulSoup(page_source, 'html.parser')

    #Gets all product information divs
    products = content.select("div[data-test='SearchProduct-product-content']")

    #Loops through and breaks down products
    for a in range(len(products)):

      product = products[a]
      name = product.select("div.body-3.mb1.black.break-word")[0].get_text()
      sale_price = product.find("span", class_="callout-2").get_text()
      full_price = product.select('span.caption-1.strike')[0].get_text()
      product_img = product.select('img.db.center')[0]['src'].replace('thumb_', '')
      portion = product.select('div.caption-1.h1.mb1.gray')[0].get_text().replace(';', ':')
      #Diff returns the % saved
      diff = Decimal((1 - (Decimal(sub(r'[^\d.]', '', sale_price)) / Decimal(sub(r'[^\d.]', '', full_price))))*100).quantize(TWOPLACES)

      #Writes current product to the correct CSV
      with open(cat_name+'.csv', 'a') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow([cat, name+' ('+portion+')',sale_price,full_price,str(diff)+'%',product_img])

print('Done')
time.sleep(2) #Pauses 2 seconds to be sure its finished
driver.quit() #Closes the window
