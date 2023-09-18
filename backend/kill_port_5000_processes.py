
import os
import signal

def kill_process_on_port(port):
    try:
        # Find the PIDs (process IDs) of the processes running on the given port
        cmd = f"lsof -t -i:{port}"
        pids = os.popen(cmd).read().strip().splitlines()
        if pids:
            for pid in pids:
                os.kill(int(pid), signal.SIGKILL)
                print(f"Killed process running on port {port} with PID {pid}")
        else:
            print(f"No process running on port {port}")
    except Exception as e:
        print(f"Error killing process on port {port}: {e}")

kill_process_on_port(5000)
