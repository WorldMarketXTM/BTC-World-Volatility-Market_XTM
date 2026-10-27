import time
from datetime import datetime
import json
import websocket

# Configuración inicial basada en tus análisis financieros
SYMBOL = "btcusdt"
SOCKET_URL = f"wss://stream.binance.com:9443/ws/{SYMBOL}@ticker"
THRESHOLD = 375.0  # Umbral de variación ajustado a $375 dólares por hora

base_price = None
current_hour = None

def on_message(ws, message):
    global base_price, current_hour
    
    data = json.loads(message)
    current_price = float(data['c']) # Precio actual de cierre en milisegundos
    now = datetime.now()
    hour_now = now.hour

    # Si es la primera ejecución o cambió la hora, actualizamos el precio base de la hora
    if base_price is None or current_hour != hour_now:
        base_price = current_price
        current_hour = hour_now
        print(f"\n[{now.strftime('%H:%M:%S')}] NUEVA HORA DETECTADA. Precio Base fijado en: ${base_price:.2f}")
        return

    # Calcular la variación (delta) respecto al precio base de la hora anterior
    delta = current_price - base_price
    sign = "+" if delta >= 0 else ""
    
    # Mostrar estado en consola en tiempo real
    print(f"\rPrecio: ${current_price:.2f} | Variación: {sign}${delta:.2f} (Base: ${base_price:.2f})", end="")

    # Evaluar la condición de alerta por los $375
    if abs(delta) >= THRESHOLD:
        print(f"\n\n🚨 ¡ALERTA DE OPORTUNIDAD / VOLATILIDAD! 🚨")
        print(f"Hora: {now.strftime('%H:%M:%S')}")
        print(f"Se ha superado el umbral de ${THRESHOLD} con una variación de: {sign}${delta:.2f}")
        print(f"Precio actual: ${current_price:.2f} | Precio inicial de hora: ${base_price:.2f}\n")
        
        # Pausa breve para evitar saturación en el mismo momento crítico
        time.sleep(2)

def on_error(ws, error):
    print(f"\n[Error de Conexión]: {error}")

def on_close(ws, close_status_code, close_msg):
    print("\n[Conexión cerrada con Binance. Reconectando...]")

def on_open(ws):
    print(f"--- Conectado a Binance WebSocket para BTC/USDT ---")
    print(f"Monitoreando variaciones mayores a ±${THRESHOLD} en la ventana horaria...\n")

if __name__ == "__main__":
    # Bucle de reconexión automática ante cualquier interrupción de internet
    while True:
        try:
            ws = websocket.WebSocketApp(SOCKET_URL,
                                      on_open=on_open,
                                      on_message=on_message,
                                      on_error=on_error,
                                      on_close=on_close)
            ws.run_forever()
        except Exception as e:
            print(f"Reintentando conexión en 5 segundos... Error: {e}")
            time.sleep(5)
