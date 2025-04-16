from typing import Dict
import csv
import io

class CSVExporter:
    @staticmethod
    def generate_csv(product_data: Dict) -> str:
        """
        Generate CSV from product data
        """
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        # Write header
        header = [
            'VaterartikelNr',
            'cHAN',
            'fLagerbestandeigen',
            'cbarcode',
            'cArtNr',
            'cName',
            'cBeschreibung',
            'cFirma',
            'cHerstellerName',
            'Attributgruppe',
            'Attributname',
            'Attributwert',
            'Shopaktiv',
            'Shop',
            'IstVaterArtikel',
            'kVaterartikel'
        ]
        writer.writerow(header)
        
        # Write product data
        row = [
            product_data.get('artikelnummer', ''),  # VaterartikelNr
            '',  # cHAN
            '1',  # fLagerbestandeigen
            '',  # cbarcode
            product_data.get('artikelnummer', ''),  # cArtNr
            product_data.get('name', ''),  # cName
            product_data.get('details', ''),  # cBeschreibung
            'Blutsgeschwister',  # cFirma
            'Blutsgeschwister',  # cHerstellerName
            'Größe',  # Attributgruppe
            'Größe',  # Attributname
            ', '.join(product_data.get('groessen', [])),  # Attributwert
            '1',  # Shopaktiv
            'Blutsgeschwister',  # Shop
            '1',  # IstVaterArtikel
            ''  # kVaterartikel
        ]
        writer.writerow(row)
        
        # Get the CSV content
        csv_content = output.getvalue()
        output.close()
        
        return csv_content
