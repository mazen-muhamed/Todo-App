# Cisco Final Exam — Full Step-by-Step Build Guide

Open this guide side-by-side with Packet Tracer. Work through **one device at a time**.

> Passwords used throughout: console=`cisco`, enable=`class`, VTY/SSH=`cisco`

---

## STEP 0: Place All Devices in Packet Tracer

Open Packet Tracer → **Network** tab → drag devices onto workspace.

```
CAIRO (center):
  1× 2911 Router    → name: CAIRO-R1
  1× 2960 Switch    → name: CAIRO-SW1
  1× Server         → name: CAIRO-WEB
  4× PC             → CAIRO-PC1, CAIRO-PC2, CAIRO-PC3, CAIRO-PC4

BRANCH 1 (top-left):
  1× 2911 Router    → name: BR1-R1
  1× 2960 Switch    → name: BR1-SW1
  4× PC             → BR1-PC1, BR1-PC2, BR1-PC3, BR1-PC4

BRANCH 2–5: same pattern (BR2-R1/SW1/PC1-4 … BR5-R1/SW1/PC1-4)
```

**Naming device in PT:** Click device → **Config** tab → change **Display Name** and hostname will be set by commands later.

---

## STEP 1: Cabling

### Cairo connections
| Cable color (suggested) | From              | Port     | To              | Port     |
|--------------------------|--------------------|----------|------------------|----------|
| ▐ ▐ dark blue            | CAIRO-R1           | Gi0/0    | CAIRO-SW1        | Gi0/1    |
| ▐ ▐ black                | CAIRO-R1           | Se0/0/0  | BR1-R1           | Se0/0/0  |
| ▐ ▐ black                | CAIRO-R1           | Se0/0/1  | BR2-R1           | Se0/0/0  |
| ▐ ▐ black                | CAIRO-R1           | Se0/1/0  | BR3-R1           | Se0/0/0  |
| ▐ ▐ black                | CAIRO-R1           | Se0/1/1  | BR4-R1           | Se0/0/0  |
| ▐ ▐ black                | CAIRO-R1           | Se0/2/0  | BR5-R1           | Se0/0/0  |
| ▐ ▐ light blue           | CAIRO-SW1          | Fa0/1    | CAIRO-PC1        | NIC      |
| ▐ ▐ light blue           | CAIRO-SW1          | Fa0/2    | CAIRO-PC2        | NIC      |
| ▐ ▐ light blue           | CAIRO-SW1          | Fa0/3    | CAIRO-PC3        | NIC      |
| ▐ ▐ light blue           | CAIRO-SW1          | Fa0/4    | CAIRO-PC4        | NIC      |
| ▐ ▐ light blue           | CAIRO-SW1          | Fa0/5    | CAIRO-WEB        | NIC      |

### Branch x connections (repeat for BR1–BR5)
| From         | Port     | To              | Port     |
|---------------|----------|------------------|----------|
| BRx-R1       | Gi0/0    | BRx-SW1          | Gi0/1    |
| BRx-SW1      | Fa0/1    | BRx-PC1          | NIC      |
| BRx-SW1      | Fa0/2    | BRx-PC2          | NIC      |
| BRx-SW1      | Fa0/3    | BRx-PC3          | NIC      |
| BRx-SW1      | Fa0/4    | BRx-PC4          | NIC      |

---

## STEP 2: Configure CAIRO-SW1 (VTP Server, VLANs, STP)

Click CAIRO-SW1 → **CLI** tab → press Enter.

