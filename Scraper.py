from bs4 import BeautifulSoup
import urllib.request
#from selenium import webdriver
import time
class Scraper(object):

    def __init__(self, minHolders, maxHolders, minPercentInContractsOrDead, maxLargestHolder, maxTransfersPerMin, minTransfersPerMin, minBNBLPHoldings):
        self.minHolders = minHolders
        self.maxHolders = maxHolders
        self.minPercentInContractsOrDead = minPercentInContractsOrDead
        self.maxLargestHolder = maxLargestHolder
        self.maxTransfersPerMin = maxTransfersPerMin
        self.minTransfersPerMin = minTransfersPerMin
        self.minBNBLPHoldings = minBNBLPHoldings


    def run(self):
        #=========https://bscscan.com/tokentxns=========
        #needed to properly load the html
        tokentxns_request = urllib.request.Request('https://bscscan.com/tokentxns', headers={'User-Agent': 'Mozilla/5.0'})
        tokentxns_html_text = urllib.request.urlopen(tokentxns_request).read()
        tokentxns_soup = BeautifulSoup(tokentxns_html_text, 'lxml')
        
        #the vertical table with all of the transactions
        transactionsTable = tokentxns_soup.find('tbody')

        #the horizontal table for a transaction
        transactionTable = transactionsTable.find('tr') #change this to findall for all transactions

        #the image for that transaction
        tokenImage = transactionTable.find('img')['src'] #empty image: "/images/main/empty-token.png"
        
        #the contract address. Finds the last href in transactiontable and only saves the contract address
        tokenContract = transactionTable.find_all('a', href = True)[-1]['href'][7:]

        self.scrapeTokenAddressPage(tokenContract)



    def scrapeTokenAddressPage(self, tokenContract):
        #needed to properly load the html
        tokenAddress_request = urllib.request.Request(f'https://bscscan.com/token/{tokenContract}', headers={'User-Agent': 'Mozilla/5.0'})
        tokenAddress_html_text = urllib.request.urlopen(tokenAddress_request).read()
        tokenAddress_soup = BeautifulSoup(tokenAddress_html_text, 'lxml')

        print(tokenAddress_soup)

        
