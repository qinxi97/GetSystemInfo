#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: main.py
# Author: qinxi
# Email: 1023495336@qq.com
# Date: 2024/5/15
# Description: 获取服务器系统相关信息【操作系统、磁盘、CPU，内存、负载、网络IP、进程】
# Import Module :

import os
import platform
import re
import subprocess
import sys
import requests
import datetime
import time
import psutil

def print_banner():
    author = "Qinxi"
    email = "<1023495336@qq.com>"
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    banner = f"""
    \033[36m -------------------------------------------------------- \033[0m
    \033[31m     ██████╗  █████╗ ████████╗██╗  ██╗███████╗██████╗     \033[0m
    \033[31m    ██╔════╝ ██╔══██╗╚══██╔══╝██║  ██║██╔════╝██╔══██╗    \033[0m
    \033[31m    ██║  ███╗███████║   ██║   ███████║█████╗  ██████╔╝    \033[0m
    \033[31m    ██║   ██║██╔══██║   ██║   ██╔══██║██╔══╝  ██╔══██╗    \033[0m
    \033[31m    ╚██████╔╝██║  ██║   ██║   ██║  ██║███████╗██║  ██║    \033[0m
    \033[31m     ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    \033[0m
    \033[36m -------------------------------------------------------- \033[0m
    Author: {author}
    Email: {email}
    Current Time: {current_time}
    """
    print(banner)

def get_system_uptime():
    # 获取系统启动时间
    boot_time = psutil.boot_time()

    # 计算当前时间与系统启动时间的差值
    uptime_seconds = int(time.time() - boot_time)

    # 将秒数转换为更友好的格式
    uptime = str(datetime.timedelta(seconds=uptime_seconds))

    print(f"System uptime: \033[32m {uptime} \033[0m")