```
enable
configure terminal

hostname CAIRO-SW1

! --- VTP Server Mode ---
vtp mode server
vtp domain cisco
vtp version 2

! --- STP: make this switch root for all VLANs ---
spanning-tree mode pvst
spanning-tree vlan 10 priority 4096
spanning-tree vlan 20 priority 4096
spanning-tree vlan 100 priority 4096

! --- VLANs ---
vlan 10
 name USERS-A
vlan 20
 name USERS-B
vlan 100
 name SERVERS
exit

! --- Trunk to router (Gi0/1) ---
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,100
 exit

! --- Access ports to PCs (VLAN 10) ---
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 10
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
 switchport port-security mac-address sticky
 exit

interface FastEthernet0/2
 switchport mode access
 switchport access vlan 10
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
 switchport port-security mac-address sticky
 exit

! --- Access ports to PCs (VLAN 20) ---
interface FastEthernet0/3
 switchport mode access
 switchport access vlan 20
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
 switchport port-security mac-address sticky
 exit

interface FastEthernet0/4
 switchport mode access
 switchport access vlan 20
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
 switchport port-security mac-address sticky
 exit

! --- Access port to Web Server (VLAN 100) ---
interface FastEthernet0/5
 switchport mode access
 switchport access vlan 100
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
 switchport port-security mac-address sticky
 exit

! --- Console password ---
line console 0
 password cisco
 login
 exit

! --- Enable secret ---
enable secret class

! --- VTY lines ---
line vty 0 4
 password cisco
 login
 transport input ssh
 exit

! --- Enable SSH ---
ip domain-name cisco.local
crypto key generate rsa general-keys modulus 1024
username admin password cisco
ip ssh version 2

exit
write memory
```

---

## STEP 3: Configure CAIRO-R1 (Router-on-a-Stick, OSPF, SSH)

Click CAIRO-R1 → **CLI** tab.

```
enable
configure terminal

hostname CAIRO-R1

! --- Security first ---
enable secret class

line console 0
 password cisco
 login
 exit

line vty 0 4
 password cisco
 login
 transport input ssh
 exit

ip domain-name cisco.local
crypto key generate rsa general-keys modulus 1024
username admin password cisco
ip ssh version 2

! --- Gateway interface to CAIRO-SW1 (router-on-a-stick) ---
interface GigabitEthernet0/0
 no shutdown
 exit

! --- Sub-interfaces ---
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
 exit

interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
 exit

interface GigabitEthernet0/0.100
 encapsulation dot1Q 100
 ip address 192.168.100.1 255.255.255.0
 exit

! --- WAN serial links to branches ---
! Cairo-R1 serial ports: Se0/0/0 → BR1-R1, Se0/0/1 → BR2-R1,
!                        Se0/1/0 → BR3-R1, Se0/1/1 → BR4-R1,
!                        Se0/2/0 → BR5-R1
! DCE ends (set clock rate):

interface Serial0/0/0
 ip address 10.0.1.1 255.255.255.252
 clock rate 64000
 no shutdown
 exit

interface Serial0/0/1
 ip address 10.0.2.1 255.255.255.252
 clock rate 64000
 no shutdown
 exit

interface Serial0/1/0
 ip address 10.0.3.1 255.255.255.252
 clock rate 64000
 no shutdown
 exit

interface Serial0/1/1
 ip address 10.0.4.1 255.255.255.252
 clock rate 64000
 no shutdown
 exit

interface Serial0/2/0
 ip address 10.0.5.1 255.255.255.252
 clock rate 64000
 no shutdown
 exit

! --- OSPF: advertise everything ---
router ospf 1
 network 192.168.10.0 0.0.0.255 area 0
 network 192.168.20.0 0.0.0.255 area 0
 network 192.168.100.0 0.0.0.255 area 0
 network 10.0.1.0 0.0.0.3 area 0
 network 10.0.2.0 0.0.0.3 area 0
 network 10.0.3.0 0.0.0.3 area 0
 network 10.0.4.0 0.0.0.3 area 0
 network 10.0.5.0 0.0.0.3 area 0
 exit

exit
write memory
```

---

## STEP 4: Configure CAIRO-WEB Server

Click the **Server** device → **Desktop** tab → **IP Configuration**:

```
IP Address:   192.168.100.10
Subnet Mask:  255.255.255.0
Default GW:   192.168.100.1
```

Then **Services** tab → **HTTP** → turn **ON** both HTTP and HTTPS.

