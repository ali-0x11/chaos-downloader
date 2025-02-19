#!/usr/bin/env python3
import os
import urllib.request
import urllib.parse
import json
import zipfile
import glob
import subprocess
import sqlite3
import threading
import concurrent.futures
from pathlib import Path
from simple_term_menu import TerminalMenu
from tabulate import tabulate

# Clear screen
os.system("clear")

##########################################
# Database setup with thread safety
##########################################
sqliteConnection = sqlite3.connect('chaos.db', check_same_thread=False)
cursor = sqliteConnection.cursor()
sqlite_lock = threading.Lock()

def setup_database():
    with sqlite_lock:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS names (ID INTEGER PRIMARY KEY, name TEXT UNIQUE, platform TEXT, offer_bounty BOOLEAN, late_update DATE);"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS subdomains (ID INTEGER PRIMARY KEY, subdomain TEXT UNIQUE, program_ID INTEGER, FOREIGN KEY(program_ID) REFERENCES names(ID));"
        )
        sqliteConnection.commit()

setup_database()

##########################################
# Colors for terminal output
##########################################
Red     = "\033[31m"
Green   = "\033[32m"
White   = "\033[97m"
Yellow  = "\033[33m"
Default = "\033[0m"

##########################################
# Load JSON data from chaos API
##########################################
def load_data():
    url = "https://chaos-data.projectdiscovery.io/index.json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    webpage = urllib.request.urlopen(req).read()
    return json.loads(webpage)

data_json = load_data()

# Set up an opener with a custom header (to avoid 403 errors)
opener = urllib.request.URLopener()
opener.addheader('User-Agent', 'Mozilla/5.0')

##########################################
# Helper functions for database operations
##########################################
def insert_table_name(program_name, platform, offer_bounty):
    with sqlite_lock:
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO names(name, platform, offer_bounty, late_update) VALUES(?, ?, ?, DATE('NOW'));",
                (program_name, platform, offer_bounty)
            )
            sqliteConnection.commit()
        except Exception as e:
            print("DB error:", e)

def insert_domains(program_name, subdomain):
    with sqlite_lock:
        try:
            cursor.execute("SELECT ID FROM names WHERE name=?", (program_name,))
            row = cursor.fetchone()
            if row:
                program_id = row[0]
                cursor.execute(
                    "INSERT OR IGNORE INTO subdomains(subdomain, program_ID) VALUES(?, ?)",
                    (subdomain, program_id)
                )
                sqliteConnection.commit()
        except sqlite3.IntegrityError:
            pass

##########################################
# File and download functions
##########################################
def get_file_name(download_link):
    return os.path.basename(download_link)

def unzip_files(file_path, save_dir):
    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            zf.extractall(save_dir)
        os.remove(file_path)
    except Exception as e:
        print(f"Error unzipping {file_path}: {e}")

def download(download_link, save_dir, file_name, program_name, platform, offer_bounty):
    # Ensure the program folder exists
    program_dir = Path(save_dir) / program_name
    program_dir.mkdir(parents=True, exist_ok=True)
    
    # Insert the program into the database (if not already present)
    insert_table_name(program_name, platform, offer_bounty)
    
    # Encode URL to avoid Unicode issues
    parsed = urllib.parse.urlsplit(download_link)
    encoded_path = urllib.parse.quote(parsed.path)
    download_link = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, encoded_path, parsed.query, parsed.fragment))
    
    file_path = program_dir / file_name
    try:
        opener.retrieve(download_link, str(file_path))
        unzip_files(str(file_path), str(program_dir))
        print(f"{Red}[+]{White} {file_name} Done {Green}[\u2713]{White}")
    except Exception as e:
        print(f"Error downloading {file_name}: {e}")

def merge_sub_files_and_insert(save_dir, program_name):
    program_dir = Path(save_dir) / program_name
    txt_files = list(program_dir.glob("*.txt"))
    all_subdomains = []

    # Merge all text files into one master file
    master_file = Path(f"{save_dir}.txt")
    with master_file.open("a", encoding="utf-8") as outfile:
        for file in txt_files:
            with file.open("r", encoding="utf-8") as infile:
                lines = infile.readlines()
                outfile.write("".join(lines))
                all_subdomains.extend([line.strip() for line in lines if line.strip()])
    
    # Batch insert into the database
    with sqlite_lock:
        cursor.execute("SELECT ID FROM names WHERE name=?", (program_name,))
        row = cursor.fetchone()
        if row:
            program_id = row[0]
            data_to_insert = [(sd, program_id) for sd in all_subdomains]
            cursor.executemany(
                "INSERT OR IGNORE INTO subdomains(subdomain, program_ID) VALUES(?, ?)",
                data_to_insert
            )
            sqliteConnection.commit()
    
    # Also write new subdomains to a separate file
    new_file_path = Path(f"new_{save_dir}.txt")
    with new_file_path.open("a", encoding="utf-8") as new_file:
        for sd in all_subdomains:
            new_file.write(sd + "\n")

