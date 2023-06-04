#!/usr/bin/python3
import urllib.request
import urllib.parse
import json
import os
from pick import pick
import zipfile
import glob

# Colors
Red          = "\033[31m"
Green        = "\033[32m"
White        = "\033[97m"


# Load the main json page
url = "https://chaos-data.projectdiscovery.io/index.json"
request_site = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
webpage = urllib.request.urlopen(request_site).read()
data_json = json.loads(webpage)


# To solve error 403 while downloading
opener = urllib.request.URLopener()
opener.addheader('User-Agent', 'Mozilla/5.0')

def get_file_name(download_link):
    return os.path.basename(download_link)

def download(link, save_dir, file_name):
    if not os.path.exists(f'{save_dir}/{file_name.removesuffix(".zip")}'):
        os.makedirs(f'{save_dir}/{file_name.removesuffix(".zip")}')
    
    # To solve UnicodeError
    link = urllib.parse.urlsplit(link)
    link = list(link)
    link[2] = urllib.parse.quote(link[2])
    link = urllib.parse.urlunsplit(link)
    opener.retrieve(link, os.path.join(f'{save_dir}/{file_name.removesuffix(".zip")}', file_name))
    unzip_files(file_name, f'{save_dir}/{file_name.removesuffix(".zip")}')
    print(f"{Red}[+]{White} {file_name} Done {Green}[\u2713]{White}")

def download_all_programmes():
    save_dir = "./all_programmes"
    for link in data_json:
        download_link = link["URL"]
        file_name = get_file_name(download_link)
        download(download_link, save_dir, file_name)
    merg_files(save_dir)

def download_offer_bounty():
    save_dir = "./offer_bounty"
    for data in data_json:
        if data["bounty"] == True:
            file_name = get_file_name(data["URL"])
            download(data["URL"], save_dir, file_name)
    merg_files(save_dir)

def download_not_offer_bounty():
    save_dir = "./not_offer_bounty"
    for data in data_json:
        if data["bounty"] == False:
            file_name = get_file_name(data["URL"])
            download(data["URL"], save_dir, file_name)
    merg_files(save_dir)

def download_by_platform(platform_name):
    save_dir = f"{platform_name}"
    for program in data_json:
        if program['platform'] == platform_name:
            if program['platform'] == "":
                save_dir = "self hosted"
            file_name = get_file_name(program["URL"])
            download(program["URL"], save_dir, file_name)
    merg_files(save_dir)

def download_specific_program(program_name):
    save_dir = f"{program_name}"
    for program in data_json:
        if program['name'] == program_name:
            file_name = get_file_name(program["URL"])
            download(program["URL"], save_dir, file_name)
    merg_files(save_dir)

def download_new_subdomain():
    save_dir = "./new_subdomains"
    for program in data_json:
        if program["change"] != 0:
            file_name = get_file_name(program["URL"])
            download(program["URL"], save_dir, file_name)
    merg_files(save_dir)

def new_subdomains_and_offer_bounty():
    save_dir = "./new_subdomains_and_offer_bounty"
    for data in data_json:
        if (data["bounty"] == True) and (data["change"] != 0):
            file_name = get_file_name(data["URL"])
            download(data["URL"], save_dir, file_name)
    merg_files(save_dir)

def new_subdomain_and_offer_bounty_and_platform(platform_name):
    save_dir = f"./new_subdomain_and_offer_bounty_and_{platform_name}"
    for data in data_json:
        if (data["bounty"] == True) and (data["change"] != 0) and (data['platform'] == platform_name):
            if data['platform'] == "":
                save_dir = "new_subdomain_and_offer_bounty_and_self_hosted"
            file_name = get_file_name(data["URL"])
            download(data["URL"], save_dir, file_name)
    merg_files(save_dir)

def new_subdomain_and_platform(platform_name):
    save_dir = f"./new_subdomain_and_offer_bounty_and_{platform_name}"
    for data in data_json:
        if (data["change"] != 0) and (data['platform'] == platform_name):
            if data['platform'] == "":
                save_dir = "./new_subdomain_and_offer_bounty_and_self_hosted"
            file_name = get_file_name(data["URL"])
            download(data["URL"], save_dir, file_name)
    merg_files(save_dir)

def new_subdomain_and_not_offer_bounty():
    save_dir = "./new_subdomain_and_not_offer_bounty"
    for program in data_json:
        if (program["change"] != 0) and (program["bounty"] == False):
            file_name = get_file_name(program["URL"])
            download(program["URL"], save_dir, file_name)
    merg_files(save_dir)

def new_subdomain_and_not_offer_bounty_and_platform(platform_name):
    save_dir = f"./new_subdomain_and_not_offer_bounty_and_{platform_name}"
    for program in data_json:
        if (program["change"] != 0) and (program["bounty"] == False) and (data['platform'] == platform_name):
            if data['platform'] == "":
                save_dir = "./new_subdomain_and_not_offer_bounty_and_self_hosted"
            file_name = get_file_name(program["URL"])
            download(program["URL"], save_dir, file_name)
    merg_files(save_dir)

def offer_bounty_and_platform(platform_name):
    save_dir = f"./offer_bounty_and_{platform_name}"
    for program in data_json:
        if (program["bounty"] == True) and (program['platform'] == platform_name):
            if program['platform'] == "":
                save_dir = "./offer_bounty_and_self_hosted"
            file_name = get_file_name(program["URL"])
            download(program["URL"], save_dir, file_name)
    merg_files(save_dir)

