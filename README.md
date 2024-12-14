# Distributed-System-Project
This repository contains the implementation of a Distributed System designed for the course exam. The project integrates hardware components, a server, and a web interface to manage participants and communication within the system.

Project Description
The project centers around a distributed environment where multiple hardware clients interact with a central server. Clients include totems and participating teams, which use NFC readers and WiFi modules to communicate with the server. The server handles requests, processes data, and maintains transaction workflows, while a web interface displays results to end users.

Clients are initialized using Arduino-compatible .ino files. 
These files configure the hardware components, including WiFi connections and NFC readers.
- AP_Wifi.ino sets up the WiFi Access Point.
- Client_Wifi.ino manages client WiFi connections.
- ReadNFC.ino handles data collection from NFC readers.
- Totem.ino contains logic specific to totem devices.

The server is implemented in Python (Flask).
It manages client requests, processes transactions, and synchronizes data. 
The main server files include:
- LockCommit.py for locking and committing data to ensure consistency.
- TransactionManager.py to oversee transaction workflows.
- serverCommit.py the server script to be runned.

A simple yet effective .html file (leaderboard.html) serves as the front-end interface. It allows users to view results, and rankings.

How to Set Up and Run

Client Setup:
Upload the .ino files to your hardware devices (e.g., Arduino boards).
Ensure NFC readers and WiFi credentials are correctly configured.

Server Deployment:
Install Python 3.x on your machine.
Run the required server script.

Web Interface:
Open leaderboard.html in your browser to view rankings and results.
