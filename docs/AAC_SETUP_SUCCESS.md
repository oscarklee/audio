# ✅ Habilitación Exitosa de Códec AAC en PipeWire 0.3.48

**Fecha:** 19 de Octubre, 2025  
**Sistema:** NVIDIA Jetson Orin Nano + Ubuntu Linux 5.15.148-tegra  
**Audífonos:** Nothing Ear (open) - MAC: 3C:B0:ED:52:00:0C  
**PipeWire:** 0.3.48 (compilado desde fuente con soporte AAC)

---

## 🎯 Objetivo Completado

Se compiló e instaló exitosamente PipeWire 0.3.48 con soporte para el códec **AAC (Advanced Audio Coding)**, permitiendo que los audífonos Nothing Ear (open) utilicen este códec de mayor calidad.

---

## 📋 Resumen de lo Realizado

### 1. Descarga del Código Fuente
```bash
cd /home/oscarklee/dev/bt-speakers
wget https://gitlab.freedesktop.org/pipewire/pipewire/-/archive/0.3.48/pipewire-0.3.48.tar.gz
tar -xzf pipewire-0.3.48.tar.gz
```

### 2. Verificación de Dependencias
```bash
# libfdk-aac-dev ya estaba instalado
sudo apt install libfdk-aac-dev
```

### 3. Configuración de la Compilación
```bash
cd pipewire-0.3.48
meson setup build \
  --prefix=/usr \
  --libdir=/usr/lib/aarch64-linux-gnu \
  --sysconfdir=/etc \
  -Dbuildtype=release \
  -Dbluez5=enabled \
  -Dbluez5-codec-aac=enabled \      # ✅ AAC HABILITADO
  -Dbluez5-codec-ldac=disabled \
  -Dalsa=enabled \
  -Dpipewire-alsa=enabled \
  -Dsystemd=enabled \
  -Dsystemd-system-service=enabled \
  -Dsystemd-user-service=enabled \
  -Dudevrulesdir=/lib/udev/rules.d
```

**Confirmación del build:**
```
Bluetooth audio codecs
    SBC                                     : YES
    LDAC                                    : NO
    LDAC ABR                                : NO
    aptX                                    : NO
    AAC                                     : YES  ✅
```

### 4. Compilación e Instalación
```bash
cd build
ninja -j4
sudo ninja install
```

### 5. Configuración de PipeWire
Archivos creados:

**`~/.config/pipewire/pipewire.conf.d/99-bluetooth-aac.conf`**
```conf
context.properties = {
    bluez5.codecs = [ sbc sbc_xq aac ldac aptx aptx_hd aptx_ll aptx_ll_duplex faststream faststream_duplex ]
    bluez5.default.rate = 48000
    bluez5.default.channels = 2
    
    default.clock.rate = 48000
    default.clock.quantum = 1024
    default.clock.min-quantum = 32
    default.clock.max-quantum = 2048
}
```

**`~/.config/pipewire/pipewire-pulse.conf.d/99-bluetooth-aac.conf`**
```conf
pulse.properties = {
    bluez5.enable-sbc-xq = true
    bluez5.enable-msbc = true
    bluez5.enable-hw-volume = true
    bluez5.headset-roles = [ hsp_hs hfp_hf ]
    bluez5.auto-connect = [ a2dp_sink ]
    bluez5.hfp-offload-sco = true
}
```

### 6. Reinicio de Servicios
```bash
systemctl --user daemon-reload
systemctl --user restart pipewire wireplumber pipewire-pulse
```

---

## ✅ Verificación de Funcionamiento

### Módulo AAC Instalado
```bash
$ ls -la /usr/lib/aarch64-linux-gnu/spa-0.2/bluez5/ | grep aac
-rwxr-xr-x  1 root root  35592 Oct 19 21:08 libspa-codec-bluez5-aac.so
```

### Perfiles A2DP Disponibles
```bash
$ pactl list cards | grep -A 30 "bluez_card"
Profiles:
    a2dp-sink: High Fidelity Playback (A2DP Sink)
    a2dp-sink-sbc: High Fidelity Playback (A2DP Sink, codec SBC)
    a2dp-sink-sbc_xq: High Fidelity Playback (A2DP Sink, codec SBC-XQ)
    a2dp-sink-aac: High Fidelity Playback (A2DP Sink, codec AAC) ✅
    headset-head-unit: Headset Head Unit (HSP/HFP)
    
Active Profile: a2dp-sink-aac ✅
```

### Calidad de Audio
```bash
$ pactl list sinks | grep "Sample Specification"
Sample Specification: s16le 2ch 48000Hz
```
**Estéreo 48kHz** - Calidad completa A2DP con AAC

---

## 🎵 Uso del Perfil AAC

### Cambiar al Perfil AAC
```bash
pactl set-card-profile bluez_card.3C_B0_ED_52_00_0C a2dp-sink-aac
```

### Configurar como Salida Predeterminada
```bash
pactl set-default-sink bluez_output.3C_B0_ED_52_00_0C.a2dp-sink
```

