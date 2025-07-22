from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import seaborn as sns
import matplotlib.pyplot as plt

# SETUP CHROME DRIVER
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")

driver = webdriver.Chrome(options=options)
url = "https://www.linkedin.com/jobs/search/?keywords=data&location=Delhi%20NCR"

print("Opening LinkedIn Jobs...")
driver.get(url)
time.sleep(5)

# Scroll to load more jobs
for _ in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

# PARSE JOB LISTINGS
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

job_cards = soup.find_all("div", class_="base-card")

# Skill keywords
skills_list = ['Python', 'SQL', 'Excel', 'Tableau', 'Power BI', 'AWS', 'Spark', 'R', 'Hadoop']
job_data = []

for card in job_cards:
    title = card.find("h3").get_text(strip=True) if card.find("h3") else "N/A"
    company = card.find("h4").get_text(strip=True) if card.find("h4") else "N/A"
    location = card.find("span", class_="job-search-card__location").get_text(strip=True) if card.find("span", class_="job-search-card__location") else "Delhi NCR"
    job_text = card.get_text(" ", strip=True)

    # Find skills in the text

    found_skills = [skill for skill in skills_list if re.search(rf'\b{skill}\b', job_text, re.IGNORECASE)]

    if not found_skills:
        found_skills = ["None Listed"]

    for skill in found_skills:
        job_data.append({
            "Job Title": title,
            "Company": company,
            "Location": location,
            "Skill": skill
        })

# SAVE TO EXCEL
df = pd.DataFrame(job_data)

if not df.empty:
    df.to_excel("LinkedIn_Job_Trends_Delhi_NCR.xlsx", index=False)
    print("✅ Data saved to 'LinkedIn_Job_Trends_Delhi_NCR.xlsx'")

    # HEATMAP GENERATION

    # Clean sub-location (e.g., extract Noida, Gurgaon, etc.)

    df['City'] = df['Location'].str.extract(r'(Delhi|Noida|Gurgaon|Gurugram|Faridabad|Ghaziabad)', expand=False)
    df['City'].fillna('Other', inplace=True)

    # Top 10 most frequent skills

    top_skills = df['Skill'].value_counts().nlargest(10).index.tolist()
    df_top_skills = df[df['Skill'].isin(top_skills)]

    # Pivot: City vs Skill

    pivot = df_top_skills.pivot_table(index='City', columns='Skill', aggfunc='size', fill_value=0)

    # Heatmap

    plt.figure(figsize=(12, 6))
    sns.heatmap(pivot, annot=True, fmt='d', cmap='YlGnBu')
    plt.title("Top 10 Skills by City (LinkedIn – Delhi NCR Jobs)")
    plt.ylabel("City")
    plt.xlabel("Skill")
    plt.tight_layout()
    plt.savefig("top_10_skills_by_city_heatmap.png")
    print("Heatmap saved as 'top_10_skills_by_city_heatmap.png'")
    plt.show()

else:
    print("⚠️ No job data was extracted. LinkedIn may have blocked the page or the structure has changed.")
