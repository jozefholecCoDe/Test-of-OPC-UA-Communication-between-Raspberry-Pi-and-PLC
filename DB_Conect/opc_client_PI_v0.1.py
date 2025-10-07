from opcua import Client
import mysql.connector
import time

# OPC UA adresa PLC
plc_url = "opc.tcp://192.168.1.1:4840"
client = Client(plc_url)

try:
    client.connect()
    print("🔗 Pripojené na PLC OPC UA Server")

    # Prístup k PLC premenným cez NodeId z UaExpert
    lookup_trigger_node = client.get_node("ns=4;i=2")
    product_code_node = client.get_node("ns=4;i=3")
    product_name_node = client.get_node("ns=4;i=4")

    # Pripojenie na databázu MariaDB
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="SafeControl2523",
        database="skuska"
    )
    cursor = db.cursor()

    while True:
        trigger = lookup_trigger_node.get_value()
        if trigger:
            code = product_code_node.get_value()
            print(f"🔍 Hľadám produkt pre kód: {code}")
            cursor.execute("SELECT Nazov FROM produkty WHERE Kod = %s", (code,))
            result = cursor.fetchone()

            if result:
                product_name_node.set_value(result[0])
                print(f"✅ Nájdený: {result[0]}")
            else:
                product_name_node.set_value("NENÁJDENÝ")
                print("❌ Produkt nenájdený")

            # Resetuj spúšťač v PLC
            lookup_trigger_node.set_value(False)

        time.sleep(0.2)

except Exception as e:
    print(f"❗ Chyba: {e}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'db' in locals():
        db.close()
    print("🔴 Server ukončený.")
