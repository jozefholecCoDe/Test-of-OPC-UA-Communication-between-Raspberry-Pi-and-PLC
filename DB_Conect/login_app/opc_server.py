from opcua import Server, ua
import mysql.connector
import time

# Inicializácia servera
server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4840/")
uri = "http://192.168.0.178/product"
idx = server.register_namespace(uri)

# Objekt a premenne
objects = server.get_objects_node()
product_obj = objects.add_object(idx, "ProductLookup")

product_code = product_obj.add_variable(idx, "productCode", "", varianttype=ua.VariantType.String)
product_name = product_obj.add_variable(idx, "productName", "", varianttype=ua.VariantType.String)
product_code.set_writable()

# Pripojenie na databázu
db = mysql.connector.connect(
    host="localhost",
    user="root",             # uprav podľa potreby
    password="SafeControl2523",             # ak máš heslo, doplň ho
    database="skuska"
)
cursor = db.cursor()

# Spustenie servera
server.start()
print("✅ OPC UA server beží na: opc.tcp://192.168.0.178:4840/")

try:
    last_code = ""

    while True:
        code = product_code.get_value()

        if code != last_code and code != "":
            print(f"🔍 Hľadám kód: {code}")
            cursor.execute("SELECT Nazov FROM produkty WHERE Kod = %s", (code,))
            result = cursor.fetchone()

            if result:
                name = result[0]
                product_name.set_value(name)
                print(f"✅ Nájdený produkt: {name}")
            else:
                product_name.set_value("NENÁJDENÝ")
                print("❌ Produkt neexistuje")

            last_code = code
            product_code.set_value("")

        time.sleep(1)

finally:
    server.stop()
    cursor.close()
    db.close()
    print("🛑 Server ukončený.")