def not_offer_bounty_and_platform(platform_name):
    save_dir = f"./not_offer_bounty_and{platform_name}"
    for program in data_json:
        if (program["bounty"] == False) and (data['platform'] == platform_name):
            if data['platform'] == "":
                save_dir = "./not_offer_bounty_and_self_hosted"
            file_name = get_file_name(program["URL"])
            download(program["URL"], save_dir, file_name)
    merg_files(save_dir)

def unzip_files(file_name, save_dir):
    with zipfile.ZipFile(f'{save_dir}/{file_name}', 'r') as zip:
        zip.extractall(save_dir)
    os.remove(f"{save_dir}/{file_name}")

def merg_files(first_dir):
    read_files = glob.glob(f"{first_dir}/*/*.txt")
    with open(f"{first_dir}.txt", "wb") as outfile:
        for f in read_files:
            with open(f, "rb") as infile:
                outfile.write(infile.read())
    print_menu = "Do you want to use httprobe or httpx?"
    print_options = ["httprobe", "httpx", "exit"]
    option, index = pick(print_options, print_menu)    
    if index == 0:
        httprobe_command(f"{first_dir}.txt")
    elif index == 1:
        httpx_command(f"{first_dir}.txt")
    else:
        exit(0)

def httprobe_command(file_name):
    os.system(f"cat {file_name} | httprobe -c 1000 | tee -a live_domains_{file_name}_httprobe.txt")

def httpx_command(file_name):
    os.system(f"cat {file_name} | httpx -t 200 -rl 600 | tee -a live_domains_{file_name}_httpx.txt ")

main_title = """

          _____ _                       _____                      _                 _           
         / ____| |                     |  __ \                    | |               | |          
        | |    | |__   __ _  ___  ___  | |  | | _____      ___ __ | | ___   __ _  __| | ___ _ __ 
        | |    | '_ \ / _` |/ _ \/ __| | |  | |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|
        | |____| | | | (_| | (_) \__ \ | |__| | (_) \ V  V /| | | | | (_) | (_| | (_| |  __/ |   
         \_____|_| |_|\__,_|\___/|___/ |_____/ \___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|\___|_|   

            This tools is designed to deal with chaos api from projectdiscovery.io
                        https://chaos.projectdiscovery.io/
"""
main_options = ["all programmes", "offer bounty", "not offer bounty", "platform", "new subdomain",
                "new subdomain and offer bounty", "new subdomain and offer bounty and platform", "new subdomain and platform", 
                "new subdomain and not offer bounty", "new subdomain and not offer bounty and platform", 
                "offer bounty and platform", "not offer bounty and platform" ,"specific program"]
option, index = pick(main_options, main_title)

sub_title = "choose your platform"
sub_menu = ["hackerone", "bugcrowd", "yeswehack", "self hosted"]



if index == 0:
    download_all_programmes()
elif index == 1:
    download_offer_bounty()
elif index == 2:
    download_not_offer_bounty()
elif index == 3:
    sub_option, sub_index = pick(sub_menu, sub_title)
    if sub_index == 0:
        download_by_platform(sub_option)
    elif sub_index == 1:
        download_by_platform(sub_option)
    elif sub_index == 2:
        download_by_platform(sub_option)
    else:
        download_by_platform("")
elif index == 4:
    download_new_subdomain()
elif index == 5:
    new_subdomains_and_offer_bounty()
elif index == 6:
    sub_option, sub_index = pick(sub_menu, sub_title)
    if sub_index == 0:
        new_subdomain_and_offer_bounty_and_platform(sub_option)
    elif sub_index == 1:
        new_subdomain_and_offer_bounty_and_platform(sub_option)
    elif sub_index == 2:
        new_subdomain_and_offer_bounty_and_platform(sub_option)
    else:
        new_subdomain_and_offer_bounty_and_platform("")
elif index == 7:
    sub_option, sub_index = pick(sub_menu, sub_title)
    if sub_index == 0:
        new_subdomain_and_platform(sub_option)
    elif sub_index == 1:
        new_subdomain_and_platform(sub_option)
    elif sub_index == 2:
        new_subdomain_and_platform(sub_option)
    else:
        new_subdomain_and_platform("")
elif index == 8:
    new_subdomain_and_not_offer_bounty()
elif index == 9:
    sub_option, sub_index = pick(sub_menu, sub_title)
    if sub_index == 0:
        new_subdomain_and_not_offer_bounty_and_platform(sub_option)
    elif sub_index == 1:
        new_subdomain_and_not_offer_bounty_and_platform(sub_option)
    elif sub_index == 2:
        new_subdomain_and_not_offer_bounty_and_platform(sub_option)
    else:
        new_subdomain_and_not_offer_bounty_and_platform("")
elif index == 10:
    sub_option, sub_index = pick(sub_menu, sub_title)
    if sub_index == 0:
        offer_bounty_and_platform(sub_option)
    elif sub_index == 1:
        offer_bounty_and_platform(sub_option)
    elif sub_index == 2:
        offer_bounty_and_platform(sub_option)
    else:
        offer_bounty_and_platform("")
elif index == 11:
    sub_option, sub_index = pick(sub_menu, sub_title)
    if sub_index == 0:
        not_offer_bounty_and_platform(sub_option)
    elif sub_index == 1:
        not_offer_bounty_and_platform(sub_option)
    elif sub_index == 2:
        not_offer_bounty_and_platform(sub_option)
    else:
        not_offer_bounty_and_platform("")
else:
    programe_names = []
    for name in data_json:
        programe_names.append(name["name"])
    subdomain_title = "Choose your program"
    programe_name = pick(programe_names, subdomain_title)
    download_specific_program(programe_name[0])