#!/usr/bin/env python3
# Shebang: Python 3 ortamında çalıştırılabilir bir betik olduğunu belirtir.

import time  # Zaman gecikmesi ve zamanla ilgili işlemler için.
import json  # JSON formatında dosya okuma/yazma işlemleri için.
import os  # Dosya ve dizin işlemleri için.
from watchdog.observers import Observer  # Dosya sistemini izlemek için gözlemci sınıfı.
from watchdog.events import FileSystemEventHandler  # Dosya sistemindeki olayları işlemek için temel sınıf.
from datetime import datetime  # Tarih ve saat bilgisi almak için.
import hashlib  # Dosya hash değerlerini hesaplamak için (MD5 kullanımı).

# Değişiklikleri işlemek için özelleştirilmiş bir sınıf tanımlıyoruz.
class ChangeHandler(FileSystemEventHandler):
    def __init__(self, log_file):
        # Log dosyasının yolu belirtiliyor ve son olay bilgisi için bir yapı oluşturuluyor.
        self.log_file = log_file
        self.last_event = {}  # En son olayların takibini yapmak için bir sözlük.
        self.initialize_log_file()  # Log dosyasını başlat.

    def initialize_log_file(self):
        """Log dosyasını başlatmak için bir fonksiyon."""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)  # Log dosyasının bulunduğu dizini oluştur.
        if not os.path.exists(self.log_file):  # Eğer log dosyası yoksa:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)  # Boş bir JSON listesi oluştur.

    def _read_logs(self):
        """Log dosyasını oku ve JSON formatında geri döndür."""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)  # Log dosyasını JSON olarak yükle.
        except (FileNotFoundError, json.JSONDecodeError):  # Dosya bulunamazsa veya JSON hatalıysa:
            return []  # Boş bir liste döndür.

    def _write_logs(self, logs):
        """Log dosyasına verileri yaz."""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)  # Logları JSON formatında dosyaya yaz.

    def _write_log(self, log_entry):
        """Yeni bir log girdisini log dosyasına ekle."""
        logs = self._read_logs()  # Mevcut logları oku.
        logs.append(log_entry)  # Yeni log girdisini mevcut loglara ekle.
        self._write_logs(logs)  # Güncellenmiş logları tekrar dosyaya yaz.

    def _get_file_info(self, path):
        """Dosya hakkında detaylı bilgi al."""
        try:
            if os.path.exists(path):  # Dosya mevcutsa:
                stat_info = os.stat(path)  # Dosya sisteminden bilgi al.
                file_info = {
                    'size': stat_info.st_size,  # Dosya boyutu.
                    'created': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),  # Oluşturulma zamanı.
                    'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),  # Son değiştirilme zamanı.
                    'permissions': oct(stat_info.st_mode)[-3:],  # Dosya izinleri (örneğin 644).
                }
                if os.path.isfile(path):  # Eğer dosya bir klasör değilse:
                    with open(path, 'rb') as f:
                        file_info['md5'] = hashlib.md5(f.read()).hexdigest()  # Dosyanın MD5 hash değeri.
                return file_info  # Dosya bilgilerini döndür.
        except Exception as e:
            return {'error': str(e)}  # Hata durumunda hata mesajı döndür.
        return None

    def should_log_event(self, event_type, path):
        """Bir olayın loglanıp loglanmayacağını kontrol et."""
        last_event = self.last_event.get(path)  # İlgili dosya için son olay bilgisi.
        if last_event and last_event["event_type"] == "file_created" and event_type == "file_modified":
            return False  # Eğer dosya yeni oluşturulmuşsa ve ardından değiştirilmişse bu loglanmaz.
        return True  # Aksi durumda loglanabilir.

    def log_event(self, event_type, path, details=None, source_path=None, dest_path=None):
        """Bir olayı logla."""
        if not self.should_log_event(event_type, path):  # Eğer olay loglanmamalıysa:
            return  # İşlemi sonlandır.
        log_entry = {
            'timestamp': datetime.now().isoformat(),  # Olayın gerçekleştiği zaman.
            'event_type': event_type,  # Olay türü (örneğin, file_created).
            'path': path,  # Etkilenen dosyanın yolu.
        }
        if details:  # Eğer detay bilgisi varsa:
            log_entry['details'] = details  # Detay bilgisi ekle.
        if source_path and dest_path:  # Eğer taşınma olayıysa:
            log_entry['source_path'] = source_path  # Eski yol.
            log_entry['destination_path'] = dest_path  # Yeni yol.
        self.last_event[path] = log_entry  # Son olay bilgilerini güncelle.
        self._write_log(log_entry)  # Olayı log dosyasına yaz.

    def on_created(self, event):
        """Bir dosya veya klasör oluşturulduğunda çalıştırılır."""
        self.log_event('folder_created' if event.is_directory else 'file_created', event.src_path, self._get_file_info(event.src_path))

    def on_deleted(self, event):
        """Bir dosya veya klasör silindiğinde çalıştırılır."""
        self.log_event('folder_deleted' if event.is_directory else 'file_deleted', event.src_path)

    def on_modified(self, event):
        """Bir dosya değiştirildiğinde çalıştırılır."""
        if not event.is_directory:  # Sadece dosyalar için çalıştırılır.
            self.log_event('file_modified', event.src_path, self._get_file_info(event.src_path))

    def on_moved(self, event):
        """Bir dosya veya klasör taşındığında çalıştırılır."""
        self.log_event('folder_moved' if event.is_directory else 'file_moved', event.dest_path, self._get_file_info(event.dest_path), source_path=event.src_path, dest_path=event.dest_path)


def main():
    # İzlenecek klasör ve log dosyasının yolu tanımlanır.
    watch_path = "/home/mtg/bsm/test"
    log_path = "/home/mtg/bsm/logs/changes.json"
    os.makedirs(watch_path, exist_ok=True)  # İzlenecek klasör yoksa oluşturulur.
    event_handler = ChangeHandler(log_path)  # Event handler (olay işleyici) oluşturulur.
    observer = Observer()  # Observer (gözlemci) başlatılır.
    observer.schedule(event_handler, watch_path, recursive=True)  # Klasör izleme başlatılır.

    try:
        while True:
            time.sleep(1)  # Programın sürekli çalışmasını sağlar.
    except KeyboardInterrupt:
        observer.stop()  # Program durdurulduğunda gözlemciyi durdur.
    observer.join()  # Gözlemci işlemini sonlandır.


if __name__ == "__main__":
    main()  # Programın ana fonksiyonu çalıştırılır.
