from Scraper import Scraper

iters = 1
def main():
    scraper = Scraper(200, 15000, True, 5, 5, 'test.csv')

    for i in range(iters):
        print(f"Scraping progress: {i+1}/{iters}")
        potentialCoins = scraper.run()
        scraper.writeToCsv(potentialCoins)

if __name__ == "__main__":
    main()
