#!/usr/bin/python3
import urllib.request
import urllib.parse
import json
import os
import zipfile
import glob
from simple_term_menu import TerminalMenu
from tabulate import tabulate
import subprocess
import sqlite3
from progress.bar import Bar


os.system("clear")


# Databse connection
sqliteConnection = sqlite3.connect('chaos.db')
cursor = sqliteConnection.cursor()

# Create Tables
sql = "CREATE TABLE IF NOT EXISTS names (ID INTEGER PRIMARY KEY, name TEXT UNIQUE, platform TEXT, offer_bounty BOOLEAN, late_update DATE);"
cursor.execute(sql)
sqliteConnection.commit()

sql5 = "CREATE TABLE IF NOT EXISTS subdomains (ID INTEGER PRIMARY KEY, subdomain TEXT UNIQUE, program_ID INTEGER, FOREIGN KEY(program_ID) REFERENCES names(ID));"
cursor.execute(sql5)
sqliteConnection.commit()


# Colors
Red          = "\033[31m"
Green        = "\033[32m"
White        = "\033[97m"
Yellow       = "\033[33m"
Default      = '\033[0m'


# Load the main json page
url = "https://chaos-data.projectdiscovery.io/index.json"
request_site = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
webpage = urllib.request.urlopen(request_site).read()
data_json = json.loads(webpage)

# To solve error 403 while downloading
opener = urllib.request.URLopener()
opener.addheader('User-Agent', 'Mozilla/5.0')


def insert_table_name(programe_name, platform, offer_bounty):
    try:
        sql = f"INSERT INTO names(name, platform, offer_bounty, late_update) VALUES('{programe_name}', '{platform}', '{offer_bounty}',  DATE('NOW'));"
        cursor.execute(sql)
        sqliteConnection.commit()
    except Exception as e:
        pass


def insert_domains(programe_name, subdomain):
    try:
        sql = f"SELECT ID FROM names WHERE name='{programe_name}'"
        cursor.execute(sql)
        programm_id = cursor.fetchone()[0]
        sql1 = f"SELECT subdomain FROM subdomains WHERE program_ID='{programm_id}'"
        cursor.executemany('INSERT INTO subdomains(subdomain, program_ID) values (?, ?)', [(subdomain, programm_id)])
        sqliteConnection.commit()
        return subdomain
    except sqlite3.IntegrityError as e:
        pass

def insert_values_httprobe(programe_name, live_subdomains_httprobe):
    try:
        sql = f"SELECT ID FROM names WHERE name='{programe_name}'"
        cursor.execute(sql)
        programm_id = cursor.fetchone()[0]
        sql1 = f'INSERT INTO httprobe (live_subdomains, program_ID) VALUES (?, ?);'
        cursor.executemany(sql1, [(live_subdomains_httprobe, programm_id)])
        sqliteConnection.commit()
    except Exception as e:
        print(e)


def get_file_name(download_link):
    return os.path.basename(download_link)


# Main function for download
def download(link, save_dir, file_name, programe_name, platform, offer_bounty):
    if not os.path.exists(f'{save_dir}/{programe_name}'):
        os.makedirs(f'{save_dir}/{programe_name}')

    # insert Programmes names
    insert_table_name(programe_name, platform, offer_bounty)

    # To solve UnicodeError
    link = urllib.parse.urlsplit(link)
    link = list(link)
    link[2] = urllib.parse.quote(link[2])
    link = urllib.parse.urlunsplit(link)
    try:
        opener.retrieve(link, os.path.join(f'{save_dir}/{programe_name}', file_name))
        unzip_files(file_name, f'{save_dir}/{programe_name}')
        print(f"{Red}[+]{White} {file_name} Done {Green}[\u2713]{White}")
    except KeyboardInterrupt:
        exit(0)

