import sys
import os.path
from Tkinter import *
import ttk

def cidr_to_netmask(cidr):
  cidr = int(cidr)
  mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
  return (str( (0xff000000 & mask) >> 24)   + '.' +
          str( (0x00ff0000 & mask) >> 16)   + '.' +
          str( (0x0000ff00 & mask) >> 8)    + '.' +
          str( (0x000000ff & mask)))

def check_input_ip(input_ip):
    # Validate the IP
    octet_ip = input_ip.split(".")
    try:
        int_octet_ip = [int(i) for i in octet_ip]

        if (len(int_octet_ip) == 4) and \
            (int_octet_ip[0] != 127) and \
            (int_octet_ip[0] != 169) and  \
            (0 <= int_octet_ip[1] <= 255) and \
            (0 <= int_octet_ip[2] <=255) and \
            (0 <= int_octet_ip[3] <= 255):
            return int_octet_ip
        else:
            return 0
    except ValueError:
        return 0

def check_input_mask(input_subnet):
    # Predefine possible subnet masks
    masks = [0, 128, 192, 224, 240, 248, 252, 254, 255]
    try:
        # Convert cidr to subnet mask
        if (input_subnet.isdigit()):
            if(int(input_subnet) > 0 and int(input_subnet) < 33):
                input_subnet = cidr_to_netmask(input_subnet)
                octet_subnet = [int(j) for j in input_subnet.split(".")]
                return octet_subnet
            else:
                return 0
        else:    
            # Validate the subnet mask
            octet_subnet = [int(j) for j in input_subnet.split(".")]
            if (len(octet_subnet) == 4) and \
                    (octet_subnet[0] == 255) and \
                    (octet_subnet[1] in masks) and \
                    (octet_subnet[2] in masks) and \
                    (octet_subnet[3] in masks) and \
                    (octet_subnet[0] >= octet_subnet[1] >= octet_subnet[2] >= octet_subnet[3]):
                    return octet_subnet
            else:
                return 0
    except ValueError:
        return 0

# Converting IP and subnet to binary
def subnet_calc(input_ip, input_subnet,int_octet_ip,octet_subnet):
    try:
        ip_in_binary = []

        # Convert each IP octet to binary
        ip_in_bin_octets = [bin(i).split("b")[1] for i in int_octet_ip]

        # make each binary octet of 8 bit length by padding zeros
        for i in range(0,len(ip_in_bin_octets)):
            if len(ip_in_bin_octets[i]) < 8:
                padded_bin = ip_in_bin_octets[i].zfill(8)
                ip_in_binary.append(padded_bin)
            else:
                ip_in_binary.append(ip_in_bin_octets[i])

        # join the binary octets
        ip_bin_mask = "".join(ip_in_binary)

        # print ip_bin_mask

        sub_in_bin = []

        # convert each subnet octet to binary
        sub_bin_octet = [bin(i).split("b")[1] for i in octet_subnet]

        # make each binary octet of 8 bit length by padding zeros
        for i in sub_bin_octet:
            if len(i) < 8:
                sub_padded = i.zfill(8)
                sub_in_bin.append(sub_padded)
            else:
                sub_in_bin.append(i)

        # print sub_in_bin
        sub_bin_mask = "".join(sub_in_bin)

        # calculating number of hosts
        no_zeros = sub_bin_mask.count("0")
        no_ones = 32 - no_zeros
        no_hosts = abs(2 ** no_zeros - 2)

        # Calculating wildcard mask
        wild_mask = []
        for i in octet_subnet:
            wild_bit = 255 - i
            wild_mask.append(wild_bit)

        wildcard = ".".join([str(i) for i in wild_mask])

        # Calculating the network and broadcast address
        network_add_bin = ip_bin_mask[:no_ones] + "0" * no_zeros
        broadcast_add_bin = ip_bin_mask[:no_ones] + "1" * no_zeros

        network_add_bin_octet = []
        broadcast_binoct = []

        [network_add_bin_octet.append(i) for i in [network_add_bin[j:j+8]
                                                   for j in range(0, len(network_add_bin), 8)]]
        [broadcast_binoct.append(i) for i in [broadcast_add_bin[j:j+8]
                                              for j in range(0,len(broadcast_add_bin),8)]]

        network_add_dec_final = ".".join([str(int(i,2)) for i in network_add_bin_octet])
        broadcast_add_dec_final = ".".join([str(int(i,2)) for i in broadcast_binoct])

        # Calculate the host IP range
        first_ip_host = network_add_bin_octet[0:3] + [(bin(int(network_add_bin_octet[3],2)+1).split("b")[1].zfill(8))]
        first_ip = ".".join([str(int(i,2)) for i in first_ip_host])

        last_ip_host = broadcast_binoct[0:3] + [bin(int(broadcast_binoct[3],2) - 1).split("b")[1].zfill(8)]
        last_ip = ".".join([str(int(i,2)) for i in last_ip_host])

        # print all the computed results
        tex.insert(END, "IP Address : " + input_ip + "\n")
        tex.insert(END, "Subnet mask : " +  '.'.join(map(str, octet_subnet)) + "\n")
        tex.insert(END, "Number of mask bits : {0}".format(str(no_ones)) + "\n")
        tex.insert(END, "Wildcard mask : {0}".format(wildcard) + "\n")
        tex.insert(END, "\n")
        tex.insert(END, "Network address : {0}".format(network_add_dec_final) + "\n")
        tex.insert(END, "Broadcast address : {0}".format(broadcast_add_dec_final) + "\n")
        tex.insert(END, "\n")
        tex.insert(END, "Host min : {0}".format(first_ip) + "\n")
        tex.insert(END, "Host max : {0}".format(last_ip) + "\n")
        tex.insert(END, "\n")
        tex.insert(END, "Number of hosts per subnet: {0}".format(str(no_hosts)) + "\n")
        tex.insert(END, "Maximum number of subnets is: " + str(2**abs(24 - no_ones)) + "\n")
        tex.insert(END, "\n\n")

        #automatically scrolldown
        tex.see(END)
        tex.focus_set()

    except ValueError:
        tex.insert(END,"Seem to have entered an incorrect value\n")

