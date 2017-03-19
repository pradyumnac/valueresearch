import os
import re
import json
import time
import pdb
from pyquery import PyQuery as pq
import lxml.html
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

UA_STRING = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36"

DEBUG = True
DEBUG_READ = True

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

def cleanup_data(vr=None):
    if DEBUG_READ and not vr:
        vr = json.loads(open("valueresearch_portfolio.json","r").read())
    
    # vr["stocks_raw"] = lstStock
    # vr["mfs_raw"] = lstMF
    # vr["stock_subtotal_raw"] = lststockSubTotal
    # vr["MF_subtotal_raw"] = lstmfSubTotal
    # vr["summary_raw"] = lstsummary 
    
    lstCategory = []
    
    # summaryvalue
    d = {
        "totalvalue":vr["summary_raw"][0],
        "onedaychngamt":vr["summary_raw"][1].split(r"|")[0].strip(),
        "onedaychngpert":vr["summary_raw"][1].split(r"|")[1].strip(),
        "totalgrowthamt":vr["summary_raw"][2].split(r"|")[0].strip(),
        "totalgrowthpert":vr["summary_raw"][2].split(r"|")[1].strip(),
        }
    vr['summaryvalue'] = d
    lstCategory = []
    
    # stocksubtotal
    d = {
        "investedamt":vr["stock_subtotal_raw"][7],
        "latestamt":vr["stock_subtotal_raw"][10],
        "onedaychngamt":"",
        "onedaychngpert":"",
        "returnamt":"",
        "returnpert":"",
    }
    vr['stocksubtotal'] = d
    
    # mfsubtotal
    d = {
        "investedamt":vr["MF_subtotal_raw"][7],
        "latestamt":vr["MF_subtotal_raw"][10],
        "onedaychngamt":"",
        "onedaychngpert":"",
        "returnamt":"",
        "returnpert":"",
    }
    vr['mfssubtotal'] = d
    
    
    # stock
    lstCategory = []
    for i in vr["stocks_raw"]:
        lstCategory.append({
            "title":i[0].split("\u00a0")[0],
            "portpert":i[2],
            "latestnav":i[3].split(" ")[0],
            "navdate":i[3].split(" ")[1],
            "onedaychngamt":i[5],
            "onedaychngpert":i[6],
            "investamt":i[8],
            "costnav":i[9],
            "latestvalue":i[11],
            "units":i[12],
            "returnabs":i[14],
            "returnpertpa":i[15]
        })
    vr['stock'] = lstCategory
    lstCategory = []
    
    # mfs
    lstCategory = []
    for i in vr["mfs_raw"]:
        lstCategory.append({
            "title":i[0].split("\u00a0")[0],
            "portpert":i[2],
            "latestnav":i[3].split(" ")[0],
            "navdate":i[3].split(" ")[1],
            "onedaychngamt":i[5],
            "onedaychngpert":i[6],
            "investamt":i[8],
            "costnav":i[9],
            "latestvalue":i[11],
            "units":i[12],
            "returnabs":i[14],
            "returnpertpa":i[15]
        })
    vr['mfs'] = lstCategory
    lstCategory = []
    
    del vr["stocks_raw"]
    del vr["mfs_raw"]
    del vr["stock_subtotal_raw"]
    del vr["MF_subtotal_raw"]
    del vr["summary_raw"] 
    
    
    return vr
 
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
    # vr['portfolio'] = []
    # vr['portfolio_raw'] = []
    
    driver.get("https://www.valueresearchonline.com/")
    
    linkSkipAdlanding = WaitFor(driver, By.LINK_TEXT, "Go directly to Value Research Online")
    if linkSkipAdlanding:
        linkSkipAdlanding.click()
    else:
        vr['warn'].append("'Skip' link not found")
    
    
    btnNoThanks = WaitFor(driver, By.CSS_SELECTOR, "#noThanks")
    if btnNoThanks:
        btnNoThanks.click()
    else:
        vr['error'].append("'No Thanks' button not found")
    
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
        re_pattern_summary = re.compile("(?:PORTFOLIO VALUE IN R)|(?:VALUE CHANGE TODAY IN R)|(?:TOTAL GAIN IN R \| % PA)|(?:[ ]+)")
        re_pattern_stocks  = re.compile("(?:[ ]+)")
        re_pattern_mfs     = re.compile("(?:[ ]+)")
        WaitFor(driver, By.CSS_SELECTOR, "table#snapshot_tbl tbody.trData")
        tblStock, tblMF = driver.find_elements_by_css_selector("table#snapshot_tbl tbody.trData")
        tblStockSubTotal, tblMFSubTotal = driver.find_elements_by_css_selector("table#snapshot_tbl tbody.subtotal")
        tblSummary = driver.find_elements_by_css_selector("table.Portfolio-summary tr")[1]
        # print(tblMFSubTotal.get_attribute('innerHTML'))
        # print(tblSummary.get_attribute('innerHTML'))
        rowsStock = [i for i in pq(tblStock.get_attribute('innerHTML'))('tr:not(.soldHoldings)')]
        rowsMF = [i for i in pq(tblMF.get_attribute('innerHTML'))('tr:not(.soldHoldings)')]
        lstStock = []
        lstMF = []
        for row in rowsStock:
            lstStock.append([re.sub(re_pattern_stocks," ",str(i.text_content())).strip() for i in pq(lxml.html.tostring(row))('td') ])
        for row in rowsMF:
            lstMF.append([re.sub(re_pattern_mfs," ",str(i.text_content())).strip() for i in pq(lxml.html.tostring(row))('td') ])
        lststockSubTotal = [i.text_content() for i in pq(tblStockSubTotal.get_attribute('innerHTML'))('tr.NotImportHoldings td') ]
        lstmfSubTotal    = [i.text_content() for i in pq(tblMFSubTotal.get_attribute('innerHTML'))('tr td') ]
        lstsummary       = [re.sub(re_pattern_summary," ",str(i.text_content())).strip() for i in pq(tblSummary.get_attribute('innerHTML'))('td') ]
        
        vr["stocks_raw"] = lstStock
        vr["mfs_raw"] = lstMF
        vr["stock_subtotal_raw"] = lststockSubTotal
        vr["MF_subtotal_raw"] = lstmfSubTotal
        vr["summary_raw"] = lstsummary  
    else:
        raise Exception("Portfolio table not found!")
        
    if DEBUG:        
        open("valueresearch_portfolio.json","w").write(json.dumps(vr))
        
    vr = cleanup_data(vr)
    if DEBUG:        
        open("valueresearch_portfolio_clean.json","w").write(json.dumps(vr))
    return(vr)
    
if __name__ == "__main__":
    import os 
    dir_path = os.path.dirname(os.path.realpath(__file__))
    orders = get_portfolio(os.environ['VR_username'],os.environ['VR_passwd'],"Chrome",dir_path+os.path.sep+r"chromedriver\chromedriver.exe")
    # vr = cleanup_data()
    # open("valueresearch_portfolio_clean.json","w").write(json.dumps(vr))