def download_all_programmes():
    save_dir = "all_programmes"
    banner =  Yellow + "warning:" + Default + " this option will take a long time to finish " + Red + "[!]" + Default
    print(banner)
    input("Press enter to continue or CTRL+c to exit")
    remove_all = open("all_programmes.txt", "w")
    remove_all.close()
    for link in data_json:
        download_link = link["URL"]
        programe_name = link["name"]
        platform = link["platform"]
        offer_bounty = link["bounty"]
        file_name = get_file_name(download_link)
        download(download_link, save_dir, file_name, programe_name, platform, offer_bounty)
        merg_sub_files_insert(save_dir, programe_name)
    ask(save_dir)

def download_offer_bounty():
    save_dir = "offer_bounty"
    for data in data_json:
        if data["bounty"] == True:
            file_name = get_file_name(data["URL"])
            programe_name = data["name"]
            download_link = data["URL"]
            platform = data["platform"]
            offer_bounty = data["bounty"]
            download(download_link, save_dir, file_name, programe_name, platform, offer_bounty)
            merg_sub_files_insert(save_dir, programe_name)
    ask(save_dir)

def download_not_offer_bounty():
    save_dir = "not_offer_bounty"
    for data in data_json:
        if data["bounty"] == False:
            file_name = get_file_name(data["URL"])
            programe_name = data["name"]
            download_link = data["URL"]
            platform = data["platform"]
            offer_bounty = data["bounty"]
            download(download_link, save_dir, file_name, programe_name, platform, offer_bounty)
            merg_sub_files_insert(save_dir, programe_name)
    ask(save_dir)

def download_by_platform(platform_name):
    save_dir = f"{platform_name}"
    for data in data_json:
        if data['platform'] == platform_name:
            if data['platform'] == "":
                save_dir = "self hosted"
            file_name = get_file_name(data["URL"])
            programe_name = data["name"]
            download_link = data["URL"]
            platform = data["platform"]
            offer_bounty = data["bounty"]
            download(download_link, save_dir, file_name, programe_name, platform, offer_bounty)
            merg_sub_files_insert(save_dir, programe_name)
    ask(save_dir)

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
            programe_name = program["name"]
            download_link = program["URL"]
            platform = program["platform"]
            offer_bounty = program["bounty"]
            download(download_link, save_dir, file_name, programe_name, platform, offer_bounty)
            merg_sub_files_insert(save_dir, programe_name)
    print("\n")
    print(tabulate(program_info[0], headers, tablefmt="double_grid"))
    ask(save_dir)

def download_new_subdomain():
    save_dir = "new_subdomains"
    for program in data_json:
        if program["change"] != 0:
            file_name = get_file_name(program["URL"])
            programe_name = program["name"]
            download_link = program["URL"]
            platform = program["platform"]
            offer_bounty = program["bounty"]
            download(download_link, save_dir, file_name, programe_name, platform, offer_bounty)
            merg_sub_files_insert(save_dir, programe_name)
    ask(save_dir)

def new_subdomains_and_offer_bounty():
    save_dir = "new_subdomains_and_offer_bounty"
    for data in data_json:
        if (data["bounty"] == True) and (data["change"] != 0):
            file_name = get_file_name(data["URL"])
            programe_name = data["name"]
            download_link = data["URL"]
            platform = data["platform"]
            offer_bounty = data["bounty"]
            download(download_link, save_dir, file_name, programe_name, platform, offer_bounty)
            merg_sub_files_insert(save_dir, programe_name)
    ask(save_dir)

def new_subdomain_and_offer_bounty_and_platform(platform_name):
    save_dir = f"new_subdomain_and_offer_bounty_and_{platform_name}"
    for data in data_json:
        if (data["bounty"] == True) and (data["change"] != 0) and (data['platform'] == platform_name):
            if data['platform'] == "":
                save_dir = "new_subdomain_and_offer_bounty_and_self_hosted"
            file_name = get_file_name(data["URL"])
            programe_name = data["name"]
            download_link = data["URL"]
            platform = data["platform"]
            offer_bounty = data["bounty"]
            download(download_link, save_dir, file_name, programe_name, platform, offer_bounty)
            merg_sub_files_insert(save_dir, programe_name)
    ask(save_dir)

