
# **Directory Monitor Service**

Bu proje, belirli bir dizini izleyerek dosya ekleme, silme veya değiştirme gibi olayları tespit eder ve bu değişiklikleri JSON formatında bir log dosyasına kaydeder. Bu servisin çalışması Linux ortamında `systemd` servisi olarak yapılandırılmıştır. Proje aşağıdaki adımları takip ederek kurulum ve çalıştırma işlemleri için gereksinim duyulacak adımları içerir.

## **Özellikler**
- Bir dizini izler (örneğin, `/home/ubuntu/bsm/test`).
- Dosya oluşturma, silme, değiştirme gibi değişiklikleri takip eder.
- Bu değişiklikleri `/home/ubuntu/bsm/logs/changes.json` dosyasına JSON formatında kaydeder.
- Linux üzerinde `systemd` servisi olarak yapılandırılmıştır.
- Sistem yeniden başlatıldığında otomatik olarak başlatılır.

## **Kurulum Adımları**

### 1. **Yeni bir Sanal Makine Oluşturun (İsteğe Bağlı)**
Projenizi izole bir ortamda çalıştırmak için sanal bir makine oluşturabilirsiniz. VirtualBox, VMware veya KVM gibi araçlar kullanabilirsiniz.

### 2. **Python Kurulumu Yapın**
Linux sisteminizde Python 3.8 veya daha güncel bir sürümün kurulu olduğundan emin olun. Ayrıca, gerekli Python kütüphanelerini yüklemek için `pip` aracını kullanabilirsiniz.

#### Python Kurulum:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 3. **Gerekli Python Kütüphanelerini Yükleyin**
Projenin çalışması için `watchdog` kütüphanesine ihtiyacınız olacak. Bu kütüphaneyi aşağıdaki komut ile yükleyebilirsiniz:

```bash
pip install watchdog
```

### 4. **Log Dizinini Oluşturun**
Değişikliklerin kaydedileceği log dosyaları için `/home/ubuntu/bsm/logs` dizinini oluşturun.

```bash
mkdir -p /home/ubuntu/bsm/logs
```

### 5. **Python Scripti Yazın**
Bir Python scripti oluşturarak, belirlenen dizindeki dosya değişikliklerini takip edin. Script aşağıdaki gibi olacaktır:

**directory_monitor.py** dosyasının içeriğini kullanarak bu adımı tamamlayabilirsiniz.

### 6. **Systemd Servisi Oluşturun**
Scripti bir sistem servisi olarak çalıştırabilmek için `systemd` servisi oluşturmalısınız. Aşağıdaki servis dosyasını `/etc/systemd/system/` dizinine kaydedin.

**directory-monitor.service**:
```ini
[Unit]
Description=Directory Monitor Service
After=network.target

[Service]
Type=simple
User=mtg
Group=mtg
WorkingDirectory=/home/mtg/bsm
ExecStart=/usr/bin/python3 /home/mtg/bsm/directory_monitor.py
Restart=always
RestartSec=3
StandardOutput=append:/home/mtg/bsm/logs/service.log
StandardError=append:/home/mtg/bsm/logs/service.log

[Install]
WantedBy=multi-user.target
```

Servisi aktif etmek için:

```bash
sudo systemctl daemon-reload
sudo systemctl enable directory-monitor.service
sudo systemctl start directory-monitor.service
```

### 7. **Servisi Kontrol Etme**
Servisin çalıştığını kontrol etmek için aşağıdaki komutu kullanabilirsiniz:

```bash
sudo systemctl status directory-monitor.service
```

### 8. **Log Dosyasını Görüntüleme**
Servisin oluşturduğu logları `/home/mtg/bsm/logs/service.log` dosyasından takip edebilirsiniz.

### 9. **Servisi Durdurma ve Yeniden Başlatma**
Servisi durdurmak veya yeniden başlatmak için şu komutları kullanabilirsiniz:

```bash
sudo systemctl stop directory-monitor.service
sudo systemctl restart directory-monitor.service
```

## **Notlar**
- Eğer servisin doğru çalışmadığını düşünüyorsanız, `journalctl` komutunu kullanarak sistem loglarını inceleyebilirsiniz:

```bash
sudo journalctl -u directory-monitor.service
```

Bu adımlar projenin kurulumu ve çalıştırılması için gereklidir.
