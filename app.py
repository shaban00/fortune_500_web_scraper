import re
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from art import text2art  # type: ignore
from tabulate import tabulate  # type: ignore
from colorama import Fore  # type: ignore
from tqdm import tqdm  # type: ignore
from models.database import create_db_session
from models.company import Company
from utils import format_text, prompt, clear_screen, make_get_request, company_tabulate_info

base_url = "https://www.zyxware.com/articles/4344/list-of-fortune-500-companies-and-their-websites"


def scrape_company_website(website: str) -> str:
    response = make_get_request(website)

    if response:
        soup = BeautifulSoup(response, 'html.parser')
        all_hrefs = soup.find_all('a', href=re.compile(
            r'career?|jobs?|internship?', re.IGNORECASE))
        links = set()

        if all_hrefs:
            for link in all_hrefs:
                career_url = link.get('href')
                # Convert relative URLs to absolute URLs
                if career_url.startswith('/'):
                    career_url = urljoin(website, career_url).strip()
                links.add(career_url)

            return json.dumps(list(links))
        else:
            format_text("No career links found.", color=Fore.BLUE)
            return ""


def scrape_and_insert_data():
    response = make_get_request(base_url)

    if (response):
        soup = BeautifulSoup(response, 'html.parser')
        tables = soup.find_all('table', class_='table')

        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip the header row
            # Create tqdm progress bar
            progress_bar = tqdm(rows, desc="Processing", total=len(rows))

            for row in progress_bar:
                cells = row.find_all('td')
                rank = cells[0].text.strip()
                company = cells[1].text.strip()
                website = cells[2].text.strip()

                if not website.startswith(('http://', 'https://')):
                    website = 'https://' + website  # Assuming 'http://' if missing

                with create_db_session() as session:
                    existing_company = session.query(Company).filter_by(
                        company=company, website=website).first()

                    if existing_company:
                        format_text(
                            f"{company} already exists. Skipping insertion.")
                    else:
                        career_links = scrape_company_website(website)

                        company = Company(
                            rank=rank, company=company, website=website, career_links=career_links)
                        session.add(company)
                        session.commit()


def display_companies():
    with create_db_session() as session:
        companies = session.query(Company).order_by(Company.rank).all()
        if companies:
            headers = [format_text("Rank", print_result=False), format_text(
                "Company", print_result=False), format_text("Website", print_result=False), format_text("Scrapped At", print_result=False)]
            data = [[company.rank, company.company, company.website,
                     company.created_at] for company in companies]
            print()
            print(tabulate(data, headers=headers, tablefmt="mixed_grid"))
        else:
            format_text("\nNo companies found in the database.")


def display_company_career_links():
    with create_db_session() as session:
        companies = session.query(Company).order_by(Company.rank).all()
        company_tabulate_info(companies)


def search_company():

    while True:
        search_options()

        choice = prompt()

        if choice == '1':
            rank = input("Enter rank to search: ")
            search_by_rank(rank)
        elif choice == '2':
            company = input("Enter company name to search: ")
            search_by_company(company)
        elif choice == '3':
            start_rank = int(input("Enter start rank to search: "))
            end_rank = int(input("Enter end rank to search: "))
            search_by_range(start_rank, end_rank)
        elif choice == '4':
            break
        else:
            format_text(
                "\nInvalid choice. Please enter a valid option (1-6)", color=Fore.RED)


def search_by_rank(rank):
    with create_db_session() as session:
        companies = session.query(Company).filter_by(
            rank=rank).order_by(Company.rank).all()
        company_tabulate_info(companies)


def search_by_company(company):
    with create_db_session() as session:
        companies = session.query(Company).filter_by(
            company=company).order_by(Company.rank).all()
        company_tabulate_info(companies)


def search_by_range(start_rank, end_rank):
    with create_db_session() as session:
        companies = session.query(Company).filter(Company.rank >= start_rank,
                                                  Company.rank <= end_rank).order_by(Company.rank).all()
        company_tabulate_info(companies)


def delete_by_rank(rank):
    with create_db_session() as session:
        session.query(Company).filter_by(rank=rank).delete()
        session.commit()
        format_text("\nCompany deleted successfully 👍", color=Fore.GREEN)


def delete_by_company(company):
    with create_db_session() as session:
        session.query(Company).filter_by(company=company).delete()
        session.commit()
        format_text("\nCompany deleted successfully 👍", color=Fore.GREEN)


def delete_by_website(website):
    with create_db_session() as session:
        session.query(Company).filter_by(website=website).delete()
        session.commit()
        format_text("\nCompany deleted successfully 👍", color=Fore.GREEN)


def delete_by_range(start_rank, end_rank):
    with create_db_session() as session:
        session.query(Company).filter(Company.rank >= start_rank,
                                      Company.rank <= end_rank).delete()
        session.commit()
        format_text("\nCompanies deleted successfully 👍", color=Fore.GREEN)


def delete_all_companies():
    with create_db_session() as session:
        session.query(Company).delete()
        session.commit()
        format_text("\nCompanies deleted successfully 👍", color=Fore.GREEN)


def delete_company():

    while True:
        delete_options()

        choice = prompt()

        if choice == '1':
            rank = input("Enter rank to delete: ")
            delete_by_rank(rank)
        elif choice == '2':
            company = input("Enter company name to delete: ")
            delete_by_company(company)
        elif choice == '3':
            website = input("Enter website to delete: ")
            delete_by_website(website)
        elif choice == '4':
            start_rank = int(input("Enter start rank to delete: "))
            end_rank = int(input("Enter end rank to delete: "))
            delete_by_range(start_rank, end_rank)
        elif choice == '5':
            delete_all_companies()
        elif choice == '6':
            break
        else:
            format_text(
                "\nInvalid choice. Please enter a valid option (1-6)", color=Fore.RED)


def search_options():
    format_text("\nSelect search method\n", color=Fore.GREEN)

    print("1. Search by rank")
    print("2. Search by company")
    print("3. Search by range")
    print("4. Back to main")


def delete_options():
    format_text("\nSelect deletion method\n", color=Fore.GREEN)

    print("1. Delete by rank")
    print("2. Delete by company")
    print("3. Delete by website")
    print("4. Delete by range")
    print("5. Delete all companies")
    print("6. Back to main")


def main_options():
    banner_text = text2art("Fortune 500 Web Scraper")

    format_text(banner_text, color=Fore.GREEN)

    print("1. Scrape and insert data into database")
    print("2. Display all companies")
    print("3. Display all company career links")
    print("4. Search company")
    print("5. Delete company")
    print("6. Exit")


def main():
    clear_screen()

    while True:
        main_options()

        choice = prompt()

        if choice == '1':
            scrape_and_insert_data()
        elif choice == '2':
            display_companies()
        elif choice == '3':
            display_company_career_links()
        elif choice == '4':
            search_company()
        elif choice == '5':
            delete_company()
        elif choice == '6':
            format_text(f"\n{'Exiting. Good Bye...👋👋👋👋👋'}\n", color=Fore.RED)
            break
        else:
            format_text(
                "\nInvalid choice. Please enter a valid option (1-5)", color=Fore.RED)

        input("\nPress Enter to continue...")

        clear_screen()


if __name__ == "__main__":
    main()
