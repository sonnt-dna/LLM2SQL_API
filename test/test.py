  # STEP 9: Check Provisioning State
import subprocess
command = ['az', 'containerapp', 'show',
        '--name', 'duc-c2',
        '--subscription', '2f9bda04-bf37-41f3-901e-31537a8b84d3', 
        '--resource-group', 'azc-container-app-rs-group',
        '--query', 'properties.runningStatus']
try:
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    print(result.stdout)
    if result.returncode == 0:
        running_state = result.stdout
    else:
        print(result.stderr)
        raise SystemExit("Lỗi khi thực hiện lệnh kiểm tra Running State")
except subprocess.CalledProcessError as e:
    print(e.stderr)
    raise SystemExit("Lỗi khi thực hiện lệnh Running State")
