import mido

print("Puertos MIDI de salida disponibles:")
for port in mido.get_output_names():
    print(f"- {port}")
