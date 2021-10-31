from bs4 import BeautifulSoup
import urllib.request
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PATH = 'C:\Program Files (x86)\chromedriver.exe'
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

class Scraper(object):

    def __init__(self, minHolders, maxHolders, minPercentInContractsOrDead, maxLargestHolder, maxTransfersPerMin, minTransfersPerMin, minBNBLPHoldings, hasEmptyImage):
        self.minHolders = minHolders
        self.maxHolders = maxHolders
        self.minPercentInContractsOrDead = minPercentInContractsOrDead
        self.maxLargestHolder = maxLargestHolder
        self.maxTransfersPerMin = maxTransfersPerMin
        self.minTransfersPerMin = minTransfersPerMin
        self.minBNBLPHoldings = minBNBLPHoldings
        self.hasEmptyImage = hasEmptyImage


    def run(self):
        #=========https://bscscan.com/tokentxns=========
        #needed to properly load the html
        tokentxns_request = urllib.request.Request('https://bscscan.com/tokentxns', headers={'User-Agent': 'Mozilla/5.0'})
        tokentxns_html_text = urllib.request.urlopen(tokentxns_request).read()
        tokentxns_soup = BeautifulSoup(tokentxns_html_text, 'lxml')
        
        #the vertical table with all of the transactions
        transactionsTable = tokentxns_soup.find('tbody')

        #list of the horizontal tables for a transaction
        transactionTables = transactionsTable.find_all('tr') 

        #the image for that transaction
        tokenImage = transactionTables[0].find('img')['src'] #empty image: "/images/main/empty-token.png"
        
        #the contract address. Finds the last href in transactiontable and only saves the contract address
        tokenContract = transactionTables[0].find_all('a', href = True)[-1]['href'][7:]

        self.scrapeTokenTransfersPage(tokenContract)



    def scrapeTokenTransfersPage(self, tokenContract):
        #needed to properly load the html
        tokenTransfers_request = urllib.request.Request(f'https://bscscan.com/token/{tokenContract}', headers={'User-Agent': 'Mozilla/5.0'})
        print(f'https://bscscan.com/token/{tokenContract}')
        tokenTransfers_html_text = urllib.request.urlopen(tokenTransfers_request).read()
        tokenTransfers_soup = BeautifulSoup(tokenTransfers_html_text, 'lxml')

        #the vertical table with all of the trasnfers
        tables = tokenTransfers_soup.find_all('div', class_ = 'card-body')

        overviewTable = tables[0]
        numHolders = int(overviewTable.find('div', class_= 'mr-3').text[:-11].replace(',',""))

        transfersTable = tokenTransfers_soup.find('table', class_= 'table table-md-text-normal table-hover mb-4')

        print(transfersTable)
        #list of the horizontal tables for a transfers
        #transferTables = transfersTable.find_all('tr')
        #print(transferTables)


        #transferAge = transferTables[0].find('td', class_ = 'showAge')
        #print(transferAge)

    def seleniumTesting(self):
        driver = webdriver.Chrome(PATH, options = options)
        
        driver.get('https://bscscan.com/tokentxns')
        try:
            table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME,'tbody'))
        )
        except:
            driver.quit()
        tableRows = table.find_elements(By.TAG_NAME, 'tr')
        #for tableRow in tableRows:
        tableRow = tableRows[0]
        tokenImg = tableRow.find_element(By.TAG_NAME,'img').get_attribute('src')  #empty image
        tokenImgButton = tableRow.find_element(By.TAG_NAME,'img')
        tokenImgButton.click()


        try:
            numHoldersString = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME,'mr-3'))
        )
        except:
            driver.quit()
        numHolders = int(numHoldersString.text[:-10].replace(',',""))

        print(numHolders)
        time.sleep(4)
        driver.quit()
        
