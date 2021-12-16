from Scraper import Scraper

iters = 1
def main():
    scraper = Scraper(200,5000,0,0,0,0,0, True, 'potentialCoins.csv')

    for i in range(iters):
        print(f"Scraping progress: {i+1}/{iters}")
        potentialCoins = scraper.run()
        scraper.writeToCsv(potentialCoins)


if __name__ == "__main__":
    main()
