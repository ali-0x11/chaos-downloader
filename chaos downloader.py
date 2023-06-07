#!/usr/bin/python3
import urllib.request
import urllib.parse
import json
import os
import zipfile
import glob
from simple_term_menu import TerminalMenu
from tabulate import tabulate


os.system("clear")

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
    try:
        opener.retrieve(link, os.path.join(f'{save_dir}/{file_name.removesuffix(".zip")}', file_name))
        unzip_files(file_name, f'{save_dir}/{file_name.removesuffix(".zip")}')
        print(f"{Red}[+]{White} {file_name} Done {Green}[\u2713]{White}")
    except KeyboardInterrupt:
        exit(0)

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
    program_info = []
    headers = ["Info", f"{program_name}"]
    for program in data_json:
        if program['name'] == program_name:
            program_info.append([["name",program['name']],["program url", program['URL']],
                                ["total subdomains", program['count']], ["new subdomains", program['change']],
                                ["is new", program['is_new']], ["platform", program['platform']],
                                ["offer reward", program['bounty']], ['last_updated', program['last_updated'][:10]]])
            file_name = get_file_name(program["URL"])
            download(program["URL"], save_dir, file_name)
    print("\n")
    print(tabulate(program_info[0], headers, tablefmt="double_grid"))
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
        if (program["change"] != 0) and (program["bounty"] == False) and (program['platform'] == platform_name):
            if program['platform'] == "":
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
        if (program["bounty"] == False) and (program['platform'] == platform_name):
            if program['platform'] == "":
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
    print("\n")
    print_title = "Do you want to use httprobe or httpx?"
    print_options = ["httprobe", "httpx", "Back to Main Menu", "exit"]
    print_menu = TerminalMenu(print_options, title=print_title)
    index = print_menu.show()   
    if index == 0:
        httprobe_command(f"{first_dir}.txt")
    elif index == 1:
        httpx_command(f"{first_dir}.txt")
    elif index == 2:
        pass
    else:
        exit(0)

def info():
    last_update = data_json[0]['last_updated'][:10]
    total_subdomains = 0
    total_programs = 0
    programs_changed = 0
    new_programs = 0
    hackerone_programs = 0
    bugcrowd_programs = 0
    yeswehacker_programs = 0
    self_hosted_programs = 0
    programs_with_rewards = 0
    programs_with_swag = 0
    programs_with_no_rewards = 0

    for program in data_json:
        total_subdomains += program["count"]
        if program["platform"] == "hackerone":
            hackerone_programs += 1
        if program["platform"] == "bugcrowd":
            bugcrowd_programs += 1
        if program["platform"] == "yeswehack":
            yeswehacker_programs += 1
        if program["platform"] == "":
            self_hosted_programs += 1
        if program["change"] != 0:
            programs_changed +=1
        if program["is_new"] == True:
            new_programs += 1
        if program["bounty"] == True:
            programs_with_rewards +=1
        if program["bounty"] == False:
            programs_with_no_rewards +=1
        if 'swag' in program:
            programs_with_swag +=1

    info_options = [f"Programs last updated in {last_update}", f"{total_subdomains} Subdomain.",
                    f"{total_programs} Programs.", f"{programs_changed} Programs changes.",
                    f"{new_programs} New programs.", f"{hackerone_programs} Hackerone programs.",
                    f"{bugcrowd_programs} Bugcrowd programs.", f"{yeswehacker_programs} Yeswehack programs.",
                    f"{self_hosted_programs} Self hosted programs.",
                    f"{programs_with_rewards} Programs with rewards.",
                    f"{programs_with_swag} Programs offers swags.",
                    f"{programs_with_no_rewards} No rewards programs.",
                     "Back to Main Menu", "exit"]
    info_menu = TerminalMenu(info_options, title=main_menu_title + "  Info Menu.\n  Press Q or Esc to back to main menu. \n",
                             menu_cursor=main_menu_cursor,
                             menu_cursor_style=main_menu_cursor_style,
                             menu_highlight_style=main_menu_style)
    index = info_menu.show()
    if index == 13:
        print("Quit Selected")
        exit(0)


        

def httprobe_command(file_name):
    os.system(f"cat {file_name} | httprobe -c 1000 | tee -a live_domains_{file_name}_httprobe.txt")

def httpx_command(file_name):
    os.system(f"cat {file_name} | httpx -t 200 -rl 600 | tee -a live_domains_{file_name}_httpx.txt ")

main_menu_title = """
          _____ _                       _____                      _                 _           
         / ____| |                     |  __ \                    | |               | |          
        | |    | |__   __ _  ___  ___  | |  | | _____      ___ __ | | ___   __ _  __| | ___ _ __ 
        | |    | '_ \ / _` |/ _ \/ __| | |  | |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|
        | |____| | | | (_| | (_) \__ \ | |__| | (_) \ V  V /| | | | | (_) | (_| | (_| |  __/ |   
         \_____|_| |_|\__,_|\___/|___/ |_____/ \___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|\___|_|   

        This tools is designed to deal with chaos api from projectdiscovery.io
                    https://chaos.projectdiscovery.io/
"""
main_menu_items = ["all programmes", "offer bounty", "not offer bounty", "platform", "new subdomain",
            "new subdomain and offer bounty", "new subdomain and offer bounty and platform", "new subdomain and platform", 
            "new subdomain and not offer bounty", "new subdomain and not offer bounty and platform", 
            "offer bounty and platform", "not offer bounty and platform" ,"specific programs", "Info about programs","Quit"]
main_menu_cursor = "> "
main_menu_cursor_style = ("fg_red", "bold")
main_menu_style = ("bg_red", "fg_yellow")
main_menu_exit = False

