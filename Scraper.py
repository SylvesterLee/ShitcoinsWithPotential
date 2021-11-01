from bs4 import BeautifulSoup
import urllib.request
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import date
import csv
from pandas import *


PATH = 'C:\Program Files (x86)\chromedriver.exe'
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--start-maximized")

class Scraper(object):

    def __init__(self, minHolders, maxHolders, minPercentInContractsOrDead, maxLargestHolder, maxTransfersPerMin, minTransfersPerMin, minBNBLPHoldings, hasEmptyImage, fileName):
        self.minHolders = minHolders
        self.maxHolders = maxHolders
        self.minPercentInContractsOrDead = minPercentInContractsOrDead
        self.maxLargestHolder = maxLargestHolder
        self.maxTransfersPerMin = maxTransfersPerMin
        self.minTransfersPerMin = minTransfersPerMin
        self.minBNBLPHoldings = minBNBLPHoldings
        self.hasEmptyImage = hasEmptyImage
        self.savedTokens = []
        self.fileName = fileName

    def run(self):
        try:
            potentialCoins = []
            driver = webdriver.Chrome(PATH, options = options)
            self.readSavedCoins()

            driver.get('https://bscscan.com/tokentxns')
            try:
                txTable = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME,'tbody'))
            )
            except:
                driver.quit()
            
            txTableRows = txTable.find_elements(By.TAG_NAME, 'tr')
            for i in range(14):
                tokenImg = txTableRows[i].find_element(By.TAG_NAME,'img').get_attribute('src')
                tokenImgBtn = txTableRows[i].find_element(By.TAG_NAME,'img')
                tokenID = txTableRows[i].find_elements(By.TAG_NAME, 'a')[-1].get_attribute('href')[26:]
                tokenName = txTableRows[i].find_elements(By.TAG_NAME, 'span')[-1].get_attribute('data-original-title')
                if tokenName == None:
                    tokenName = txTableRows[i].find_elements(By.TAG_NAME, 'a')[-1].text
        
                if tokenID in self.savedTokens:
                    continue
                
                if tokenImg == 'https://bscscan.com/images/main/empty-token.png':
                    tokenImgBtn.click()
                    try:
                        numHoldersString = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME,'mr-3'))
                    )
                    except:
                        driver.quit()
                    numHolders = int(numHoldersString.text[:-10].replace(',',""))




                    if self.minHolders < numHolders < self.maxHolders:
                        coinDict = {
                            "name": tokenName,
                            "tokenID": tokenID,
                            "holders": numHolders,
                            "date": date.today().strftime("%Y-%m-%d"),
                            "tokenSniffer" : f"https://tokensniffer.com/token/{tokenID}"
                        }
                        potentialCoins.append(coinDict)
                    driver.back()

                    try:
                        txTable = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME,'tbody'))
                    )
                    except:
                        driver.quit()
                    txTableRows = txTable.find_elements(By.TAG_NAME, 'tr')
                    self.savedTokens.append(tokenID)
            
            driver.quit()
            return potentialCoins
        except:
            return
        
    def writeToCsv(self, potentialCoins, newCSV = False):
        try:
            keys = potentialCoins[0].keys()
            if newCSV:
                with open(self.fileName, 'w', newline='')  as output_file:
                    dict_writer = csv.DictWriter(output_file, keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(potentialCoins)
            else:
                with open(self.fileName, 'a', newline='')  as output_file:
                    dict_writer = csv.DictWriter(output_file, keys)
                    dict_writer.writerows(potentialCoins)
        except:
            pass

    def readSavedCoins(self):
        file = read_csv(self.fileName)
        self.savedTokens = file['tokenID'].tolist()