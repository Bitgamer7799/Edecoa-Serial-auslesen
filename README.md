Dieses P?rogramm habe ich entwickelt, damit ich meine Edecoa EM-161A Wechselrichter über Serial auslesen kann um die Daten in Grafana zu übertragen.
Man muss die folgenden Libarys über pip installiern: serial((Windows: python -m pip install PySerial, Linux: pip install PySerial)
Die Cooamds findet man auf folgender Seite: https://www.photovoltaikforum.com/core/attachment/193347-voltronic-power-rs232-communication-protocol-for-infinisolare5-5kw-v1-0-pdf/
Der wichtigste Command ist QPIGS, da er zum auslesen des Wechselrichtzers dient.