main_menu = TerminalMenu(
    menu_entries= main_menu_items,
    title= main_menu_title + "  Main Menu.\n  Press Q or Esc to back to main menu. \n",
    menu_cursor=main_menu_cursor,
    menu_cursor_style=main_menu_cursor_style,
    menu_highlight_style=main_menu_style,
    cycle_cursor=True,
    clear_screen=False,
)

sub_menu_title = main_menu_title + "  Platform Menu.\n  Press Q or Esc to back to main menu. \n"
sub_menu_items = ["Hackerone", "Bugcrowd", "Yeswehack", "Self hosted", "Back to Main Menu"]
sub_menu_back = False
sub_menu = TerminalMenu(
    sub_menu_items,
    title= sub_menu_title,
    menu_cursor=main_menu_cursor,
    menu_cursor_style=main_menu_cursor_style,
    menu_highlight_style=main_menu_style,
    cycle_cursor=True,
    clear_screen=True,
)

while not main_menu_exit:
    main_sel = main_menu.show()

    if main_sel == 0:
        download_all_programmes()
    elif main_sel == 1:
        download_offer_bounty()
    elif main_sel == 2:
        download_not_offer_bounty()
    elif main_sel == 3:
        while not sub_menu_back:
            sub_sel = sub_menu.show()
            if sub_sel == 0:
                download_by_platform(sub_menu_items[sub_sel])
            elif sub_sel == 1:
                download_by_platform(sub_menu_items[sub_sel])
            elif sub_sel == 2:
                download_by_platform(sub_menu_items[sub_sel])
            elif sub_sel == 3:
                download_by_platform(sub_menu_items[sub_sel])
            elif sub_sel == 4 or sub_sel == None:
                sub_menu_back = True
        sub_menu_back = False
    elif main_sel == 4:
        download_new_subdomain()
    elif main_sel == 5:
        new_subdomains_and_offer_bounty()
    elif main_sel == 6:
        while not sub_menu_back:
            sub_sel = sub_menu.show()
            if sub_sel == 0 :
                new_subdomain_and_offer_bounty_and_platform(sub_menu_items[sub_sel])
            elif sub_sel == 1:
                new_subdomain_and_offer_bounty_and_platform(sub_menu_items[sub_sel])
            elif sub_sel == 2:
                new_subdomain_and_offer_bounty_and_platform(sub_menu_items[sub_sel])
            elif sub_sel == 3:
                new_subdomain_and_offer_bounty_and_platform("")
            elif sub_sel == 4 or sub_sel == None:
                sub_menu_back = True
        sub_menu_back = False
    elif main_sel == 7:
        while not sub_menu_back:
            sub_sel = sub_menu.show()
            if sub_sel == 0 :
                new_subdomain_and_platform(sub_menu_items[sub_sel])
            elif sub_sel == 1:
                new_subdomain_and_platform(sub_menu_items[sub_sel])
            elif sub_sel == 2:
                new_subdomain_and_platform(sub_menu_items[sub_sel])
            elif sub_sel == 3:
                new_subdomain_and_platform("")
            elif sub_sel == 4 or sub_sel == None:
                sub_menu_back = True
        sub_menu_back = False
    elif main_sel == 8:
        new_subdomain_and_not_offer_bounty()
    elif main_sel == 9:
        while not sub_menu_back:
            sub_sel = sub_menu.show()
            if sub_sel == 0 :
                new_subdomain_and_not_offer_bounty_and_platform(sub_menu_items[sub_sel])
            elif sub_sel == 1:
                new_subdomain_and_not_offer_bounty_and_platform(sub_menu_items[sub_sel])
            elif sub_sel == 2:
                new_subdomain_and_not_offer_bounty_and_platform(sub_menu_items[sub_sel])
            elif sub_sel == 3:
                new_subdomain_and_not_offer_bounty_and_platform("")
            elif sub_sel == 4 or sub_sel == None:
                sub_menu_back = True
        sub_menu_back = False
    elif main_sel == 10:
        while not sub_menu_back:
            sub_sel = sub_menu.show()
            if sub_sel == 0 :
                offer_bounty_and_platform(sub_menu_items[sub_sel])
            elif sub_sel == 1:
                offer_bounty_and_platform(sub_menu_items[sub_sel])
            elif sub_sel == 2:
                offer_bounty_and_platform(sub_menu_items[sub_sel])
            elif sub_sel == 3:
                offer_bounty_and_platform("")
            elif sub_sel == 4 or sub_sel == None:
                sub_menu_back = True
        sub_menu_back = False
    elif main_sel == 11:
        while not sub_menu_back:
            sub_sel = sub_menu.show()
            if sub_sel == 0 :
                not_offer_bounty_and_platform(sub_menu_items[sub_sel])
            elif sub_sel == 1:
                not_offer_bounty_and_platform(sub_menu_items[sub_sel])
            elif sub_sel == 2:
                not_offer_bounty_and_platform(sub_menu_items[sub_sel])
            elif sub_sel == 3:
                not_offer_bounty_and_platform("")
            elif sub_sel == 4 or sub_sel == None:
                sub_menu_back = True
        sub_menu_back = False
    elif main_sel == 12:
        programe_names = []
        for name in data_json:
            programe_names.append(name["name"])
        programe_title = main_menu_title + "  programs Menu.\n  Press Q or Esc to back to main menu. \n"
        programe_menu = TerminalMenu(programe_names, title=programe_title, show_search_hint=True, menu_cursor=main_menu_cursor, menu_cursor_style=main_menu_cursor_style, menu_highlight_style=main_menu_style)
        index = programe_menu.show()
        programe_name = programe_names[index]
        download_specific_program(programe_name)
    elif main_sel == 13:
        info()
    elif main_sel == 14 or main_sel == None:
        main_menu_exit = True
        print("Quit Selected")
