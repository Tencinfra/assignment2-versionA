#!/usr/bin/env python3

'''
OPS445 Assignment 2
Program: assignment2.py 
Author: Chograb Tenzin
Semester: Fall 2024

The python code in this file is original work written by
Chograb Tenzin. No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or online resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: Memory visualization program to monitor system memory usage and specific program memory usage.
'''

import argparse
import os

def parse_command_args() -> object:
    "Set up argparse here. Call this function inside main."
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts", epilog="Copyright 2023")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    # added argument for "human-readable".
    parser.add_argument("-H", "--human-readable", action="store_true", help="Display memory sizes in human-readable format.")
    parser.add_argument("program", type=str, nargs='?', help="if a program is specified, show memory use of all associated processes. Show only total use if not.")
    args = parser.parse_args()
    return args
# converts percentages from 0.0 to 1.0 to graph and rejects those that are not
def percent_to_graph(percent: float, length: int=20) -> str:
    "turns a percent 0.0 - 1.0 into a bar graph"
    # if the value is NOT between the suggested range, it is rejected and they are notfied
    if not (0.0 <= percent <= 1.0):
        raise ValueError("not between 0.0 and 1.0")
    # calculates number of bars filled then returns it as a string
    num_filled = int(percent * length)
    return '#' * num_filled + ' ' * (length - num_filled)

def get_sys_mem() -> int:
    "return total system memory (used or available) in kB"
    #opens the proc/meminfo file
    with open("/proc/meminfo", "r") as mem_file:
        #reads each line in a loop the file to find specifically memtotal and extracts it    
        for line in mem_file:
            if 'MemTotal' in line:
                sys_total_mem = int(line.split()[1])
                # returns as sys_total_mem once  extracted
                return sys_total_mem

def get_avail_mem() -> int:
    "return total memory that is available"
    #opens the meminfo file 
    with open("/proc/meminfo", "r") as mem_file:
        #reads each line in a loop the file to find specifically nemavaialable and extracts it    
        for line in mem_file:    
            if 'MemAvailable' in line:
                available_mem = int(line.split()[1])
                # returns the value as available_mem once extracted
                return available_mem

def pids_of_prog(app_name: str) -> list:
    "given an app name, return all pids associated with app"
    #gets pid for app based off the app name
    pids = os.popen("pidof " + app_name).read().strip()
    # some apps have mutliple ids so this returns them into a list
    if pids:
        pids_list = pids.split()
    # if there are none, it will return as an empty list
    else:
        pids_list =[]
    return pids_list

def rss_mem_of_pid(proc_id: str) -> int:
    "given a process id, return the resident memory used, zero if not found"
    try:
        # opens smaps file where memory info is located
        with open(f'/proc/{proc_id}/smaps') as smaps:
            # loop to look through every line in smaps to find line that starts with vmsrr which contains resident memory information
            for line in smaps:
                if line.startswith("VmRSS"):
                    # returns the value, specifically as an integer
                    return int(line.split()[1])
    # if you receive a file not found error, it will return 0 
    except FileNotFoundError:
        return 0
    # returns zero if nothing is found
    return 0 

def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    "turn 1,024 into 1 MiB, for example"
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']  # iB indicates 1024
    suf_count = 0
    result = kibibytes
    while result > 1024 and suf_count < len(suffixes):
        result /= 1024
        suf_count += 1
    str_result = f'{result:.{decimal_places}f} '
    str_result += suffixes[suf_count]
    return str_result

if __name__ == "__main__":
    args = parse_command_args()

    total_mem = get_sys_mem()
    avail_mem = get_avail_mem()
    if not args.program:
        # No program specified, just show total system memory stats
        used_mem = total_mem - avail_mem # calcualting used mem by subtracting total from available
        mem_dec_used = used_mem / total_mem #calcualting decimal form memory used by dividing used mem and total
        mem_perc_used = (used_mem / total_mem)*100 # calcualting percentage by diving to get decimal the mulitpling by 100
        graph = percent_to_graph(mem_dec_used, args.length) #creating bar graph with values provided
        # providing the information in human readable and raw format
        if args.human_readable:
            # converting all menu info into huma nreadable
            total_mem_readable = bytes_to_human_r(total_mem) 
            used_mem_readable = bytes_to_human_r(used_mem)
            avail_mem_readable = bytes_to_human_r(avail_mem)
            #making information much more human readable with easier information
            print(f"Memory: [{graph} | {mem_perc_used:.0f}%] {used_mem_readable}/{total_mem_readable}")
        else:
            #raw format of memeory usage
            print(f"Memory: [{graph} | {mem_perc_used:.0f}%] {used_mem}/{total_mem}")

    else:
        # Program specified, check memory used by its processes
        pid_list = pids_of_prog(args.program)
        if not pid_list:
            # if ap rogram is not found they will receive the below error message
            print(f"ERROR: {args.program} not found.")
        else: 
            total_rss = 0
            for pid in pid_list:
                rss_mem = rss_mem_of_pid(pid) # get rss memory of application searched
                total_rss += rss_mem # adding to get total memory information
                mem_dec_used = (rss_mem / total_mem) # decimal form of used memory by dividing rss memory used by total
                mem_perc_used = (rss_mem / total_mem) * 100  # Calculating memory usage relative to total system memory and multiplying by 100 to get percentage
                graph = percent_to_graph(mem_dec_used, args.length) # creating the mem usage ggraph
                
                if args.human_readable:
                    #covnerrts to readable format
                    rss_mem_readable = bytes_to_human_r(rss_mem)
                    total_mem_readable = bytes_to_human_r(total_mem)
                    #print in readable format with graph bar and peprcentage
                    print(f"{pid} [{graph}] | {mem_perc_used:.0f}%] {rss_mem_readable}/{total_mem_readable}")
                else:
                    #print process in raw form
                    print(f"{pid} [{graph}] | {mem_perc_used:.0f}%] {rss_mem}/{total_mem}")

            # Calculate total memory used by all program's processes
            total_mem_dec_used = total_rss / total_mem # decima value of total mem used
            # create graph for total memory used
            graph = percent_to_graph(total_mem_dec_used, args.length) 
            #humaanr edable output with graph and percentage
            if args.human_readable: 
                total_rss_readable = bytes_to_human_r(total_rss)
                total_mem_readable = bytes_to_human_r(total_mem)
                print(f"{args.program} [{graph} | {total_mem_dec_used * 100:.0f}%] {total_rss_readable}/{total_mem_readable}")
            else:
                #show values in raw form if -h(human readable) isnt selected
                print(f"{args.program} [{graph} | {total_mem_dec_used * 100:.0f}%] {total_rss}/{total_mem}")
