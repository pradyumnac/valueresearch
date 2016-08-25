import os
import re
import json
import time
import pdb
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

UA_STRING = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36"

DEBUG = True
DEBUG_READ = False

def log(s,log_type="INFO"):
    if DEBUG:
        print(log_type+":"+s)
        
def WaitFor(driver, strByType, strIdentifier, timeout =10):
    try:        
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((strByType, strIdentifier))
        )
    except:
        el = None
    if el:
        log("Found item:"+strByType+":"+strIdentifier)
    else:
        log("Not Found item:"+strByType+":"+strIdentifier,"WARN")
        
    return(el)
    
def get_portfolio(email,passwd, drivertype, driver_path=''):
    if drivertype == "Chrome":
        if driver_path is '':
            raise Exception("Driverpath cannot be blank for Chrome")
        from selenium.webdriver.chrome.options import Options
        opts = Options()
        opts.add_argument("user-agent="+UA_STRING)
        # disable images
        prefs = {"profile.managed_default_content_settings.images":2}
        opts.add_experimental_option("prefs",prefs)

        driver = webdriver.Chrome(driver_path,chrome_options=opts)
    elif drivertype == "PhantomJS":
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (UA_STRING)
        driver = webdriver.PhantomJS(desired_capabilities=dcap)
    else:
        raise Exception("Invalid Driver Type:" + drivertype)
    driver.set_window_size(1366, 680)
    
    vr = {}
    vr['error'] = []
    vr['portfolio'] = []
    vr['portfolio_raw'] = []
    
    driver.get("https://www.valueresearchonline.com/")
    
    btnNoThanks = WaitFor(driver, By.CSS_SELECTOR, "#noThanks")
    if btnNoThanks:
        btnNoThanks.click()
    else:
        vr['error'].append("No Thanks button not found")
    
    linkSignin = WaitFor(driver, By.CSS_SELECTOR, "a.btnsignin")
    if linkSignin:
        linkSignin.click()
    else:
        vr['error'].append("Login link not found")
    
    inputboxUsername = WaitFor(driver, By.CSS_SELECTOR, "input#username")
    if inputboxUsername:
        inputboxUsername.send_keys(email)
    else:
        vr['error'].append("Username Field not found/Not in Signin Page")
    
    inputboxPasswd = WaitFor(driver, By.CSS_SELECTOR, "input#password")
    if inputboxPasswd:
        inputboxPasswd.send_keys(passwd)
    
        
    btnSubmit = WaitFor(driver, By.CSS_SELECTOR, "input#submitbtn")
    if btnSubmit:
        btnSubmit.click()
        if DEBUG:
            log("Logging in..")
        
        lblLoginConf = WaitFor(driver, By.CSS_SELECTOR, "span#headerLoginText")
        if lblLoginConf:
            log("You are now logged in")
        else:
            vr['error'].append("Login Failed")
    else:
        vr['error'].append("Submit Button not found")
    
    linkPortfolio = WaitFor(driver, By.CSS_SELECTOR, "a[href='/port/']")
    if linkPortfolio:
        linkPortfolio.click()
        
        lblPortfolioPage = WaitFor(driver, By.CSS_SELECTOR, "div.Portfolio-summary-head")
        if not lblPortfolioPage:
            return(vr)
    
    tblSnapsht = WaitFor(driver, By.CSS_SELECTOR, "table#snapshot_tbl")
    if tblSnapsht:
        rows = [i for i in pq(tblSnapsht.get_attribute('innerHTML'))('tr')]
        # pdb.set_trace()
        for n in range(2,len(rows)-2): # Last Row contains total
            print(rows[n].text_content())
            vr['portfolio_raw'].append([j.text_content().strip() for j in rows[n]])
            
        port = vr['portfolio_raw']
        ctr = 1
        for tt in port:
            li = {}
            li['id'] = ctr
            li['status']=''
            try:
                name_split_pattern = "(\s*\u00a0\s*)+\|(\s*\u00a0\s*)+"
                tstr = re.split(name_split_pattern,tt[0].strip())
                li['name'],li['pf_pert_allocation'] = tstr[0],tstr[-1]
                li['vro_ratings'] = tt[1].strip()
                li['??_1'] = tt[2].strip()
                try:
                    li['last_unit_price'], li['last_updated'] = tt[3].split(' ')
                except:
                    li['last_unit_price'], li['last_updated']= '',''
                    li['status'] = 'ERROR'
                li['day_chng_abs'] = tt[5].strip()
                li['day_chng_pert'] = tt[6].strip()
                li['cost_value'] = tt[8].strip()
                li['cost_unit_value'] = tt[9].strip()
                li['mkt_valu'] = tt[11].strip()
                li['units_owned'] = tt[12].strip()
                li['return_abs'] = tt[14].strip()
                li['return_pert'] = tt[15].strip()
                li['cost_unit_value'] = tt[9].strip()
                if li['status']!='ERROR':
                    li['status'] = 'OK'
            except: # some portfolio itms dont list all these numbers
                li['status'] = 'ERROR'
            
            vr['portfolio'].append(li)
            ctr += 1
            
            if not DEBUG :
                del vr['portfolio_raw']
    if DEBUG:        
        open("valueresearch_portfolio.json","w").write(json.dumps(vr))
        
    return(vr)
    
if __name__ == "__main__":
    orders = get_portfolio(os.environ['VR_username'],os.environ['VR_passwd'],"Chrome",r"D:\Projects\projects\valueresearch\downloads\chromedriver.exe")