import requests
from bs4 import BeautifulSoup
import csv

PARENT_URL = "https://www.bidfta.com"
FILTERED_URL = f"{PARENT_URL}/category/all/1?location=?"  # replace ? with location code for auction sites
page = requests.get(FILTERED_URL)

formatted = BeautifulSoup(page.content, "html.parser")
auctions = formatted.find_all("div", class_="block")


# find auction attrs like text, date, title, etc
def find_auctions():
    fields = ['Title', 'Link', 'End date']
    rows = []
    for auction in auctions[1:]:
        auction_title = auction.find('p').find('span').text
        auction_link = PARENT_URL + auction.find('a')['href']
        auction_end = auction.find('span', class_='text-8 md:text-xs').text
        rows.append([auction_title, auction_link, auction_end])

        # find items for each auction and write to separate csv file
        find_auction_items(auction_link, auction_title)

    # write auction attrs to csv file
    with open(file='auctions/auctions.csv', mode='w', newline='') as auctions_csv:
        print("Writing auctions to csv...")
        writer = csv.writer(auctions_csv)
        writer.writerow(fields)
        writer.writerows(rows)
        print("Auctions.csv ready")


def find_auction_items(link, name):
    # extract auction item attrs: Name, Condition, MSRP, item No, no bidders, current bid
    # write auction items to csv
    items_page = requests.get(link)
    items_formatted = BeautifulSoup(items_page.content, "html.parser")
    items = items_formatted.find_all("div", class_="block")
    item_fields = []
    item_rows = []
    # fetch the link to each item and navigate to page to gather item details
    for i in range(1, len(items), 4):
        item_link = PARENT_URL + items[i].find('a')['href']
        item_page = requests.get(item_link)
        item_formatted = BeautifulSoup(item_page.content, "html.parser")
        item = item_formatted.find("table", class_="max-w-3xl")
        current_bid = item_formatted.find("span", class_="block mb-4 text-sm text-bidfta-blue-light font-bold transition duration-300 ease-in-out opacity-100")

        # extract item fields and metadata
        table_headings = item.find_all("td", class_="font-bold")
        # insert MSRP field at index 1 as it's contained in an h4 field
        table_headings.insert(1, item.find("h4"))
        table_data = item.find_all("td", class_="text-bidfta-gray-dark/60 p-2")
        item_title = table_data[0].text
        item_msrp = table_data[1].text
        item_brand = table_data[2].text
        item_desc = table_data[3].text
        item_model = table_data[4].text

        # prep fields and rows for csv
        item_fields = [heading.text for heading in table_headings[:5]]
        item_rows.append([item_title, item_msrp, item_brand, item_desc, item_model, current_bid.text[13:]])
    item_fields.append("Current Bid")
    filename = f"auctions/items/{name[9:]}.csv"
    with open(file=filename, mode='w', newline='') as csvfile:
        print("writing auction items to csv")
        writer = csv.writer(csvfile)
        writer.writerow(item_fields)
        writer.writerows(item_rows)
        print("auction items written")




