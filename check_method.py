# check_method.py - VERSIÓN CORREGIDA
import os

# Busca qué método está usando tu sheets_db.py
with open('modules/sheets_db.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
if 'from_service_account_file' in content and 'from_service_account_info' not in content:
    print("❌ Estás usando el método VIEJO (que no funciona)")
    print("   Necesitas cambiar a from_service_account_info")
elif 'from_service_account_info' in content:
    print("✅ Estás usando el método NUEVO")
    print("   Pero algo más está mal...")
else:
    print("⚠️ No encuentro ningún método de autenticación")

# Muestra las líneas relevantes
print("\nLíneas de autenticación encontradas:")
for i, line in enumerate(content.split('\n'), 1):
    if 'from_service_account' in line or 'Credentials.from' in line:
        print(f"  Línea {i}: {line.strip()}")