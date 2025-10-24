#!/bin/bash
# Script de verificación de soporte AAC en PipeWire 0.3.48

echo "════════════════════════════════════════════════════════════════"
echo "   VERIFICACIÓN DE SOPORTE AAC PARA NOTHING EAR (OPEN)"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Verificar versión de PipeWire
echo "📦 Versión de PipeWire:"
pw-cli --version | head -2
echo ""

# Verificar módulo AAC instalado
echo "🔧 Módulo codec AAC:"
if [ -f "/usr/lib/aarch64-linux-gnu/spa-0.2/bluez5/libspa-codec-bluez5-aac.so" ]; then
    ls -lh /usr/lib/aarch64-linux-gnu/spa-0.2/bluez5/libspa-codec-bluez5-aac.so
    echo "✅ Módulo AAC instalado correctamente"
else
    echo "❌ Módulo AAC NO encontrado"
fi
echo ""

# Verificar servicios activos
echo "🔄 Estado de servicios:"
systemctl --user is-active pipewire wireplumber pipewire-pulse | \
    awk '{print "  - " (NR==1?"PipeWire: ":NR==2?"WirePlumber: ":"PipeWire-Pulse: ") $0}'
echo ""

# Verificar configuración de códecs
echo "⚙️  Configuración de códecs Bluetooth:"
if grep -q "aac" ~/.config/pipewire/pipewire.conf.d/99-bluetooth-aac.conf 2>/dev/null; then
    echo "  ✅ Configuración AAC encontrada en ~/.config/pipewire/"
else
    echo "  ⚠️  Configuración AAC no encontrada"
fi
echo ""

# Verificar dispositivos Bluetooth emparejados
echo "📱 Dispositivos Bluetooth emparejados:"
bluetoothctl paired-devices | grep "3C:B0:ED:52:00:0C" && \
    echo "  ✅ Nothing Ear (open) emparejados" || \
    echo "  ⚠️  Nothing Ear (open) NO emparejados"
echo ""

# Verificar conexión
echo "🔗 Estado de conexión:"
if bluetoothctl info 3C:B0:ED:52:00:0C 2>/dev/null | grep -q "Connected: yes"; then
    echo "  ✅ Nothing Ear (open) CONECTADOS"
    echo ""
    
    # Mostrar perfiles disponibles
    echo "🎧 Perfiles de audio disponibles:"
    pactl list cards | grep -A 30 "bluez_card.3C_B0_ED_52_00_0C" | grep -E "(Profile|a2dp|aac)" | sed 's/^/  /'
    echo ""
    
    # Mostrar perfil activo
    echo "🎵 Perfil activo actual:"
    pactl list cards | grep -A 30 "bluez_card.3C_B0_ED_52_00_0C" | grep "Active Profile" | sed 's/^/  /'
    echo ""
    
    # Verificar sink disponible
    echo "🔊 Audio sink disponible:"
    pactl list sinks short | grep "bluez" | sed 's/^/  /'
    echo ""
    
    # Verificar calidad de audio
    echo "📊 Calidad de audio:"
    pactl list sinks | grep -A 15 "bluez.*a2dp" | grep "Sample Specification" | sed 's/^/  /'
    
else
    echo "  ❌ Nothing Ear (open) NO conectados"
    echo ""
    echo "💡 Para conectar, ejecuta:"
    echo "   bluetoothctl connect 3C:B0:ED:52:00:0C"
fi
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "📝 CÓDECS ESPERADOS CON AAC HABILITADO:"
echo "════════════════════════════════════════════════════════════════"
echo "  • a2dp-sink           - A2DP básico (SBC)"
echo "  • a2dp-sink-sbc       - A2DP con SBC estándar"
echo "  • a2dp-sink-sbc_xq    - A2DP con SBC de alta calidad"
echo "  • a2dp-sink-aac       - A2DP con AAC ⭐ NUEVO"
echo ""
echo "💡 Para cambiar al perfil AAC cuando esté conectado:"
echo "   pactl set-card-profile bluez_card.3C_B0_ED_52_00_0C a2dp-sink-aac"
echo ""
echo "💡 Para configurar como salida predeterminada:"
echo "   pactl set-default-sink bluez_output.3C_B0_ED_52_00_0C.a2dp-sink"
echo "════════════════════════════════════════════════════════════════"
