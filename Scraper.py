from bs4 import BeautifulSoup
import requests
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
import os
import re


PATH = 'C:\Program Files (x86)\chromedriver.exe'
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--start-maximized")

class Scraper(object):

    def __init__(self, minHolders, maxHolders, minPercentInContractsOrDead, maxLargestHolder, maxTransfersPerMin, minTransfersPerMin, minBNBLPHoldings, hasEmptyImage, maxBuyTax, maxSellTax, fileName):
        self.minHolders = minHolders
        self.maxHolders = maxHolders
        self.minPercentInContractsOrDead = minPercentInContractsOrDead
        self.maxLargestHolder = maxLargestHolder
        self.maxTransfersPerMin = maxTransfersPerMin
        self.minTransfersPerMin = minTransfersPerMin
        self.minBNBLPHoldings = minBNBLPHoldings
        self.hasEmptyImage = hasEmptyImage
        self.savedTokens = []
        self.maxBuyTax = maxBuyTax
        self.maxSellTax = maxSellTax
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
                
                if tokenImg == 'https://bscscan.com/images/main/empty-token.png' or (not self.hasEmptyImage):
                    tokenImgBtn.click()
                    try:
                        numHoldersString = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME,'mr-3'))
                    )
                    except:
                        driver.quit()
                    numHolders = int(numHoldersString.text[:-10].replace(',',""))

                    if self.minHolders < numHolders < self.maxHolders and self.isHoneypotSecureAndWithinTaxRange(tokenID):
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
    
    def isHoneypotSecureAndWithinTaxRange(self, tokenID):
        try:
            driver = webdriver.Chrome(PATH, options = options)
            driver.get(f'https://honeypot.is/?address={tokenID}')
            try:
                _ = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID,'token-info')))
                conclusion = driver.find_elements(By.CLASS_NAME, 'header')[1].text

                if conclusion == 'Yup, honeypot. Run the fuck away.':
                    driver.quit()
                    return False
                elif conclusion == 'Does not seem like a honeypot.':
                    try:
                        buySellTax = driver.find_elements(By.TAG_NAME, 'p')[-1].text
                        buySellTaxNumbers = re.findall(r'\d+', buySellTax)
                        if self.maxBuyTax >= int(buySellTaxNumbers[0]) and self.maxSellTax >= int(buySellTaxNumbers[1]):
                            driver.quit()
                            return True
                        else:
                            driver.quit()
                            print(f"Did not pass test: {tokenID}")
                            return False
                    except:
                        print(f"some error occured when scraping buy and sell tax for ID: {tokenID}")
                        return False
                else: 
                    print(conclusion)
                    driver.quit()
                    return False
                

            
            except:
                driver.quit()
                return False
        except:
            print(f"some error occured when scraping honeypot for ID: {tokenID}")
            return False

        '''html_text = requests.get('https://honeypot.is/?address=0x5c7c45e7c8febb2a16092fe32bc465e88d4389eb').text
        soup = BeautifulSoup(html_text, 'lxml')
        print(soup.find('div', id_ = 'shitcoin'))'''


    def writeToCsv(self, potentialCoins):
        try:
            keys = potentialCoins[0].keys()
            if not os.path.isfile(self.fileName):
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
        if os.path.isfile(self.fileName):
            file = read_csv(self.fileName)
            self.savedTokens = file['tokenID'].tolist()