# 获取服务器可登录用户名
def get_users_with_shell():
    shell_path = "/bin/bash"
    try:
        # 使用subprocess执行命令
        result = subprocess.run(['/bin/egrep', shell_path, '/etc/passwd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)

        # 使用列表推导式获取用户名列表
        users = [line.split(':')[0] for line in result.stdout.splitlines()]
        return users
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return []

# 获取服务器系统信息（运行时间，系统版本）
def system_info():
    print("==================== SYSTEM INFO ========================")
    version = platform.release()
    kernel = platform.version()
    hostname = platform.node()

    try:
        with open('/etc/os-release', 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith('PRETTY_NAME='):
                    os_name = line.split('=')[1].strip().strip('""')
                    break
    except FileNotFoundError:
        print("\033[31m The system is not supported \033[0m")
        return
    print(f"System_version is \033[32m {os_name} \033[0m")
    print(f"System_kernel_version is  \033[32m {version} \033[0m")
    print(f"System_hostname is \033[32m {hostname} \033[0m")
    # 获取系统运行时间
    get_system_uptime()

    # 获取系统中可登录用户
    users = get_users_with_shell()
    print(f"System User as follows: ")
    for name in users:
        print(f"\033[32m {name} \033[0m")
    print('\n')

def disk_info():
    print("==================== DISK INFO ======================")
    df_output = subprocess.check_output(['df', '-ThP']).decode("utf-8").strip().split('\n')
    headers = df_output[0].split()
    data = [line.split() for line in df_output[1:]]
    formatted_data = [headers] + data
    max_lengths = [max(len(str(item)) for item in col) for col in zip(*formatted_data)]
    for row in formatted_data:
        print(" ".join(f"{item:<{max_length}}" for item, max_length in zip(row, max_lengths)))
    print('\n')

# 获取服务器CPU信息
def cpu_info():
    print("======================= CPU INFO ========================")

    # Count CPU processors
    processor_count = len(re.findall(r'^processor', subprocess.check_output(["grep", "^processor", "/proc/cpuinfo"]).decode().strip(), re.MULTILINE))
    print(f"Cpu processor is \033[32m {processor_count} \033[0m")

    # Get CPU mode name
    model_name = subprocess.check_output(["grep", "model name", "/proc/cpuinfo"]).decode().strip().split(":")[1].strip()
    print(f"Cpu mode name is \033[32m {model_name} \033[0m")

    # Get CPU MHz
    cpu_mhz = subprocess.check_output(["grep", "cpu MHz", "/proc/cpuinfo"]).decode().strip().split(":")[1].strip()
    print(f"Cpu MHz is \033[32m {cpu_mhz} \033[0m")

    # Get CPU cache size
    cache_size = subprocess.check_output(["grep", "cache size", "/proc/cpuinfo"]).decode().strip().split(":")[1].strip()
    print(f"Cpu cache size is \033[32m {cache_size} \033[0m")
    print('\n')

def mem_info():
    print("==================== MEMORY INFO ========================")
    with open('/proc/meminfo', 'r') as f:
        meminfo = f.readlines()

    # Extract memory information
    MemTotal = int(meminfo[0].split()[1])
    MemFree = int(meminfo[1].split()[1])
    Buffers = int(meminfo[2].split()[1])
    Cached = int(meminfo[3].split()[1])

    # Calculate memory usage
    TotalMem = MemTotal / 1024
    FreeMem = (MemFree + Buffers + Cached) / 1024
    UsedMem = TotalMem - FreeMem

    print(f"Total memory is \033[32m {TotalMem} MB \033[0m")
    print(f"Free  memory is \033[32m {FreeMem} MB \033[0m")
    print(f"Used  memory is \033[32m {UsedMem} MB \033[0m")
    print('\n')

# 获取服务器负载信息
def loadavg_info():
    print("================== LOAD AVERAGE INFO  ====================")
    with open('/proc/loadavg', 'r') as f:
        loadavg = f.readline().split()

    Load1 = loadavg[0]
    Load5 = loadavg[1]
    Load10 = loadavg[2]

    print(f"Loadavg in 1 min is \033[32m {Load1} \033[0m")
    print(f"Loadavg in 5 min is \033[32m {Load5} \033[0m")
    print(f"Loadavg in 10 min is \033[32m {Load10} \033[0m")
    print('\n')

# 获取服务器内网IP
def network_info():
    print("==================== NETWORK INFO =======================")
    ip_output = subprocess.check_output(["ip", "addr"]).decode().strip().split("\n")
    network_card = [line.split()[-1] for line in ip_output if
                    "inet" in line and "inet6" not in line and "127.0.0.1" not in line]
    IP = [line.split()[1].split("/")[0] for line in ip_output if
          "inet" in line and "inet6" not in line and "127.0.0.1" not in line]

    print(f"Network_device is \033[32m {network_card} \033[0m , Internal IP is  \033[32m {IP} \033[0m")

# 获取服务器外网IP
def get_External_ip():
    primary_url = "https://api.ipify.org"
    backup_url = "https://ipinfo.io/ip"

    try:
        response = requests.get(primary_url, timeout=8)
        response.raise_for_status()  # Check if the request was successful
        print(f"External IP is  \033[32m {response.text} \033[0m")
    except requests.RequestException as e:
        try:
            response = requests.get(backup_url, timeout=5)
            response.raise_for_status()  # Check if the request was successful
            #print(response.status_code)
            print(f"External IP is  \033[32m {response.text} \033[0m")
        except requests.RequestException as e:
            print(f"Failed to reach {backup_url} as well. Error: {e}")
    print('\n')

# 查询正在运行进程
def get_running_processes():
  all_process_count = 0

  print("==================== RUNNING PROCESSES =======================")
  # 获取所有进程
  for proc in psutil.process_iter(['pid', 'name', 'username']):
    try:
      # 获取进程详细信息
      process_info = proc.info

      pid = process_info['pid']
      process = psutil.Process(pid)

      # 获取进程CPU和内存使用情况
      cpu_percent = process.cpu_percent(interval=0.3)
      memory_info = process.memory_info()
      memory_mb = memory_info.rss / 1024 / 1024  # 转换为MB

      print(
        f"PID: {pid},  Name: {process_info['name']},  User: {process_info['username']},  CPU: {cpu_percent}%,  Memory: {memory_mb:.2f} MB")

      all_process_count += 1
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
      pass

  print(f"\nTotal Processes: {all_process_count}")
  print('\n')

# 查询定时任务
def get_crontab():
    print("==================== RUNNING CRONTAB =======================")
    # 使用subprocess执行命令
    result = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
    r = result.stdout.strip()
    # 返回crontab的内容
    print("Crontab content:", r)

# 查询开机启动服务
def get_startup_service():
    print("==================== STARTUP SERVICE =======================")
    services = subprocess.run(['systemctl', 'list-unit-files', '--type=service', '--state=enabled'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
    r = services.stdout.strip()
    print("Startup services:", r)

# 查询所有监听服务
def get_listening_socket():
    print("==================== LISTENING SOCKET =======================")
    services = subprocess.run(['netstat', '-lnupt'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
    r = services.stdout.strip()
    print("Startup services:", r)

# 查询所有TCP网络链接
def get_tcp_info():
    print("==================== TCP INFO =======================")
    services = subprocess.run(['netstat', '-ant'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
    r = services.stdout.strip()
    print("Startup services:", r)

# 查询路由信息
def get_routing_table():
    print("==================== ROUTING TABLE =======================")
    services = subprocess.run(['netstat', '-nr'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
    r = services.stdout.strip()
    print("Startup services:", r)

# 查询系统所有的内核参数信息
def get_kernel_parameter():
    print("==================== ALL KERNEL PARAMETER =======================")
    services = subprocess.run(['sysctl', '-a'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
    r = services.stdout.strip()
    print("Startup services:", r)
    print('\n')
    print("==================== Effective parameters =======================")
    services = subprocess.run(['egrep', '-v', '^#', '/etc/sysctl.conf'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
                              check=True)
    s = services.stdout.strip()
    print("Startup services:", s)


def usage():
    print("Usage: python3 main.py [-b] [-h] [-c] [-p] [-s] [-l] [-r] [-t] [-k]")
    print("Base Info: -b")
    print("Crontab Info: -c")
    print("Process Info: -p")
    print("TCP Info: -t")
    print("Startup Service Info: -s")
    print("Listening Socket Info: -l")
    print("Routing Table Info: -r")
    print("Kernel Parameter Info: -k")
    print("Help: -h")

if __name__ == '__main__':
    print_banner()
    if len(sys.argv) != 2:
        print(f"\033[36m Please pass in an argument. \033[0m")
        usage()
        sys.exit(1)

    value = sys.argv[1]
    def select_info(value):
        if value.lower() == '-b':
            system_info()
            time.sleep(0.4)

            disk_info()
            time.sleep(0.4)

            cpu_info()
            time.sleep(0.4)

            mem_info()
            time.sleep(0.4)

            loadavg_info()
            time.sleep(0.4)

            network_info()
            get_External_ip()

        elif value.lower() == '-p':
            time.sleep(0.4)
            get_running_processes()

        elif value.lower() == '-c':
            get_crontab()

        elif value.lower() == '-l':
            get_listening_socket()

        elif value.lower() == '-t':
            get_tcp_info()

        elif value.lower() == '-r':
            get_routing_table()

        elif value.lower() == '-k':
            get_kernel_parameter()

        elif value.lower() == '-s':
            time.sleep(0.4)
            get_startup_service()

        else:
            usage()

    select_info(value)

