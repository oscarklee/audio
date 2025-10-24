# 🎧 Nothing Ear (open) + PipeWire AAC - Guía Rápida

**Sistema:** Jetson Orin Nano  
**PipeWire:** 0.3.48 (compilado con AAC)  
**Última actualización:** 19 Oct 2025

---

## ⚡ Comandos Rápidos

### Conectar Audífonos
```bash
bluetoothctl connect 3C:B0:ED:52:00:0C
```

### Cambiar a Perfil AAC
```bash
pactl set-card-profile bluez_card.3C_B0_ED_52_00_0C a2dp-sink-aac
```

### Otros Perfiles Disponibles
```bash
# SBC-XQ (máxima calidad, mayor latencia)
pactl set-card-profile bluez_card.3C_B0_ED_52_00_0C a2dp-sink-sbc_xq

# SBC estándar (mejor estabilidad a distancia)
pactl set-card-profile bluez_card.3C_B0_ED_52_00_0C a2dp-sink

# SBC explícito
pactl set-card-profile bluez_card.3C_B0_ED_52_00_0C a2dp-sink-sbc
```

### Configurar como Salida Predeterminada
```bash
pactl set-default-sink bluez_output.3C_B0_ED_52_00_0C.a2dp-sink
```

### Verificar Estado
```bash
# Ejecutar script de verificación
./verify_aac_support.sh

# Ver perfil activo
pactl list cards | grep "Active Profile"

# Ver calidad de audio
pactl list sinks | grep "Sample Specification"
```

---

## 📊 Comparación de Códecs

| Perfil | Códec | Calidad | Latencia | Uso Recomendado |
|--------|-------|---------|----------|-----------------|
| `a2dp-sink` | SBC | ⭐⭐⭐⭐ | ~40ms | Distancia (4-5m) |
| `a2dp-sink-sbc` | SBC | ⭐⭐⭐⭐ | ~45ms | General |
| `a2dp-sink-sbc_xq` | SBC-XQ | ⭐⭐⭐⭐⭐ | ~70ms | Cerca (<2m) |
| `a2dp-sink-aac` | AAC | ⭐⭐⭐⭐⭐ | ~50ms | **Música** ⭐ |

---

## 📁 Documentación Completa

- **`AAC_SETUP_SUCCESS.md`** - Proceso completo de compilación e instalación
- **`BLUETOOTH_AUDIO_TROUBLESHOOTING.md`** - Troubleshooting histórico
- **`verify_aac_support.sh`** - Script de verificación de sistema

---

## 🔧 Información Técnica

### Módulo AAC
```
/usr/lib/aarch64-linux-gnu/spa-0.2/bluez5/libspa-codec-bluez5-aac.so
```

### Configuración
```
~/.config/pipewire/pipewire.conf.d/99-bluetooth-aac.conf
~/.config/pipewire/pipewire-pulse.conf.d/99-bluetooth-aac.conf
```

### Verificar Versión
```bash
pw-cli --version
# Compiled with libpipewire 0.3.48
# Linked with libpipewire 0.3.48
```

---

## ✅ Estado Actual

- ✅ PipeWire 0.3.48 con soporte AAC
- ✅ Perfiles disponibles: SBC, SBC-XQ, AAC
- ✅ Audio estéreo 48kHz
- ✅ Configuración persistente

---

**Creado:** 19 Oct 2025  
**Estado:** ✅ Completamente funcional
