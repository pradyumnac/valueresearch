import os
import json
import time
# import pdb
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

UA_STRING = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36"

DEBUG = True
DEBUG_READ = False

def get_portfolio(email,passwd, drivertype, driver_path=''):
    if drivertype == "Chrome":
        if driver_path is '':
            raise Exception("Driverpath cannot be blank for Chrome")
        from selenium.webdriver.chrome.options import Options
        opts = Options()
        opts.add_argument("user-agent="+UA_STRING)
        driver = webdriver.Chrome(driver_path,chrome_options=opts)
    elif drivertype == "PhantomJS":
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (UA_STRING)
        driver = webdriver.PhantomJS(desired_capabilities=dcap)
    else:
        raise Exception("Invalid Driver Type:" + drivertype)
    driver.set_window_size(1366, 680)
    
    vr = {}
    vr['portfolio'] = []
    
    driver.get("https://www.valueresearchonline.com/")
    driver.driver.find_element_by_css_selector("a.btnsignin").click()
    
    
    if DEBUG:        
        open("valueresearch_portfolio.json","w").write(json.dumps(vr))
        
        
if __name__ == "__main__":
    orders = get_portfolio(os.environ['VR_username'],os.environ['VR_passwd'],"Chrome","D:\Projects\projects\valueresearch\downloads\chromedriver.exe")