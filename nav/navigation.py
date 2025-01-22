from re import sub
import sys
sys.path.append("..")
from models.job import Job
import time

from typing import List, Optional

from markdownify import markdownify as md

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import chromedriver_autoinstaller

from .conversation_llm_cv import JobChecker
import csv


class LinkedInJobScraper:
    """
    A LinkedIn job scraper that:
      - Logs into LinkedIn
      - Navigates to a job search based on 'discipline' and 'location' from cv_profile
      - Iterates through job cards on the page
      - Extracts job information
      - Checks if the job matches the candidate’s CV
      - Scrolls through the page repeatedly until no more new job cards are found

    The logic remains the same as your original code, but with added type hints,
    docstrings, error handling, and minor improvements. Variable names and method
    signatures are unchanged to maintain your original flow.
    """

    BASE_URL = "https://www.linkedin.com/"

    def __init__(
        self,
        cv_profile,
        username: str,
        password: str,
        headless: bool = False,
    ):
        """
        :param cv_profile: A CVProfile-like object containing candidate data
        :param username: LinkedIn username (email)
        :param password: LinkedIn password
        :param headless: Whether to run Chrome in headless mode
        """
        self.username = username
        self.password = password
        self.headless = headless
        self.cv_profile = cv_profile

        # This is your LLM-based job checker
        self.jobchecker = JobChecker()

        # Will be assigned in init_browser()
        self.driver: Optional[webdriver.Chrome] = None
        
        self.job_counter = 0
        
        self.csv_path = "matched_jobs.csv"
        
        self._init_csv()

    def init_browser(self) -> None:
        """
        Installs (if necessary) and launches a Chrome driver with specified options.
        """
        chromedriver_autoinstaller.install()
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        
    def _init_csv(self) -> None:
        try:
            with open(self.csv_path, "r", encoding="utf-8") as f:
                pass
        except FileNotFoundError:
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["row", "role", "company", "location", "description", "link"])

    # Pseudocode changes in run() to keep it short:

    def run(self) -> None:
        self.init_browser()
        try:
            self.login()

            # We'll loop pages until we see "No matching jobs found."
            start_offset = 0
            while True:
                # Build the page URL with `start` param
                # e.g. &start=25, &start=50, etc.
                self.navigate_search(self.cv_profile.discipline, self.cv_profile.location, start=start_offset)

                found_any_jobs = self.parse_job_cards()  # parse them

                # If the page HTML has "No matching jobs found." or parse_job_cards returns no jobs
                if not found_any_jobs or self._page_has_no_jobs():
                    print("[INFO] No more jobs, stopping.")
                    break

                # Increase offset by 25 for next page
                start_offset += 25

        except Exception as e:
            print(f"[ERROR] A top-level error occurred: {e}")
        finally:
            self.__del__()
    
    def _page_has_no_jobs(self) -> bool:
        page_source = self.driver.page_source
        return "No matching jobs found." in page_source



    def login(self) -> None:
        if not self.driver:
            raise ValueError("WebDriver is not initialized.")

        self.driver.get(f"{self.BASE_URL}login")

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            submit_button = self.driver.find_element(
                By.CSS_SELECTOR, "button[type='submit']"
            )

            email.send_keys(self.username)
            password_field.send_keys(self.password)
            submit_button.click()

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "artdeco-card"))
            )
            print("LOGIN SUCCESSFUL")
        except (NoSuchElementException, TimeoutException, WebDriverException) as e:
            print(f"[ERROR] Login failed: {e}")
            raise

    def __url__space_sub__(self, query: str) -> str:
        """
        Replaces spaces in the query with '%20' for URL formatting.

        :param query: A string to be URL-encoded for spaces
        :return: The same string with spaces replaced by '%20'
        """
        return sub(" ", "%20", query)

    def navigate_search(self, query: str, location: str, start:int = 0) -> None:
        if not self.driver:
            raise ValueError("WebDriver is not initialized.")

        query = self.__url__space_sub__(query) 
        location = self.__url__space_sub__(location)

        # Base search URL
        search_url = f"{self.BASE_URL}jobs/search/?keywords={query}&location={location}"
        
        # Only add start parameter if not zero
        if start > 0:
            search_url += f"&start={start}"

        self.driver.get(search_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[class*='jobs-search-results-list']")
                )
            )
            print("JOB SEARCH NAV SUCCESSFUL")
        except TimeoutException as e:
            print(f"[ERROR] Could not load job search results: {e}")
            raise

    def parse_job_cards(self) -> bool:
        if not self.driver:
            raise ValueError("WebDriver is not initialized.")

        processed_jobs = []
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        found_job_list = False  # We'll flip this to True if we see any jobs

        while True:
            jobs_cards = self.driver.find_elements(By.CSS_SELECTOR, "li[data-occludable-job-id]")
            if jobs_cards:
                found_job_list = True  # We found at least one job in this round

            for job_card in jobs_cards:
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", job_card)
                    time.sleep(0.5)

                    job_info = self.extract_job_info(job_card)
                    output = self.jobchecker.check_job(self.cv_profile, job_info)

                    if output and output.get("match") == "True":
                        print("MATCH FOUND")
                        link = self._extract_job_link(job_card)
                        # Save to CSV as before
                        job = Job(
                            match=True,
                            role=output.get("role", ""),
                            company=output.get("company", ""),
                            location=output.get("location", ""),
                            description=output.get("description", ""),
                            link=link,
                        )
                        self._save_job_csv(job)

                    job_card.click()
                    time.sleep(1)
                    processed_jobs.append(job_card)

                except Exception as e:
                    print(f"Error processing job: {str(e)}")
                    continue

            self.scroll_to_page_bottom()
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # No more new content to scroll
            last_height = new_height

        return found_job_list

    
    def _save_job_csv(self, job: Job) -> None:
        self.job_counter += 1
        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                self.job_counter,
                job.role,
                job.company,
                job.location,
                job.description,
                job.link,
            ])

    def scroll_to_page_bottom(self) -> None:
        """
        Scrolls the window to the bottom of the page to trigger lazy-loaded items.
        """
        if not self.driver:
            raise ValueError("WebDriver is not initialized.")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    def extract_job_info(self, job_element: WebElement) -> str:
        """
        Extracts the job card HTML and the expanded job description HTML,
        then converts them to Markdown.

        :param job_element: A Selenium WebElement representing a single job listing
        :return: Markdown-formatted text containing the job info
        """
        card_html = job_element.get_attribute("outerHTML")

        job_element.click()
        time.sleep(1)

        # Wait for the job description panel
        try:
            desc_panel = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-description"))
            )
            desc_html = desc_panel.get_attribute("outerHTML")
        except TimeoutException:
            desc_html = ""

        full_html = f"{card_html}\n{desc_html}"
        converted_docs = md(full_html, strip=["a"]) 
        return converted_docs
    

    def _extract_job_link(self, job_element: WebElement) -> str:
        try:
            anchor = job_element.find_element(By.TAG_NAME, "a")
            return anchor.get_attribute("href") or ""
        except NoSuchElementException:
            return ""
        
    def go_to_next_page(self) -> bool:
        if not self.driver:
            raise ValueError("WebDriver is not initialized.")

        try:
            pagination = self.driver.find_element(By.CLASS_NAME, "artdeco-pagination__pages")
            next_btn = pagination.find_element(By.XPATH, ".//button[@aria-label='Next page']")
            if "disabled" in next_btn.get_attribute("class"):
                return False
            else:
                next_btn.click()
                # Let the page load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list"))
                )
                print("[INFO] Moved to next page.")
                time.sleep(2)
                return True
        except NoSuchElementException:
            print("[INFO] No next page found.")
            return False
        except TimeoutException:
            print("[INFO] Next page took too long to load, stopping.")
            return False


    def __del__(self) -> None:
        """
        Ensures that the driver is properly quit when the scraper is deleted.
        """
        if getattr(self, "driver", None):
            try:
                self.driver.quit()
                print("[INFO] Browser closed.")
            except Exception as e:
                print(f"[WARN] Error closing browser: {e}")