def new_subdomain_and_platform(platform_name):
    save_dir = f"new_subdomain_and_offer_bounty_and_{platform_name}"
    for data in data_json:
        if (data["change"] != 0) and (data['platform'] == platform_name):
            if data['platform'] == "":
                save_dir = "new_subdomain_and_offer_bounty_and_self_hosted"
            file_name = get_file_name(data["URL"])
            programe_name = data["name"]
            download_link = data["URL"]
            platform = data["platform"]
            offer_bounty = data["bounty"]
            download(download_link, save_dir, file_name, programe_name, platform, offer_bounty)
            merg_sub_files_insert(save_dir, programe_name)
    ask(save_dir)

def new_subdomain_and_not_offer_bounty():
    save_dir = "new_subdomain_and_not_offer_bounty"
    for program in data_json:
        if (program["change"] != 0) and (program["bounty"] == False):
            file_name = get_file_name(program["URL"])
            programe_name = program["name"]
            download_link = program["URL"]
            platform = program["platform"]
            offer_bounty = program["bounty"]
            download(download_link, save_dir, file_name, programe_name, platform, offer_bounty)
            merg_sub_files_insert(save_dir, programe_name)
    ask(save_dir)

def new_subdomain_and_not_offer_bounty_and_platform(platform_name):
    save_dir = f"./new_subdomain_and_not_offer_bounty_and_{platform_name}"
    for program in data_json:
        if (program["change"] != 0) and (program["bounty"] == False) and (program['platform'] == platform_name):
            if program['platform'] == "":
                save_dir = "new_subdomain_and_not_offer_bounty_and_self_hosted"
            file_name = get_file_name(program["URL"])
            programe_name = program["name"]
            download_link = program["URL"]
            platform = program["platform"]
            offer_bounty = program["bounty"]
            download(download_link, save_dir, file_name, programe_name, platform, offer_bounty)
            merg_sub_files_insert(save_dir, programe_name)
    ask(save_dir)

def offer_bounty_and_platform(platform_name):
    save_dir = f"./offer_bounty_and_{platform_name}"
    for program in data_json:
        if (program["bounty"] == True) and (program['platform'] == platform_name):
            if program['platform'] == "":
                save_dir = "offer_bounty_and_self_hosted"
            file_name = get_file_name(program["URL"])
            programe_name = program["name"]
            download_link = program["URL"]
            platform = program["platform"]
            offer_bounty = program["bounty"]
            download(download_link, save_dir, file_name, programe_name, platform, offer_bounty)
            merg_sub_files_insert(save_dir, programe_name)
    ask(save_dir)

def not_offer_bounty_and_platform(platform_name):
    save_dir = f"./not_offer_bounty_and{platform_name}"
    for program in data_json:
        if (program["bounty"] == False) and (program['platform'] == platform_name):
            if program['platform'] == "":
                save_dir = "not_offer_bounty_and_self_hosted"
            file_name = get_file_name(program["URL"])
            programe_name = program["name"]
            download_link = program["URL"]
            platform = program["platform"]
            offer_bounty = program["bounty"]
            download(download_link, save_dir, file_name, programe_name, platform, offer_bounty)
            merg_sub_files_insert(save_dir, programe_name)
    ask(save_dir)

def unzip_files(file_name, save_dir):
    with zipfile.ZipFile(f'{save_dir}/{file_name}', 'r') as zip:
        zip.extractall(save_dir)
    os.remove(f"{save_dir}/{file_name}")


