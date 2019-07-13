from selenium import webdriver

driver = webdriver.Chrome()
driver.get("http://mi.talkingdata.com/")
element = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[2]/div/input")
element.send_keys("qq")
driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div/button').click()
response= driver.page_source
driver.close()