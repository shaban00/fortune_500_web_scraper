import requests
import certifi
import os
import json
from colorama import Fore, Style  # type: ignore
from fake_useragent import UserAgent  # type: ignore
from tabulate import tabulate  # type: ignore


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.google.com/',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-User': '?1',
}

verify = certifi.where()


def format_text(text: str, color=Fore.BLUE, bold: bool = True, print_result: bool = True) -> str:
    bold_text = Style.BRIGHT if bold else ''
    result = f"{bold_text}{color}{text}{Style.RESET_ALL}"

    return print(result) if print_result else result


def prompt(text: str = "choice: ") -> str:
    choice = input(format_text(f"\n{text}", print_result=False))

    return choice


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def error_messag(message: str, status_code: int = 400) -> None:
    format_text(f"{message} Status code: {status_code}", color=Fore.RED)


def make_get_request(url: str) -> str | None:
    ua = UserAgent()
    random_user_agent = ua.random
    headers["User-Agent"] = random_user_agent

    try:
        response = requests.get(url, headers=headers, verify=verify)
        if response.status_code == 200:
            return response.text
        else:
            error_messag(f"Failed to make request {url}", response.status_code)
            return None
    except requests.exceptions.SSLError:
        error_messag(f"SSL error occurred {url}")
        return None
    except requests.exceptions.Timeout:
        format_text(
            "Connection timed out. Please try again later.", color=Fore.RED)
        return None
    except requests.exceptions.RequestException as e:
        format_text(f"An error occurred: {e}", color=Fore.RED)
        return None


def company_tabulate_info(companies):
    if companies:
        data = []

        for company in companies:
            # Check if career_links is not empty or null
            if company.career_links:
                # Convert stringified JSON array to a Python list
                career_links = json.loads(company.career_links)
                # Format career links with bullets
                formatted_career_links = "\n".join(
                    format_text(f"• {link}", print_result=False) for link in career_links)
            else:
                formatted_career_links = ""

            row_data = [format_text(
                f"{company.company}", color=Fore.GREEN, print_result=False), formatted_career_links]

            data.append(row_data)

        headers = [format_text("Company", print_result=False), format_text(
            "Career Links", print_result=False)]
        
        print()
        print(tabulate(data, headers=headers, tablefmt="mixed_grid"))
    else:
        format_text("\nNo companies found in the database.")