def clear_text():
    tex.delete(1.0,END)

def calculate():
    clear_text()
    input_ip = var_ip.get()
    int_octet_ip = 0
    octet_subnet = 0
    if check_input_ip(input_ip):
        int_octet_ip = check_input_ip(input_ip)
    else:
        tex.insert(END, "Invalid IP, retry\n")
    input_subnet = var_mask.get()
    if check_input_mask(input_subnet):
        octet_subnet = check_input_mask(input_subnet)
    else:
        tex.insert(END,"Invalid subnet mask, retry\n")
    
    if int_octet_ip != 0 and octet_subnet != 0:
        subnet_calc(input_ip, input_subnet, int_octet_ip, octet_subnet)
    else:
        tex.insert(END,"Seem to have entered an incorrect value\n")

window = Tk()
window.title("IP Calculator")

window.grid_rowconfigure(0, weight=2)
window.grid_columnconfigure(0, weight=0)
window.grid_columnconfigure(1, weight=2)

froot = Frame(window)
froot.grid(row=0, column=0, padx=5, pady=5, sticky="NSEW")

f0 = Frame(froot, bd=1, relief="sunken")
f0.grid(row=0, column=0, sticky='we', rowspan=1, padx=5, pady=5)

f1 = Frame(froot, bd=1, relief="sunken")
f1.grid(row=1, column=0, sticky='we', rowspan=1, padx=5, pady=5)

f2 = Frame(window, bd=1, relief="sunken")
f2.grid(row=0, column=1, padx=5, pady=5, sticky="NSEW", rowspan=1)
#f2.grid_rowconfigure(0, weight=1)
#f2.grid_columnconfigure(0, weight=0)

message = Label(f0, text="IP Calculator and IP Subnetting")
message.grid(row=0, column=2, padx=5, pady=5)

label_ip = Label(f1, text="IP Address ").grid(row=1, padx=5, pady=5)
var_ip = StringVar()
line_ip = Entry(f1, textvariable=var_ip, width=30)
line_ip.grid(row=1, column=1, padx=5, pady=5)
line_ip.focus()

label_mask = Label(f1, text="Netmask ")
label_mask.grid(row=2, padx=5, pady=5)
var_mask = StringVar()
line_mask = Entry(f1, textvariable=var_mask, width=30)
line_mask.grid(row=2, column=1, padx=5, pady=5)

tex = Text(master=f2)
scr=Scrollbar(f2, orient=VERTICAL, command=tex.yview)
scr.grid(row=0, column=1, sticky=NS)
tex.grid(row=0, column=0, sticky=NSEW, padx=5, pady=5)
tex.config(yscrollcommand=scr.set, font=('Arial', 10), width = 35, height = 20)

button_calc = Button(f1, text="Calculate", fg="black", command=calculate)
button_calc.grid(row=3, column=0)
window.bind('<Return>', lambda e: calculate())

window.geometry("580x360")
window.mainloop()