def ask(first_dir):
    print("\n")
    print_title = "Do you want to use httprobe or httpx?"
    print_options = ["httprobe", "httpx", "Back to Main Menu", "exit"]
    print_menu = TerminalMenu(print_options, title=print_title,
                            menu_cursor=main_menu_cursor,
                            menu_cursor_style=main_menu_cursor_style,
                            menu_highlight_style=main_menu_style)
    index = print_menu.show()   
    if index == 0:
        httprobe_command(f"{first_dir}")
    elif index == 1:
        httpx_command(f"{first_dir}")
    elif index == 2:
        pass
    else:
        exit(0)

def merg_sub_files_insert(first_dir, program_name):        
    read_files = glob.glob(f"{first_dir}/{program_name}/*.txt")
    new_subdomains = [] 
    with open(f"{first_dir}.txt", "a+") as outfile:
        for f in read_files:
            with open(f, "r") as infile:
                outfile.write(infile.read())
                infile.seek(0)
                lines = infile.readlines()
                total = len(lines)
                with Bar('Migrating Subdomains to the database...',max = total) as bar:
                    for line in lines:
                        s = insert_domains(program_name, line)
                        new_subdomains.append(s)
                        bar.next()
        print()
    try:
        with open(f"new_{str(first_dir)}.txt", "a+") as new_file:
            for subdomain in new_subdomains:
                if subdomain == None:
                    pass
                else:
                    new_file.write(subdomain)
    except:
        pass

def info():
    last_update = data_json[0]['last_updated'][:10]
    total_subdomains = 0
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
                    f"{ hackerone_programs + bugcrowd_programs + yeswehacker_programs + self_hosted_programs } Programs.", f"{programs_changed} Programs changes.",
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
    cmd = f'cat "new_{file_name}.txt" | httprobe -c 1000 | tee -a "live_domains_{file_name}_httprobe.txt"'
    file = open(f"live_domains_{file_name}_httprobe.txt", "a+", encoding="utf-8")
    file.truncate(0)
    p1 = subprocess.Popen(cmd, shell=True, text=True, stdout=subprocess.PIPE, bufsize=1)
    for line in p1.stdout:
        print(line)

def httpx_command(file_name):
    cmd = f'cat "new_{file_name}.txt" | httpx -t 200 -silent -nc -rl 600 | tee -a "live_domains_{file_name}_httpx.txt"'
    file = open(f"live_domains_{file_name}_httpx.txt", "w+", encoding="utf-8")
    file.truncate(0)
    p1 = subprocess.Popen(cmd, shell=True, text=True, stdout=subprocess.PIPE, bufsize=1)
    for line in p1.stdout:
        print(line)

