from bs4 import BeautifulSoup
import requests
import io
import pandas as pd
from pandas import ExcelWriter
from openpyxl.workbook import Workbook

# gets all the html objects that contain the relevant links

def get_links(soup):
    link_containers = soup.find_all("li", {"class":"rule-link"})
    rule_links = []

    # appends them to a list to be used later
    for i in link_containers:
        link = "https://www.cloudconformity.com" + i.a.get('href')
        rule_links.append(link)

    return rule_links

# method for getting the required data from the list of links
def get_data(rule_links, w, row):
    for link in rule_links:
        source = requests.get(link).text
        soup = BeautifulSoup(source, 'html.parser')
        try:
            azure_service = soup.find("div", {"class":"nav"}).text.strip()

            while '  ' in azure_service:
                azure_service = azure_service.replace('  ', '')

            azure_service = azure_service.split("\n")
            azure_service = ' '.join(azure_service)
            azure_service = azure_service.split("  ")
            azure_service = azure_service[2].strip()
        except:
            azure_service = ''

        try:
            title = soup.h1.text
        except:
            title = 'NA'

        try:
            risk_level_list = soup.find("div", {"class":"risk-level"}).text.split()[2:]
            risk_level = ' '.join([str(elem) for elem in risk_level_list])
            risk_level = risk_level.replace("\n","")
        except:
            risk_level = 'NA'

        try:
            rule_id = soup.find("div", {"class":"rule-id"}).text.split(':')[1].strip().replace("\n","")
        except:
            rule_id = 'NA'

        try:
            description = soup.find("div", {"class":"box text"}).p.text.strip().replace(',','').replace("\n","")
        except:
            description = 'NA'

        try:
            rationale = soup.find("p", {"class":"lead"}).text.strip().replace(',','').replace("\n","")
        except:
            rationale = 'NA'

        try:
            audit_goal = (soup.find("div",{"class":"header-text"}).p.text.strip().replace(',','').replace("\n",""))
        except:
            audit_goal = 'NA'

        # lists of steps for auditing and remediation
        steps = (soup.findAll("div",{"class":"overlay"}))

        try:
            audit_using_console = steps[1].text.replace(',','').replace('			','').strip()
        except:
            audit_using_console = ''

        try:
            audit_using_cli = steps[3].text.replace(',', '').replace('			','').strip()
        except:
            audit_using_cli = ''

        try:
            remediation_using_console = steps[5].text.replace(',', '').replace('			','').strip()
        except:
            remediation_using_console = ''

        try:
            remediation_using_cli = steps[7].text.replace(',', '').replace('			','').strip()
        except:
            remediation_using_cli = ''

        # format the relevant data into a csv friendly string, and then write it to the file
        csv_string = title + "," + azure_service + "," + risk_level + ',' + rule_id + ',' + description + ',' + rationale + ',' + audit_goal + ',' + audit_using_console + ',' + audit_using_cli + ',' + remediation_using_console + ',' + remediation_using_cli + "," + link
        print(csv_string)
        row = row + 1
        # Create dataframe and write to file
        df = pd.DataFrame(columns=[title,azure_service,risk_level,rule_id,description,rationale,audit_goal,audit_using_console,audit_using_cli, remediation_using_console, remediation_using_cli, link])
        df.to_excel(w, startrow=row, index=False)
        w.save()

def main():
    # variables: address to gather links from and variables for html parsing
    address = "https://www.cloudconformity.com/knowledge-base/azure/"
    source = requests.get(address).text
    soup = BeautifulSoup(source, 'html.parser')
    w = pd.ExcelWriter("azure_bp_rules.xlsx")
    row = 0;
    df = pd.DataFrame(columns=["Title", "Azure Service", "Risk", "ID", "Description", "Rationale", "Audit Goal", "Audit Console", "Audit Cli", "Remediation Console", "Remediation Cli", "Link"])
    df.to_excel(w, startrow=row, index=False)
    w.save()

    # calls method to get all rule links from the 'address' variables and iterates through the links to get required data
    links = get_links(soup)
    get_data(links, w, row)



if __name__ == '__main__':
    main()


