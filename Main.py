from Scraper import Scraper

iters = 3
def main():
    scraper = Scraper(200,15000,0,0,0,0,0, True, 5, 5, 'test.csv')

    for i in range(iters):
        print(f"Scraping progress: {i+1}/{iters}")
        potentialCoins = scraper.run()
        scraper.writeToCsv(potentialCoins)
    #res = scraper.isHoneypotSecureAndWithinTaxRange('0xc6f8532439f4ec88b98b9cc545626960604182db')
    #print(res)

if __name__ == "__main__":
    main()
