from opcua import Client
import time

# Pripojenie na OPC UA server
client = Client("opc.tcp://192.168.0.178:4840/")
try:
    client.connect()
    print("✅ Pripojené na OPC UA server")

    # Získanie premenných
    root = client.get_root_node()
    objects = root.get_child(["0:Objects", "2:ProductLookup"])
    product_code_node = objects.get_child("2:productCode")
    product_name_node = objects.get_child("2:productName")

    # Zadanie kódu produktu
    code_to_find = input("🔢 Zadaj kód produktu: ")
    product_code_node.set_value(code_to_find)

    # Počkaj na odpoveď
    print("⏳ Čakám na odpoveď zo servera...")
    time.sleep(1)

    for _ in range(10):
        name = product_name_node.get_value()
        if name and name != "":
            print(f"✅ Nájdený produkt: {name}")
            break
        time.sleep(1)
    else:
        print("❌ Nepodarilo sa nájsť produkt.")

finally:
    client.disconnect()
    print("🔌 Odpojené")

