from opcua import Client, ua
import mysql.connector
import time

# OPC UA adresa PLC
plc_url = "opc.tcp://192.168.1.1:4840"
client = Client(plc_url)

try:
    client.connect()
    print("🔗 Pripojené na PLC OPC UA Server")

    # Získaj uzly z PLC
    connect_trigger_node = client.get_node("ns=4;i=8")      # Trigger na pripojenie do DB
    connected_status_node = client.get_node("ns=4;i=9")     # Spätná väzba - pripojenie OK
    lookup_trigger_node = client.get_node("ns=4;i=2")       # Trigger na vyhľadávanie
    product_code_node = client.get_node("ns=4;i=3")
    product_name_node = client.get_node("ns=4;i=4")
    disconnect_trigger_node = client.get_node("ns=4;i=7")   # Trigger na ukončenie cyklu
    login_trigger = client.get_node("ns=4;i=10")  # trigger login
    login_name_node = client.get_node("ns=4;i=12")  # meno
    login_pass_node = client.get_node("ns=4;i=13")  # heslo
    logged_node = client.get_node("ns=4;i=11")  # výstup loginu (bool)
    life_bit_node = client.get_node("ns=4;i=14")  # životnosť servera

    # Life bit toggle
    lifebit = False
    lifebit_timer = time.time()

    db = None
    cursor = None
    connected = False
    vypisane = False

    while True:
        # 🔁 Každú sekundu pošli life bit
        if time.time() - lifebit_timer > 1:
            lifebit = not lifebit
            life_bit_node.set_value(
                ua.DataValue(ua.Variant(lifebit, ua.VariantType.Boolean))
            )
            lifebit_timer = time.time()

        # 🔐 Čakanie na login trigger
        if not logged_node.get_value():
            if not vypisane:
                print("🔐 Čakám na prihlásenie...")
                vypisane = True

        if not logged_node.get_value():
            if login_trigger.get_value():
                meno = login_name_node.get_value()
                heslo = login_pass_node.get_value()
                print(f"🔐 Prihlasovanie používateľa: {meno}")

                try:
                    db = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="SafeControl2523",
                        database="skuska"
                    )
                    cursor = db.cursor()
                    cursor.execute("SELECT * FROM users WHERE Name = %s AND Password = %s", (meno, heslo))
                    prihlaseny = cursor.fetchone() is not None
                    if prihlaseny:
                        print("✅ Prihlásenie úspešné")
                        logged_node.set_value(
                            ua.DataValue(ua.Variant(True, ua.VariantType.Boolean))
                        )
                        vypisane = False
                    else:
                        print("❌ Neúspešné prihlásenie")
                        logged_node.set_value(
                            ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
                        )
                        vypisane = False

                    # zatvoriť spojenie po overení
                    cursor.close()
                    db.close()
                except Exception as e:
                    print(f"❗ Chyba pri prihlasovaní: {e}")
                    logged_node.set_value(
                        ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
                    )

            login_trigger.set_value(
                ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
                )
        time.sleep(0.2)

        connect_trigger = connect_trigger_node.get_value()
        disconnect_trigger = disconnect_trigger_node.get_value()

        # 1️⃣ Pripojenie do DB
        if connect_trigger and not connected:
            try:
                db = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="SafeControl2523",
                    database="skuska"
                )
                cursor = db.cursor()
                connected = True
                connected_status_node.set_value(
                    ua.DataValue(ua.Variant(True, ua.VariantType.Boolean))
                )
                print("✅ Pripojenie k DB nadviazané.")
            except Exception as e:
                print(f"❗ Chyba pri pripájaní do DB: {e}")
                connected_status_node.set_value(
                    ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
                )
            finally:
                # Reset connect_trigger vždy po pokuse o pripojenie
                connect_trigger_node.set_value(
                    ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
                )

        # 2️⃣ Vyhľadávanie
        if connected and lookup_trigger_node.get_value():
            code = product_code_node.get_value()
            print(f"🔍 Hľadám produkt pre kód: {code}")
            cursor.execute("SELECT Nazov FROM produkty WHERE Kod = %s", (code,))
            result = cursor.fetchone()

            if result:
                product_name_node.set_value(
                    ua.DataValue(ua.Variant(result[0], ua.VariantType.String))
                )
                print(f"✅ Nájdený: {result[0]}")
            else:
                product_name_node.set_value(
                    ua.DataValue(ua.Variant("NENÁJDENÝ", ua.VariantType.String))
                )
                print("❌ Produkt nenájdený")

            # Reset lookup trigger
            lookup_trigger_node.set_value(
                ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
            )

        # 3️⃣ Ukončenie
        if connected and disconnect_trigger:
            print("⛔ Ukončujem spojenie s DB.")
            try:
                cursor.close()
                db.close()
                print("✅ Spojenie s DB úspešne ukončené.")
            except Exception as e:
                print(f"❗ Chyba pri zatváraní DB: {e}")
            connected = False
            connected_status_node.set_value(
                ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
            )
            disconnect_trigger_node.set_value(
                ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
            )
            logged_node.set_value(
                ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
                )
            login_trigger.set_value(
                ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
            )  
            print("👤 Používateľ odhlásený...")

        time.sleep(0.2)

except Exception as e:
    print(f"❗ Chyba: {e}")

finally:
    # Reset pripojenia k DB pri ukončení programu
    try:
        connected_status_node.set_value(
            ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
        )
        connect_trigger_node.set_value(
            ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
        )
        disconnect_trigger_node.set_value(
            ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
        )
        logged_node.set_value(
            ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
        )
        login_trigger.set_value(
            ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
        )
        life_bit_node.set_value(
            ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
        )
    except:
        pass

    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'db' in locals() and db:
        db.close()
    print("🔴 Server ukončený.")