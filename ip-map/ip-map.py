# Requirements
import shodan
import re
import os
import sys
import time
from colorama import Fore, init
from shodan.cli.helpers import get_api_key


init(autoreset=True)

# Get API Key From Shodan
shodan_api_key = get_api_key();

api = shodan.Shodan(shodan_api_key)

time.sleep(0.5)


# Keywords
ip_keys = ['ip_str','ports','os','country_code','org','region_code','domains','hostnames','latitude','longitude','tags']
ip_words = ['IP: ','Port: ','OS ','Country Code: ','Organization: ','Region Code: ','Domains: ','Host Name: ','Latitude: ','Longitude: ','Tags: ']

search_keys = ['ip_str','port','os','org','transport','domains','hostnames','data']
search_words = ['IP: ','Port: ','OS: ','Organization: ','Layer: ','Domains: ','Host Name: ','Data: ']


# Save Flags

# 0 = no save
# 1 = search from ipList.txt
# 2 = save search result
# 3 = save iplist
# 4 = save both
# 5 = save ip result

temp = ''
file_name = ''


# Write On File
def writer(file_name,data):
    file = open(file_name + ".txt","a")
    file.write(data)
    file.close()


# Print Line
def ptrLine():
    print("==" * 40)

# Color Print Functions
def ptrAlert(msg):
    print(Fore.RED + "[!]" + msg)

def ptrMsg(msg):
    print(Fore.RED + "[*]" + Fore.GREEN + msg)

def ptrChoice(msg):
    temp = input(Fore.RED + "[*]" + Fore.LIGHTBLUE_EX + msg + Fore.RESET + "(y/n)")
    return temp

def ptrInput(msg):
    temp = input(Fore.GREEN + "[*]" + Fore.LIGHTBLUE_EX + msg + Fore.RESET)
    return temp

def ptrResult(msg, msg2):
    print(Fore.RED + "[+]" + Fore.LIGHTGREEN_EX + msg + Fore.RESET + msg2)
    
def ptrSkip(msg):
    print(Fore.MAGENTA + "[~]" + Fore.LIGHTBLUE_EX + msg)

def ptrSuccess(msg):
    print(Fore.GREEN + "[✓]" + Fore.LIGHTBLUE_EX + msg)


# Execute Query And Print Result
def shodan_search(flag, data, file_name, query):
        count = 0
        for result in api.search_cursor(query): 
            print("\n\n")
            ptrLine()
            count += 1
            for i in range(8):
                ptrResult(search_words[i], str(result[search_keys[i]]))
          
            ptrMsg("Searched Result: {0} Search Query: {1}".format(str(count), str(query)))

            if flag == 2 or flag == 4:
                for i in range(8):
                    data = data + (search_words[i] + str(result[search_keys[i]]) + "\n")

                writer(file_name,data)

            if flag == 3 or flag == 4:
                data = (str(result[search_keys[0]]) + "\n")
                writer("ipList", data)
            
            time.sleep(0.1)
            # Terminate Program When Counter Over 100
            if count >= 100:
                ptrAlert("Retry limit reached. Terminate Program.")
                exit()

# Shodan Search With Query
def search_func():
    try:
        data = ''
        flag = 0

        # Select Save Result File
        temp = ptrChoice("Do you want to save the result file?")
        if temp.startswith("y" or "Y"):
            file_name = ptrInput("Enter the file name (No extension needed.): ")
            if os.path.exists(file_name + ".txt"):
                ptrAlert("You can't save same name.")
                exit()
            flag = 2
        else:
            ptrSkip("Saving skipped.")

        # Select Save ipList File
        temp = ptrChoice("Do you want to save the ipList separately?")
        if temp.startswith("y" or "Y"):
            if flag == 2:
                flag = 4
            else:
                flag = 3
            ptrSuccess("Save ipList separately.")
        else:
            ptrSkip("Saving skipped.")

        # Input Query
        query = ptrInput("Enter Search Keyword: ")

        # Print Result Count
        results_count = api.count(query, facets=None)
        ptrMsg("Result Found: {0}".format(results_count['total']))

        shodan_search(flag, data, file_name, query)

        
    # Error Exception
    except shodan.APIError as e:
        ptrAlert("Shodan Error: {0}".format(e))


# Shodan Search With ipList.txt File
def shodan_ip():
    try:
        if os.path.exists("./ipList.txt") and os.path.getsize("./ipList.txt") > 0:
            # Open ipList.txt And Search
            with open("ipList.txt", "r") as f:
                lines = f.readlines()
            
                data = ''
                flag = 0
                
                # Select Save Result File
                temp = ptrChoice("Do you want to save the result file?")
            
                if temp.startswith("y" or "Y"):
                    file_name = ptrInput("Enter the file name (No extension needed.): ")
                    if os.path.exists(file_name + ".txt"):
                        ptrAlert("You can't save same name.")
                        exit()
                    flag = 5
                else:
                    ptrSkip("Saving skipped.")
                
                # Read Ip From ipLine.txt
                for ip in lines:
                    result = api.host(str(ip)) 
                    print("\n\n")
                    ptrLine()
                
                    for i in range(11):
                        ptrResult(ip_words[i], str(result[ip_keys[i]]))
                
                    if flag == 5:
                        for i in range(11):
                            data = data + (ip_words[i] + str(result[ip_keys[i]]) + "\n")
                        data = data + "\n"
                        writer(file_name, data)
                    time.sleep(0.1)
                
        else:
            ptrAlert("Error File \"ipList.txt\" Does not Exist")

    # Error Exception
    except shodan.APIError as e:
        ptrAlert("Shodan Error: {0}".format(e))


if __name__ == "__main__":

    print(Fore.YELLOW + "WELCOME to Ip-Map" + Fore.RESET)
    
    temp = ptrChoice("Search From ipList.txt?")
    
    if temp.startswith("y" or "Y"):
        ptrSuccess("import ipList.txt ...")
        shodan_ip()
    else:
        ptrSuccess("Search Wichout ipList.txt ...")
        search_func()