Edit `index.html` (optional):
```html
<h1>Cairo Web Server</h1>
<p>This site is hosted on the Cairo Main Branch Web Server.</p>
<p>VLAN 100 — Network Final Exam</p>
```

**PC Default Gateways (configure each PC via Desktop → IP Config):**

| Device | IP | Subnet Mask | Default Gateway |
|--------|-----|-------------|-----------------|
| CAIRO-PC1 | 192.168.10.2 | 255.255.255.0 | 192.168.10.1 |
| CAIRO-PC2 | 192.168.10.3 | 255.255.255.0 | 192.168.10.1 |
| CAIRO-PC3 | 192.168.20.2 | 255.255.255.0 | 192.168.20.1 |
| CAIRO-PC4 | 192.168.20.3 | 255.255.255.0 | 192.168.20.1 |
| CAIRO-WEB | 192.168.100.10 | 255.255.255.0 | 192.168.100.1 |

---

## STEP 5: Configure Branch Switches (×5)

> **Important:** Switches in remote branches are VTP **CLIENTs**. They receive
> VLANs automatically from CAIRO-SW1 (once trunk/WAN is up, VTP propagates).
> So configure them AFTER CAIRO-SW1.

### Example: BR1-SW1 (repeat with appropriate names for BR2–BR5)

```
enable
configure terminal

hostname BR1-SW1

! --- VTP Client ---
vtp mode client
vtp domain cisco
vtp version 2

! --- STP: higher priority (non-root) ---
spanning-tree mode pvst

! --- Trunk to router ---
interface GigabitEthernet0/1
 switchport mode trunk
 exit

! --- Access ports (VLAN 10: Fa0/1-2, VLAN 20: Fa0/3-4) ---
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 10
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
 switchport port-security mac-address sticky
 exit

interface FastEthernet0/2
 switchport mode access
 switchport access vlan 10
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
 switchport port-security mac-address sticky
 exit

interface FastEthernet0/3
 switchport mode access
 switchport access vlan 20
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
 switchport port-security mac-address sticky
 exit

interface FastEthernet0/4
 switchport mode access
 switchport access vlan 20
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
 switchport port-security mac-address sticky
 exit

! --- Console password ---
line console 0
 password cisco
 login
 exit

! --- Enable secret ---
enable secret class

! --- VTY + SSH ---
line vty 0 4
 password cisco
 login
 transport input ssh
 exit

ip domain-name cisco.local
crypto key generate rsa general-keys modulus 1024
username admin password cisco
ip ssh version 2

exit
write memory
```

---

## STEP 6: Configure Branch Routers (×5)

### Example: BR1-R1

Replace names and IPs according to the table in findings.md.

```
enable
configure terminal

hostname BR1-R1

! --- Security ---
enable secret class
line console 0
 password cisco
 login
 exit
line vty 0 4
 password cisco
 login
 transport input ssh
 exit
ip domain-name cisco.local
crypto key generate rsa general-keys modulus 1024
username admin password cisco
ip ssh version 2

! --- Gateway to local switch (router-on-a-stick) ---
interface GigabitEthernet0/0
 no shutdown
 exit

interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
 exit

interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
 exit

! --- WAN serial link to Cairo-R1 ---
! BR1-R1 Se0/0/0 (DCE for BR1 side — set clock rate)
interface Serial0/0/0
 ip address 10.0.1.2 255.255.255.252
 clock rate 64000
 no shutdown
 exit

! --- OSPF ---
router ospf 1
 network 192.168.10.0 0.0.0.255 area 0
 network 192.168.20.0 0.0.0.255 area 0
 network 10.0.1.0 0.0.0.3 area 0
 exit

exit
write memory
```

### BR2–BR5: same pattern, substitute values:

