# Bluetooth Speakers - PipeWire AAC Support

Sistema de audio Bluetooth con soporte para códec AAC en Jetson Orin Nano.

## 🎯 Estado Actual

✅ **PipeWire 0.3.48** compilado con soporte AAC  
✅ **Nothing Ear (open)** funcionando con perfil AAC  
✅ **Audio estéreo 48kHz** de alta calidad  

## 📚 Documentación

| Archivo | Descripción |
|---------|-------------|
| `AAC_SETUP_SUCCESS.md` | Guía completa de compilación e instalación |
| `QUICK_REFERENCE.md` | Referencia rápida de comandos |
| `BLUETOOTH_AUDIO_TROUBLESHOOTING.md` | Troubleshooting histórico completo |
| `STATUS.txt` | Resumen visual del estado actual |
| `verify_aac_support.sh` | Script de verificación del sistema |

## ⚡ Inicio Rápido

### Conectar y Usar AAC

```bash
# 1. Conectar audífonos
bluetoothctl connect 3C:B0:ED:52:00:0C

# 2. Cambiar a perfil AAC
pactl set-card-profile bluez_card.3C_B0_ED_52_00_0C a2dp-sink-aac

# 3. Configurar como salida predeterminada
pactl set-default-sink bluez_output.3C_B0_ED_52_00_0C.a2dp-sink

# 4. Verificar estado
./verify_aac_support.sh
```

## 🎵 Perfiles Disponibles

- **a2dp-sink-aac** - AAC (recomendado para música) ⭐
- **a2dp-sink-sbc_xq** - SBC-XQ (máxima calidad SBC)
- **a2dp-sink-sbc** - SBC estándar
- **a2dp-sink** - SBC básico (mejor para distancia)

## 🔧 Sistema

- **OS:** Ubuntu 22.04 (Jetson Orin Nano)
- **PipeWire:** 0.3.48 (compilado)
- **WirePlumber:** 0.4.8
- **BlueZ:** 5.64
- **Dispositivo:** Nothing Ear (open) - 3C:B0:ED:52:00:0C

## 📝 Fecha

Última actualización: 19 de Octubre, 2025

---

✅ Sistema completamente funcional y documentado