def export_programme():
    try:
        programe_names = [programme_name["name"] for programme_name in data_json]
        programe_title_e = main_menu_title + "  Export Menu.\n  Press Q or Esc to back to main menu. \n"
        programe_menu = TerminalMenu(programe_names, title=programe_title_e, show_search_hint=True, menu_cursor=main_menu_cursor, menu_cursor_style=main_menu_cursor_style, menu_highlight_style=main_menu_style)
        index = programe_menu.show()
        programe_name = programe_names[index]
        sql = f"SELECT ID FROM names WHERE name='{programe_name}'"
        cursor.execute(sql)
        programm_id = cursor.fetchone()[0]
        sql2 = f"SELECT subdomain FROM subdomains WHERE program_ID={programm_id}"
        cursor.execute(sql2)
        subdomains = [subdomain[0] for subdomain in cursor.fetchall()]
        file = open(f"{programe_name}_exported.txt", "w+", encoding="utf-8")
        total = len(subdomains)
        with Bar('Exporting subdomains from database...',max = total) as bar:
            for subdomain in subdomains:
                file.write(subdomain)
                bar.next()
        file.close()
    except Exception:
        pass

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
main_menu_items = ["all programes", "offer bounty", "not offer bounty", "platform", "new subdomain",
            "new subdomain and offer bounty", "new subdomain and offer bounty and platform", "new subdomain and platform", 
            "new subdomain and not offer bounty", "new subdomain and not offer bounty and platform", 
            "offer bounty and platform", "not offer bounty and platform" ,"specific programs", "Info about programs","Export programme from database","Quit"]
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
                download_by_platform(sub_menu_items[sub_sel].lower())
            elif sub_sel == 1:
                download_by_platform(sub_menu_items[sub_sel].lower())
            elif sub_sel == 2:
                download_by_platform(sub_menu_items[sub_sel].lower())
            elif sub_sel == 3:
                download_by_platform("")
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
                new_subdomain_and_offer_bounty_and_platform(sub_menu_items[sub_sel].lower())
            elif sub_sel == 1:
                new_subdomain_and_offer_bounty_and_platform(sub_menu_items[sub_sel].lower())
            elif sub_sel == 2:
                new_subdomain_and_offer_bounty_and_platform(sub_menu_items[sub_sel].lower())
            elif sub_sel == 3:
                new_subdomain_and_offer_bounty_and_platform("")
            elif sub_sel == 4 or sub_sel == None:
                sub_menu_back = True
        sub_menu_back = False
    elif main_sel == 7:
        while not sub_menu_back:
            sub_sel = sub_menu.show()
            if sub_sel == 0 :
                new_subdomain_and_platform(sub_menu_items[sub_sel].lower())
            elif sub_sel == 1:
                new_subdomain_and_platform(sub_menu_items[sub_sel].lower())
            elif sub_sel == 2:
                new_subdomain_and_platform(sub_menu_items[sub_sel].lower())
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
                new_subdomain_and_not_offer_bounty_and_platform(sub_menu_items[sub_sel].lower())
            elif sub_sel == 1:
                new_subdomain_and_not_offer_bounty_and_platform(sub_menu_items[sub_sel].lower())
            elif sub_sel == 2:
                new_subdomain_and_not_offer_bounty_and_platform(sub_menu_items[sub_sel].lower())
            elif sub_sel == 3:
                new_subdomain_and_not_offer_bounty_and_platform("")
            elif sub_sel == 4 or sub_sel == None:
                sub_menu_back = True
        sub_menu_back = False
    elif main_sel == 10:
        while not sub_menu_back:
            sub_sel = sub_menu.show()
            if sub_sel == 0 :
                offer_bounty_and_platform(sub_menu_items[sub_sel].lower())
            elif sub_sel == 1:
                offer_bounty_and_platform(sub_menu_items[sub_sel].lower())
            elif sub_sel == 2:
                offer_bounty_and_platform(sub_menu_items[sub_sel].lower())
            elif sub_sel == 3:
                offer_bounty_and_platform("")
            elif sub_sel == 4 or sub_sel == None:
                sub_menu_back = True
        sub_menu_back = False
    elif main_sel == 11:
        while not sub_menu_back:
            sub_sel = sub_menu.show()
            if sub_sel == 0 :
                not_offer_bounty_and_platform(sub_menu_items[sub_sel].lower())
            elif sub_sel == 1:
                not_offer_bounty_and_platform(sub_menu_items[sub_sel].lower())
            elif sub_sel == 2:
                not_offer_bounty_and_platform(sub_menu_items[sub_sel].lower())
            elif sub_sel == 3:
                not_offer_bounty_and_platform("")
            elif sub_sel == 4 or sub_sel == None:
                sub_menu_back = True
        sub_menu_back = False
    elif main_sel == 12:
        programe_names = [programme_name["name"] for programme_name in data_json]
        programe_title = main_menu_title + "  programs Menu.\n  Press Q or Esc to back to main menu. \n"
        programe_menu = TerminalMenu(programe_names, title=programe_title, show_search_hint=True, menu_cursor=main_menu_cursor, menu_cursor_style=main_menu_cursor_style, menu_highlight_style=main_menu_style)
        index = programe_menu.show()
        programe_name = programe_names[index]
        download_specific_program(programe_name)
    elif main_sel == 13:
        info()
    elif main_sel == 14:
        export_programme()
    elif main_sel == 15 or main_sel == None:
        main_menu_exit = True
        print("Quit Selected")
