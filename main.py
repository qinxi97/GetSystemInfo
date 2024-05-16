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
import requests
import datetime
import time
import psutil

def get_system_uptime():
    # 获取系统启动时间
    boot_time = psutil.boot_time()

    # 计算当前时间与系统启动时间的差值
    uptime_seconds = int(time.time() - boot_time)

    # 将秒数转换为更友好的格式
    uptime = str(datetime.timedelta(seconds=uptime_seconds))

    print(f"System uptime: \033[32m {uptime} \033[0m")


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

def network_info():
    print("==================== NETWORK INFO =======================")
    ip_output = subprocess.check_output(["ip", "addr"]).decode().strip().split("\n")
    network_card = [line.split()[-1] for line in ip_output if
                    "inet" in line and "inet6" not in line and "127.0.0.1" not in line]
    IP = [line.split()[1].split("/")[0] for line in ip_output if
          "inet" in line and "inet6" not in line and "127.0.0.1" not in line]

    print(f"Network_device is \033[32m {network_card} \033[0m , Internal IP is  \033[32m {IP} \033[0m")

def get_External_ip():
    url = "https://api.ipify.org"
    response = requests.get(url)
    print(f"External IP is  \033[32m {response.text} \033[0m")
    print('\n')

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

def get_crontab():
    print("==================== RUNNING CRONTAB =======================")
    # 使用subprocess执行命令
    result = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
    r = result.stdout.strip()
    # 返回crontab的内容
    print("Crontab content:", r)

if __name__ == '__main__':
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
    time.sleep(0.4)

    get_External_ip()
    get_running_processes()

    get_crontab()







