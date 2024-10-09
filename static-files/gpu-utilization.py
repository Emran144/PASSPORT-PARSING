import GPUtil
from time import sleep

count = 1
while True:
    gpus = GPUtil.getGPUs()
    for gpu in gpus:
        print(f"\t{count}\tGPU {gpu.id} - Utilization: {gpu.load * 100}% - Memory Used: {gpu.memoryUsed}MB")
    sleep(0.1)  # Poll every second
    count += 1

# --------------------------------------------------------------------------------------------------------------
# import GPUtil
# import os
# from time import sleep

# # Get the current process ID (PID) of your project
# project_pid = '3240969'

# count = 1
# while True:
#     gpus = GPUtil.getGPUs()
#     for gpu in gpus:
#         # Get the list of processes running on the GPU
#         for proc in gpu.processes:
#             # Check if the process PID matches the current project
#             if proc['pid'] == project_pid:
#                 print(f"{count}\tGPU {gpu.id} - Utilization: {gpu.load * 100}% - Memory Used: {gpu.memoryUsed}MB - PID: {proc['pid']} - Process Memory: {proc['gpu_memory_usage']}MB")
#     sleep(0.1)
#     count += 1
# --------------------------------------------------------------------------------------------------------------

# import subprocess
# import os
# from time import sleep

# def get_gpu_utilization_by_pid(pid):
#     # Query nvidia-smi for pid and memory usage
#     result = subprocess.run(['nvidia-smi', '--query-compute-apps=pid,used_memory', '--format=csv,noheader,nounits'],
#                             stdout=subprocess.PIPE, encoding='utf-8')
#     processes = result.stdout.strip().split('\n')
    
#     for process in processes:
#         print(process)
#         process_info = process.split(',')
        
#         # Check if the process_info is valid and skip invalid entries
#         if len(process_info) < 2:
#             continue
        
#         try:
#             process_pid = int(process_info[0].strip())
#         except ValueError:
#             # Skip lines that don't contain a valid PID
#             continue
        
#         # If the PID matches your project PID
#         if process_pid == pid:
#             memory_used = process_info[1].strip()
#             print(f"PID: {pid}, GPU Memory Used: {memory_used} MB")

# # Get the current process ID (PID) of your project
# project_pid = os.getpid()

# count = 1
# while True:
#     print(f"Check {count}:")
#     get_gpu_utilization_by_pid(project_pid)
#     sleep(1)
#     count += 1