| Router | VLAN 10 IF     | VLAN 20 IF     | WAN IF        | WAN IP      | OSPF networks           |
|--------|----------------|----------------|---------------|-------------|-------------------------|
| BR2-R1 | 192.168.30.1/24| 192.168.40.1/24| Se0/0/0       | 10.0.2.2/30 | 192.168.30/40 + 10.0.2.0 |
| BR3-R1 | 192.168.50.1/24| 192.168.60.1/24| Se0/0/0       | 10.0.3.2/30 | 192.168.50/60 + 10.0.3.0 |
| BR4-R1 | 192.168.70.1/24| 192.168.80.1/24| Se0/0/0       | 10.0.4.2/30 | 192.168.70/80 + 10.0.4.0 |
| BR5-R1 | 192.168.90.1/24| 192.168.100.1/24| Se0/0/0     | 10.0.5.2/30 | 192.168.90/100 + 10.0.5.0 |

### Branch PC IP Configs

| Branch | PC   | IP             | GW              |
|--------|------|----------------|-----------------|
| BR1    | PC1  | 192.168.10.2   | 192.168.10.1    |
| BR1    | PC2  | 192.168.10.3   | 192.168.10.1    |
| BR1    | PC3  | 192.168.20.2   | 192.168.20.1    |
| BR1    | PC4  | 192.168.20.3   | 192.168.20.1    |
| BR2    | PC1  | 192.168.30.2   | 192.168.30.1    |
| BR2    | PC2  | 192.168.30.3   | 192.168.30.1    |
| BR2    | PC3  | 192.168.40.2   | 192.168.40.1    |
| BR2    | PC4  | 192.168.40.3   | 192.168.40.1    |
| BR3    | PC1  | 192.168.50.2   | 192.168.50.1    |
| BR3    | PC2  | 192.168.50.3   | 192.168.50.1    |
| BR3    | PC3  | 192.168.60.2   | 192.168.60.1    |
| BR3    | PC4  | 192.168.60.3   | 192.168.60.1    |
| BR4    | PC1  | 192.168.70.2   | 192.168.70.1    |
| BR4    | PC2  | 192.168.70.3   | 192.168.70.1    |
| BR4    | PC3  | 192.168.80.2   | 192.168.80.1    |
| BR4    | PC4  | 192.168.80.3   | 192.168.80.1    |
| BR5    | PC1  | 192.168.90.2   | 192.168.90.1    |
| BR5    | PC2  | 192.168.90.3   | 192.168.90.1    |
| BR5    | PC3  | 192.168.100.2  | 192.168.100.1   |
| BR5    | PC4  | 192.168.100.3  | 192.168.100.1   |

---

## STEP 7: Verification Commands

Run these on the CLI of each device to take your screenshots.

### VLANs
```
on CAIRO-SW1:
  show vlan brief
on BRx-SW1:
  show vlan brief
```

### VTP Status
```
on CAIRO-SW1:
  show vtp status        (should say mode: Server)
on BRx-SW1:
  show vtp status        (should say mode: Client)
```

### STP
```
on CAIRO-SW1:
  show spanning-tree
  show spanning-tree summary
  (should be ROOT for all VLANs — priority 4096)
```

### Port Security
```
on any switch:
  show port-security
  show port-security interface Fa0/1
```

### OSPF Neighbors
```
on CAIRO-R1:
  show ip ospf neighbor
  (should show 5 neighbors — all branches)
on BRx-R1:
  show ip ospf neighbor
  (should show 1 neighbor — CAIRO-R1)
```

### SSH
```
on CAIRO-R1 or BRx-R1:
  show ip ssh
  show running-config | include line vty
from a PC terminal:
  ssh -l admin 192.168.10.1
  (then type password: cisco)
```

### Ping Tests (from any PC)
```
from CAIRO-PC1:
  ping 192.168.20.2    (same VLAN different subnet → via gateway)
  ping 192.168.100.10  (to web server)
  ping 192.168.10.2     (to BR1-PC1, across OSPF)
  ping 192.168.30.2     (to BR2-PC1, across OSPF)

from BR1-PC1:
  ping 192.168.100.10  (web server in Cairo)
```

### Web Server Access
```
from any PC:
  open Web Browser → http://192.168.100.10
  (should show Cairo Web Server page)
```
