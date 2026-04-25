import json
import urllib.request
import urllib.parse
import urllib.error
import time

def fetch_essential_medications():
    """
    Script pour récupérer des données détaillées uniquement sur les médicaments
    les plus fréquents ou "essentiels" (Le top des médicaments les plus prescrits/utilisés).
    Il interroge l'API OpenFDA pour enrichir cette liste.
    """
    # Liste ciblée des médicaments grand public les plus courants (Top 50 mondial/américain)
    top_medications = [
        "Acetaminophen", "Ibuprofen", "Amoxicillin", "Aspirin", "Omeprazole",
        "Metformin", "Atorvastatin", "Amlodipine", "Albuterol", "Diazepam",
        "Simvastatin", "Lisinopril", "Levothyroxine", "Azithromycin", "Metoprolol",
        "Pantoprazole", "Losartan", "Gabapentin", "Sertraline", "Furosemide",
        "Fluticasone", "Tramadol", "Citalopram", "Meloxicam", "Montelukast",
        "Trazodone", "Escitalopram", "Pravastatin", "Bupropion", "Fluoxetine",
        "Carvedilol", "Prednisone", "Tamsulosin", "Clopidogrel", "Ciprofloxacin",
        "Duloxetine", "Warfarin", "Rosuvastatin", "Venlafaxine", "Lorazepam",
        "Estradiol", "Cyclobenzaprine", "Hydrochlorothiazide", "Clonazepam",
        "Cephalexin", "Quetiapine", "Zolpidem", "Ranitidine", "Atenolol"
    ]
    
    results_data = []
    output_file = 'medications_essential.json'
    
    print(f"Début de la récupération pour {len(top_medications)} médicaments très fréquents...\n")
    
    for i, med_name in enumerate(top_medications):
        # Formatage de l'URL pour chercher spécifiquement ce médicament
        query = urllib.parse.quote(f'generic_name:"{med_name}"')
        url = f"https://api.fda.gov/drug/ndc.json?search={query}&limit=1"
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
                records = data.get('results', [])
                if records:
                    item = records[0] # On prend le premier résultat pertinent
                    
                    results_data.append({
                        "id": i + 1,
                        "name": med_name.capitalize(),
                        "brand_name": item.get('brand_name', 'N/A').strip(),
                        "type": item.get('product_type', 'HUMAN PRESCRIPTION DRUG'),
                        "dosage_form": item.get('dosage_form', 'N/A'),
                        "routes": item.get('route', []),
                        "pharm_class": item.get('pharm_class', [])
                    })
                    print(f"[OK] {med_name} récupéré.")
                else:
                    print(f"[-] {med_name} : Aucune donnée détaillée trouvée.")
                    
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"[-] {med_name} introuvable dans OpenFDA.")
            else:
                print(f"[!] Erreur API pour {med_name} ({e.code})")
        except Exception as e:
            print(f"[!] Erreur générique pour {med_name} : {e}")
            
        # Pause pour éviter de saturer l'API
        time.sleep(0.5)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, indent=2, ensure_ascii=False)
        
    print(f"\nSuccès ! {len(results_data)} médicaments essentiels/fréquents sauvés dans {output_file}")

if __name__ == "__main__":
    fetch_essential_medications()