def process_program(program, save_dir):
    file_name    = get_file_name(program["URL"])
    program_name = program["name"]
    platform     = program["platform"]
    bounty       = program["bounty"]
    download(program["URL"], save_dir, file_name, program_name, platform, bounty)
    merge_sub_files_and_insert(save_dir, program_name)

##########################################
# Generic download for filtered programs
##########################################
def download_filtered_programs(filter_func, save_dir):
    programs = [p for p in data_json if filter_func(p)]
    print(f"Starting download of {len(programs)} programs...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_program, prog, save_dir): prog for prog in programs}
        for future in concurrent.futures.as_completed(futures):
            prog = futures[future]
            try:
                future.result()
            except Exception as exc:
                print(f"{prog['name']} generated an exception: {exc}")
    ask(save_dir)

##########################################
# Filter lambdas for various selections
##########################################
def filter_all(p): 
    return True

def filter_offer_bounty(p): 
    return p["bounty"] == True

def filter_not_offer_bounty(p): 
    return p["bounty"] == False

def filter_by_platform(p, platform): 
    # For "self hosted", platform is empty string
    return p["platform"].lower() == platform.lower() if platform else p["platform"] == ""

def filter_new_subdomain(p): 
    return p["change"] != 0

def filter_new_and_offer(p): 
    return p["change"] != 0 and p["bounty"] == True

def filter_new_and_not_offer(p): 
    return p["change"] != 0 and p["bounty"] == False

##########################################
# Download functions for menu options
##########################################
def download_all_programmes():
    base_dir = "all_programmes"
    download_filtered_programs(filter_all, base_dir)

def download_offer_bounty():
    base_dir = "offer_bounty"
    download_filtered_programs(filter_offer_bounty, base_dir)

def download_not_offer_bounty():
    base_dir = "not_offer_bounty"
    download_filtered_programs(filter_not_offer_bounty, base_dir)

def download_by_platform(platform_name):
    base_dir = platform_name if platform_name else "self_hosted"
    download_filtered_programs(lambda p: filter_by_platform(p, platform_name), base_dir)

def download_new_subdomain():
    base_dir = "new_subdomains"
    download_filtered_programs(filter_new_subdomain, base_dir)

def new_subdomains_and_offer_bounty():
    base_dir = "new_subdomains_and_offer_bounty"
    download_filtered_programs(lambda p: filter_new_and_offer(p), base_dir)

def new_subdomain_and_offer_bounty_and_platform(platform_name):
    base_dir = f"new_subdomain_and_offer_bounty_and_{platform_name}" if platform_name else "new_subdomain_and_offer_bounty_and_self_hosted"
    download_filtered_programs(lambda p: filter_new_and_offer(p) and filter_by_platform(p, platform_name), base_dir)

def new_subdomain_and_platform(platform_name):
    base_dir = f"new_subdomain_and_platform_{platform_name}" if platform_name else "new_subdomain_and_platform_self_hosted"
    download_filtered_programs(lambda p: filter_new_subdomain(p) and filter_by_platform(p, platform_name), base_dir)

def new_subdomain_and_not_offer_bounty():
    base_dir = "new_subdomain_and_not_offer_bounty"
    download_filtered_programs(lambda p: filter_new_and_not_offer(p), base_dir)

def new_subdomain_and_not_offer_bounty_and_platform(platform_name):
    base_dir = f"new_subdomain_and_not_offer_bounty_and_{platform_name}" if platform_name else "new_subdomain_and_not_offer_bounty_and_self_hosted"
    download_filtered_programs(lambda p: filter_new_and_not_offer(p) and filter_by_platform(p, platform_name), base_dir)

def offer_bounty_and_platform(platform_name):
    base_dir = f"offer_bounty_and_{platform_name}" if platform_name else "offer_bounty_and_self_hosted"
    download_filtered_programs(lambda p: p["bounty"] == True and filter_by_platform(p, platform_name), base_dir)

def not_offer_bounty_and_platform(platform_name):
    base_dir = f"not_offer_bounty_and_{platform_name}" if platform_name else "not_offer_bounty_and_self_hosted"
    download_filtered_programs(lambda p: p["bounty"] == False and filter_by_platform(p, platform_name), base_dir)

def download_specific_program(program_name):
    base_dir = program_name
    programs = [p for p in data_json if p["name"] == program_name]
    if programs:
        p = programs[0]
        info_table = [
            ["name", p['name']],
            ["program url", p['URL']],
            ["total subdomains", p['count']],
            ["new subdomains", p['change']],
            ["is new", p['is_new']],
            ["platform", p['platform']],
            ["offer reward", p['bounty']],
            ["last_updated", p['last_updated'][:10]]
        ]
        print(tabulate(info_table, headers=["Info", program_name], tablefmt="double_grid"))
        download_filtered_programs(lambda p: p["name"] == program_name, base_dir)
    else:
        print("Program not found.")

##########################################
# Functions for external commands & export
##########################################
def httprobe_command(file_name):
    cmd = f'cat "new_{file_name}.txt" | httprobe -c 1000 | tee -a "live_domains_{file_name}_httprobe.txt"'
    with open(f"live_domains_{file_name}_httprobe.txt", "w", encoding="utf-8") as f:
        pass  # Truncate file first
    p1 = subprocess.Popen(cmd, shell=True, text=True, stdout=subprocess.PIPE, bufsize=1)
    for line in p1.stdout:
        print(line, end='')

def httpx_command(file_name):
    cmd = f'cat "new_{file_name}.txt" | httpx -t 200 -silent -nc -rl 600 | tee -a "live_domains_{file_name}_httpx.txt"'
    with open(f"live_domains_{file_name}_httpx.txt", "w", encoding="utf-8") as f:
        pass
    p1 = subprocess.Popen(cmd, shell=True, text=True, stdout=subprocess.PIPE, bufsize=1)
    for line in p1.stdout:
        print(line, end='')

def ask(first_dir):
    print("\n")
    options = ["httprobe", "httpx", "Back to Main Menu", "Exit"]
    menu = TerminalMenu(
        options,
        title="Do you want to use httprobe or httpx?",
        menu_cursor=main_menu_cursor,
        menu_cursor_style=main_menu_cursor_style,
        menu_highlight_style=main_menu_style
    )
    choice = menu.show()
    if choice == 0:
        httprobe_command(first_dir)
    elif choice == 1:
        httpx_command(first_dir)
    elif choice == 2:
        return
    else:
        exit(0)

def export_programme():
    try:
        programme_names = [p["name"] for p in data_json]
        export_menu = TerminalMenu(
            programme_names,
            title=main_menu_title + "  Export Menu.\n  Press Q or Esc to back to main menu. \n",
            show_search_hint=True,
            menu_cursor=main_menu_cursor,
            menu_cursor_style=main_menu_cursor_style,
            menu_highlight_style=main_menu_style,
            multi_select=True,
            show_multi_select_hint=True
        )
        _ = export_menu.show()
        for prog in export_menu.chosen_menu_entries:
            with sqlite_lock:
                cursor.execute("SELECT ID FROM names WHERE name=?", (prog,))
                row = cursor.fetchone()
                if row:
                    program_id = row[0]
                    cursor.execute("SELECT subdomain FROM subdomains WHERE program_ID=?", (program_id,))
                    subdomains = [r[0] for r in cursor.fetchall()]
            with open(f"{prog}_exported.txt", "w", encoding="utf-8") as file:
                for sd in subdomains:
                    file.write(sd + "\n")
    except Exception as e:
        print(e)

##########################################
# Main menu definitions and loop
##########################################
main_menu_title = """
          _____ _                       _____                      _                 _           
         / ____| |                     |  __ \\                    | |               | |          
        | |    | |__   __ _  ___  ___  | |  | | _____      ___ __ | | ___   __ _  __| | ___ _ __ 
        | |    | '_ \\ / _` |/ _ \\/ __| | |  | |/ _ \\ \\ /\\ / / '_ \\| |/ _ \\ / _` |/ _` |/ _ \\ '__|
        | |____| | | | (_| | (_) \\__ \\ | |__| | (_) \\ V  V /| | | | | (_) | (_| | (_| |  __/ |   
         \\_____|_| |_|\\__,_|\\___/|___/ |_____/ \\___/ \\_/\\_/ |_| |_|_|\\___/ \\__,_|\\__,_|\\___|_|   

        This tool is designed to deal with chaos API from projectdiscovery.io
                    https://chaos.projectdiscovery.io/
"""

main_menu_items = [
    "all programmes",
    "offer bounty",
    "not offer bounty",
    "platform",
    "new subdomain",
    "new subdomain and offer bounty",
    "new subdomain and offer bounty and platform",
    "new subdomain and platform", 
    "new subdomain and not offer bounty",
    "new subdomain and not offer bounty and platform", 
    "offer bounty and platform",
    "not offer bounty and platform",
    "specific programs",
    "Info about programs",
    "Export programme from database",
    "Quit"
]

main_menu_cursor = "> "
main_menu_cursor_style = ("fg_red", "bold")
main_menu_style = ("bg_red", "fg_yellow")

def main():
    main_menu = TerminalMenu(
        menu_entries=main_menu_items,
        title=main_menu_title + "  Main Menu.\n  Press Q or Esc to back to main menu. \n",
        menu_cursor=main_menu_cursor,
        menu_cursor_style=main_menu_cursor_style,
        menu_highlight_style=main_menu_style,
        cycle_cursor=True,
        clear_screen=False,
    )
    while True:
        choice = main_menu.show()
        if choice == 0:
            download_all_programmes()
        elif choice == 1:
            download_offer_bounty()
        elif choice == 2:
            download_not_offer_bounty()
        elif choice == 3:
            platform_options = ["Hackerone", "Bugcrowd", "Yeswehack", "Self hosted", "Back to Main Menu"]
            plat_menu = TerminalMenu(
                platform_options,
                title=main_menu_title + "  Platform Menu.\n  Press Q or Esc to back to main menu. \n",
                menu_cursor=main_menu_cursor,
                menu_cursor_style=main_menu_cursor_style,
                menu_highlight_style=main_menu_style,
                cycle_cursor=True,
                clear_screen=True,
            )
            p_choice = plat_menu.show()
            if p_choice in [0, 1, 2, 3]:
                plat = platform_options[p_choice]
                if plat.lower() == "self hosted":
                    plat = ""
                download_by_platform(plat)
        elif choice == 4:
            download_new_subdomain()
        elif choice == 5:
            new_subdomains_and_offer_bounty()
        elif choice == 6:
            platform_options = ["Hackerone", "Bugcrowd", "Yeswehack", "Self hosted", "Back to Main Menu"]
            plat_menu = TerminalMenu(
                platform_options,
                title=main_menu_title + "  Platform Menu.\n  Press Q or Esc to back to main menu. \n",
                menu_cursor=main_menu_cursor,
                menu_cursor_style=main_menu_cursor_style,
                menu_highlight_style=main_menu_style,
                cycle_cursor=True,
                clear_screen=True,
            )
            p_choice = plat_menu.show()
            if p_choice in [0, 1, 2, 3]:
                plat = platform_options[p_choice]
                if plat.lower() == "self hosted":
                    plat = ""
                new_subdomain_and_offer_bounty_and_platform(plat)
        elif choice == 7:
            platform_options = ["Hackerone", "Bugcrowd", "Yeswehack", "Self hosted", "Back to Main Menu"]
            plat_menu = TerminalMenu(
                platform_options,
                title=main_menu_title + "  Platform Menu.\n  Press Q or Esc to back to main menu. \n",
                menu_cursor=main_menu_cursor,
                menu_cursor_style=main_menu_cursor_style,
                menu_highlight_style=main_menu_style,
                cycle_cursor=True,
                clear_screen=True,
            )
            p_choice = plat_menu.show()
            if p_choice in [0, 1, 2, 3]:
                plat = platform_options[p_choice]
                if plat.lower() == "self hosted":
                    plat = ""
                new_subdomain_and_platform(plat)
        elif choice == 8:
            new_subdomain_and_not_offer_bounty()
        elif choice == 9:
            platform_options = ["Hackerone", "Bugcrowd", "Yeswehack", "Self hosted", "Back to Main Menu"]
            plat_menu = TerminalMenu(
                platform_options,
                title=main_menu_title + "  Platform Menu.\n  Press Q or Esc to back to main menu. \n",
                menu_cursor=main_menu_cursor,
                menu_cursor_style=main_menu_cursor_style,
                menu_highlight_style=main_menu_style,
                cycle_cursor=True,
                clear_screen=True,
            )
            p_choice = plat_menu.show()
            if p_choice in [0, 1, 2, 3]:
                plat = platform_options[p_choice]
                if plat.lower() == "self hosted":
                    plat = ""
                new_subdomain_and_not_offer_bounty_and_platform(plat)
        elif choice == 10:
            platform_options = ["Hackerone", "Bugcrowd", "Yeswehack", "Self hosted", "Back to Main Menu"]
            plat_menu = TerminalMenu(
                platform_options,
                title=main_menu_title + "  Platform Menu.\n  Press Q or Esc to back to main menu. \n",
                menu_cursor=main_menu_cursor,
                menu_cursor_style=main_menu_cursor_style,
                menu_highlight_style=main_menu_style,
                cycle_cursor=True,
                clear_screen=True,
            )
            p_choice = plat_menu.show()
            if p_choice in [0, 1, 2, 3]:
                plat = platform_options[p_choice]
                if plat.lower() == "self hosted":
                    plat = ""
                offer_bounty_and_platform(plat)
        elif choice == 11:
            platform_options = ["Hackerone", "Bugcrowd", "Yeswehack", "Self hosted", "Back to Main Menu"]
            plat_menu = TerminalMenu(
                platform_options,
                title=main_menu_title + "  Platform Menu.\n  Press Q or Esc to back to main menu. \n",
                menu_cursor=main_menu_cursor,
                menu_cursor_style=main_menu_cursor_style,
                menu_highlight_style=main_menu_style,
                cycle_cursor=True,
                clear_screen=True,
            )
            p_choice = plat_menu.show()
            if p_choice in [0, 1, 2, 3]:
                plat = platform_options[p_choice]
                if plat.lower() == "self hosted":
                    plat = ""
                not_offer_bounty_and_platform(plat)
        elif choice == 12:
            prog_options = [p["name"] for p in data_json]
            prog_menu = TerminalMenu(
                prog_options,
                title=main_menu_title + "  Programs Menu.\n  Press Q or Esc to back to main menu. \n",
                show_search_hint=True,
                menu_cursor=main_menu_cursor,
                menu_cursor_style=main_menu_cursor_style,
                menu_highlight_style=main_menu_style,
                multi_select=True,
                show_multi_select_hint=True
            )
            _ = prog_menu.show()
            for prog in prog_menu.chosen_menu_entries:
                download_specific_program(prog)
        elif choice == 13:
            # Info menu
            last_update = data_json[0]['last_updated'][:10]
            total_subdomains = sum(p["count"] for p in data_json)
            programs_changed = sum(1 for p in data_json if p["change"] != 0)
            new_programs = sum(1 for p in data_json if p["is_new"] == True)
            hackerone_programs = sum(1 for p in data_json if p["platform"].lower() == "hackerone")
            bugcrowd_programs = sum(1 for p in data_json if p["platform"].lower() == "bugcrowd")
            yeswehacker_programs = sum(1 for p in data_json if p["platform"].lower() == "yeswehack")
            self_hosted_programs = sum(1 for p in data_json if p["platform"] == "")
            programs_with_rewards = sum(1 for p in data_json if p["bounty"] == True)
            programs_with_no_rewards = sum(1 for p in data_json if p["bounty"] == False)
            programs_with_swag = sum(1 for p in data_json if 'swag' in p)

            info_options = [
                f"Programs last updated in {last_update}",
                f"{total_subdomains} Subdomains.",
                f"{len(data_json)} Programs.",
                f"{programs_changed} Programs changed.",
                f"{new_programs} New programs.",
                f"{hackerone_programs} Hackerone programs.",
                f"{bugcrowd_programs} Bugcrowd programs.",
                f"{yeswehacker_programs} Yeswehack programs.",
                f"{self_hosted_programs} Self hosted programs.",
                f"{programs_with_rewards} Programs with rewards.",
                f"{programs_with_swag} Programs offer swags.",
                f"{programs_with_no_rewards} No rewards programs.",
                "Back to Main Menu",
                "Exit"
            ]
            info_menu = TerminalMenu(
                info_options,
                title=main_menu_title + "  Info Menu.\n  Press Q or Esc to back to main menu. \n",
                menu_cursor=main_menu_cursor,
                menu_cursor_style=main_menu_cursor_style,
                menu_highlight_style=main_menu_style
            )
            i_choice = info_menu.show()
            if i_choice == len(info_options) - 1:
                exit(0)
        elif choice == 14:
            export_programme()
        elif choice == 15:
            print("Quit Selected")
            break

if __name__ == "__main__":
    os.system("clear")
    main()
