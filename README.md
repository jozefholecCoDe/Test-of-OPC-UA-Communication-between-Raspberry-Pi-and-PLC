# Test-of-OPC-UA-Communication-between-Raspberry-Pi-and-PLC

This repository contains a small testbed that demonstrates **OPC UA communication** and a simple **web app** running on a Raspberry Pi that talks to a **MySQL** database. There are two variants included in your code:

- **`login_app/opc_server.py`** — Raspberry Pi acts as an **OPC UA Server** exposing variables like `productCode`, `productName`, etc.; it reads a product code, looks it up in the DB, and publishes results back to the PLC (which acts as OPC UA client).
- **`login_app/opc_client_PI_v*.py`** — Raspberry Pi acts as an **OPC UA Client** connecting to a PLC OPC UA Server and exchanging trigger/response nodes.

Additionally, **`login_app/app.py`** is a small **Flask** web application that provides **login + user management** (roles: *admin*, *operator*).

> **Intended flow (your description)**: PLC sends a request to the Raspberry Pi → the Raspberry Pi queries the DB for a product → Raspberry Pi returns a response to the PLC. A basic web page on the Pi provides login and simple user management (add/remove user, username, password, role).

---

## Project structure (as in your ZIP)

```
DB_Conect/
├─ opc_client_PI_v0.1.py
├─ test_db.py
└─ login_app/
   ├─ app.py                 # Flask web UI (login, user management)
   ├─ opc_client.py          # Simple OPC UA client sample
   ├─ opc_client_PI.py       # OPC UA client (PLC <-> Pi), early version
   ├─ opc_client_PI_v0.2.py
   ├─ opc_client_PI_v1.0.py
   ├─ opc_client_PI_v1.1.py  # OPC UA client (latest variant)
   ├─ opc_server.py          # OPC UA server running on Pi
   ├─ users.sql              # Example SQL snippet
   ├─ static/
   │  ├─ script.js
   │  └─ style.css
   └─ templates/
      ├─ admin.html
      ├─ index.html
      ├─ login.html
      ├─ register.html
      └─ welcome.html
```
