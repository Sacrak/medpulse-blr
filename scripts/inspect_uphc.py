import xml.etree.ElementTree as ET

KML_FILE = "data/raw/uphc_hospitals.kml"

root = ET.parse(KML_FILE).getroot()

ns = {
    "k": "http://www.opengis.net/kml/2.2"
}

placemarks = root.findall(".//k:Placemark", ns)

print("First 20 UPHC records:\n")

for placemark in placemarks[:20]:

    def get_field(field):
        element = placemark.find(
            f".//k:SimpleData[@name='{field}']",
            ns
        )

        if element is None or element.text is None:
            return ""

        return element.text.strip()

    print(
        f"UPHC: {get_field('UPHC')}"
    )
    print(
        f"Ward: {get_field('ward')}"
    )
    print(
        f"Zone: {get_field('Zone')}"
    )
    print(
        f"Latitude: {get_field('Lattitude')}"
    )
    print(
        f"Longitude: {get_field('Longitude')}"
    )
    print("-" * 50)