### Verificar Perfil Activo
```bash
pactl list cards | grep "Active Profile"
# Active Profile: a2dp-sink-aac
```

---

## 📊 Comparación de Códecs

| Códec | Bitrate | Calidad | Latencia | Compatibilidad |
|-------|---------|---------|----------|----------------|
| **SBC** | ~328 kbps | ⭐⭐⭐⭐ | ~40ms | Universal |
| **SBC-XQ** | ~552 kbps | ⭐⭐⭐⭐⭐ | ~70ms | Amplia |
| **AAC** | ~256 kbps | ⭐⭐⭐⭐⭐ | ~50ms | iOS/Android |

**AAC ofrece:**
- ✅ Mejor eficiencia de compresión que SBC
- ✅ Menor bitrate con calidad similar
- ✅ Menor latencia que SBC-XQ
- ✅ Excelente para contenido musical

---

## 🛠️ Script de Verificación

Se creó el script `verify_aac_support.sh` que muestra:
- ✅ Versión de PipeWire
- ✅ Módulo AAC instalado
- ✅ Estado de servicios
- ✅ Perfiles disponibles
- ✅ Perfil activo
- ✅ Calidad de audio

**Uso:**
```bash
./verify_aac_support.sh
```

---

## 🎯 Perfiles Disponibles Post-Compilación

### A2DP (Alta Fidelidad)
- **a2dp-sink** - A2DP básico (SBC estándar)
- **a2dp-sink-sbc** - A2DP con SBC explícito
- **a2dp-sink-sbc_xq** - A2DP con SBC de alta calidad
- **a2dp-sink-aac** - A2DP con AAC ⭐ **NUEVO**

### HSP/HFP (Llamadas)
- **headset-head-unit** - HSP/HFP genérico
- **headset-head-unit-cvsd** - HSP/HFP con códec CVSD
- **headset-head-unit-msbc** - HSP/HFP con códec mSBC

---

## 💡 Recomendaciones de Uso

### Para Música (Alta Calidad)
```bash
# Opción 1: AAC (recomendado para Nothing Ear)
pactl set-card-profile bluez_card.3C_B0_ED_52_00_0C a2dp-sink-aac

# Opción 2: SBC-XQ (máxima calidad, mayor latencia)
pactl set-card-profile bluez_card.3C_B0_ED_52_00_0C a2dp-sink-sbc_xq
```

### Para Distancia (4-5 metros)
```bash
# SBC estándar (mejor estabilidad)
pactl set-card-profile bluez_card.3C_B0_ED_52_00_0C a2dp-sink
```

### Para Llamadas
```bash
# HSP/HFP automático al iniciar llamada
# No requiere cambio manual
```

---

## 🔄 Persistencia Post-Reinicio

La configuración persiste después de reiniciar gracias a:
- ✅ PipeWire 0.3.48 instalado en `/usr/`
- ✅ Módulo AAC en `/usr/lib/aarch64-linux-gnu/spa-0.2/bluez5/`
- ✅ Configuraciones en `~/.config/pipewire/`
- ✅ Servicios systemd configurados

**Pasos post-reinicio:**
1. Conectar audífonos: `bluetoothctl connect 3C:B0:ED:52:00:0C`
2. Cambiar a AAC: `pactl set-card-profile bluez_card.3C_B0_ED_52_00_0C a2dp-sink-aac`
3. (Opcional) Configurar como default: `pactl set-default-sink bluez_output.3C_B0_ED_52_00_0C.a2dp-sink`

---

## 📁 Archivos Relevantes

### Binarios
- `/usr/lib/aarch64-linux-gnu/spa-0.2/bluez5/libspa-codec-bluez5-aac.so`
- `/usr/bin/pipewire` (0.3.48)
- `/usr/bin/pw-cli` (0.3.48)

### Configuración
- `~/.config/pipewire/pipewire.conf.d/99-bluetooth-aac.conf`
- `~/.config/pipewire/pipewire-pulse.conf.d/99-bluetooth-aac.conf`

### Scripts
- `/home/oscarklee/dev/bt-speakers/verify_aac_support.sh`

### Código Fuente
- `/home/oscarklee/dev/bt-speakers/pipewire-0.3.48/`

---

## ✅ Estado Final

- ✅ **PipeWire 0.3.48** compilado con soporte AAC
- ✅ **Módulo libspa-codec-bluez5-aac.so** instalado
- ✅ **Perfil a2dp-sink-aac** disponible y funcional
- ✅ **Nothing Ear (open)** usando AAC activamente
- ✅ **Audio estéreo 48kHz** confirmado
- ✅ **Configuración persistente** implementada

---

## 🎉 Conclusión

La compilación e instalación de PipeWire 0.3.48 con soporte AAC fue **completamente exitosa**. Los audífonos Nothing Ear (open) ahora pueden usar el códec AAC para reproducción de audio de alta calidad, manteniendo la compatibilidad con SBC y SBC-XQ para otros escenarios de uso.

---

**Compilado y verificado:** 19 de Octubre, 2025  
**Sistema:** Jetson Orin Nano  
**Estado:** ✅ COMPLETAMENTE FUNCIONAL
