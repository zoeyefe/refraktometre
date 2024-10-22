import cv2
import numpy as np
import snap7
from snap7.util import *
import time

def get_measurement_value_from_image(image_path):
    # Görüntüyü yükle
    image = cv2.imread(image_path)

    # Görüntünün boyutunu öğren
    height, width = image.shape[:2]

    # 0 ve 100 değerlerinin y koordinatlarını belirle
    y_for_0 = 470  # 0 değeri için y koordinatı
    y_for_100 = 30  # 100 değeri için y koordinatı

    # Renk alanını HSV formatına çevir
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Mavi renk için HSV aralıkları belirle
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([130, 255, 255])

    # Mavi alanı maskelemek
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Maskelemeden sonra mavi alanın üst sınırını bulma
    max_y = None
    for y in range(height-1, -1, -1):  # Y ekseninde yukarıdan aşağıya doğru tara
        if np.any(mask[y, :] > 0):
            max_y = y
            break

    # Geçiş çizgisini bulduysak, değeri hesaplayalım
    if max_y is not None and y_for_100 <= max_y <= y_for_0:
        # max_y'yi 100'den 0'a ölçeklendir
        value = int(100 * ((max_y - y_for_100) / (y_for_0 - y_for_100)))
    else:
        value = 0  # Eğer geçiş bulunamazsa 0 değeri dön

    # Hesaplanan değeri ekranda göster
    print(f"Hesaplanan Değer: {value}")

    # Görüntüyü ve maskeyi güncelleyerek göster
    cv2.imshow("Maske", mask)

    # 1 ms bekleyerek pencerenin güncellenmesini sağla
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return None  # 'q' tuşuna basıldıysa döngüyü durdur
    return value

def write_integer_to_plc(value, plc_ip, rack, slot, db_number, start_address):
    # PLC'ye bağlan
    plc = snap7.client.Client()
    plc.connect(plc_ip, rack, slot)

    if not plc.get_connected():
        print("PLC bağlantısı başarısız oldu.")
        return

    # Integer (16-bit) veriyi hazırlama
    data = bytearray(2)
    set_int(data, 0, value)  # 0'dan başlayarak 'value'yu integer olarak ayarla

    # PLC'ye yazma (Data Block 1 örneğinde)
    plc.db_write(db_number, start_address, data)

    # Bağlantıyı kes
    plc.disconnect()

# Sonsuz döngüde her 10 saniyede bir görüntü işleme ve PLC'ye veri gönderme
while True:
    # Görüntüden değeri oku
    measurement_value = get_measurement_value_from_image('4.png')

    # Eğer değer başarıyla hesaplandıysa PLC'ye yaz
    if measurement_value is not None:
        plc_ip_address = '192.168.1.100'  # PLC'nin IP adresini ayarlayın
        rack_number = 0  # Rack numarasını ayarlayın (genellikle 0)
        slot_number = 1  # Slot numarasını ayarlayın (genellikle 1)
        db_number = 1    # Data Block numarasını ayarlayın
        start_byte = 0   # Başlangıç adresini ayarlayın

        # Hesaplanan değeri PLC'ye yaz
        write_integer_to_plc(measurement_value, plc_ip_address, rack_number, slot_number, db_number, start_byte)

    # 10 saniye bekle
    time.sleep(10)

# Pencereleri kapat
cv2.destroyAllWindows()