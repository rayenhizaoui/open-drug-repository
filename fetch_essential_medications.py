import json
import urllib.request
import urllib.parse
import urllib.error
import time

def fetch_essential_medications():
    """
    Script pour récupérer automatiquement les 1000 médicaments les plus fréquents 
    de la base de données de la FDA. Il fait appel à la fonction 'count' d'OpenFDA
    qui contient des médicaments internationaux vendus partout (France, US...), 
    car OpenFDA recense non seulement les composés (Paracetamol/Acetaminophen),
    mais aussi toutes les marques déposées par divers laboratoires globaux.
    """
    output_file = 'medications_essential.json'
    max_items = 1000 # La limite max de la fonction count d'OpenFDA est 1000
    
    print(f"Étape 1 : Demande du Top {max_items} des médicaments les plus fréquents (Noms de molécules internationales)...\n")
    
    # 1. On demande dynamiquement à l'API de classer les 1000 noms génériques les plus répertoriés
    count_url = f"https://api.fda.gov/drug/ndc.json?count=generic_name.exact&limit={max_items}"
    top_medications = []
    
    try:
        req = urllib.request.Request(count_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            results = data.get('results', [])
            # L'API renvoie des objets de type : {"term": "ACETAMINOPHEN", "count": 4531}
            # Nous convertissons en chaîne de caractères simple
            top_medications = [item['term'] for item in results if item.get('term')]
    except Exception as e:
        print(f"Erreur fatale lors du classement du Top {max_items} : {e}")
        return
        
    print(f"Succès ! Les {len(top_medications)} noms fréquents ont été classés.")
    print("Étape 2 : Récupération des informations détaillées pour chaque molécule.")
    print("Veuillez patienter... (Temps estimé pour 1000: environ 15 à 20 minutes pour éviter le ban API).\n")
    
    results_data = []
    
    # 2. On boucle sur ce Top 1000 pour chercher le détail (classes, routes, types...)
    for i, med_name in enumerate(top_medications):
        query = urllib.parse.quote(f'generic_name.exact:"{med_name}"')
        url = f"https://api.fda.gov/drug/ndc.json?search={query}&limit=1"
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
                records = data.get('results', [])
                if records:
                    item = records[0]
                    # Convertir en liste si ce n'est pas déjà le cas pour iterer facilement
                    brand_names = item.get('brand_name', 'N/A')
                    if isinstance(brand_names, str):
                        brand_names = [brand_names.strip()]
                    
                    # On stocke toutes les marques trouvées (ex: Doliprane, Tylenol...)
                    clean_brand_names = []
                    for brand in brand_names:
                        b = brand.strip().capitalize()
                        if b and b not in clean_brand_names:
                            clean_brand_names.append(b)
                            
                    # Pour assurer une bonne détection NLP (Machine Learning/OCR en Tunisie par ex),
                    # on ajoute de force quelques noms de marques extrêmement fréquents 
                    # en Tunisie et en France liés à certaines molécules.
                    molecule = clean_name.lower()
                    tunisian_french_equivalents = []
                    
                    if "acetaminophen" in molecule or "paracetamol" in molecule:
                        tunisian_french_equivalents = ["Doliprane", "Efferalgan", "Dafalgan", "Panadol", "Novacetol", "Analgan"]
                    elif "ibuprofen" in molecule:
                        tunisian_french_equivalents = ["Advil", "Nurofen", "Spedifen", "Brufen", "Upfen"]
                    elif "amoxicillin" in molecule:
                        tunisian_french_equivalents = ["Clamoxyl", "Augmentin", "Amodex"]
                    elif "metformin" in molecule:
                        tunisian_french_equivalents = ["Glucophage", "Stagid", "Metformine"]
                    elif "omeprazole" in molecule:
                        tunisian_french_equivalents = ["Mopral", "Zoltum"]
                    elif "azithromycin" in molecule:
                        tunisian_french_equivalents = ["Zithromax", "Azithromycine"]
                        
                    # On fusionne avec la liste globale
                    # Cela aidera votre programme OCR/Reconnaissance à identifier les noms locaux
                    for local_brand in tunisian_french_equivalents:
                        if local_brand not in clean_brand_names:
                            clean_brand_names.append(local_brand)

                    results_data.append({
                        "id": i + 1,
                        "name": clean_name,
                        "international_brands": clean_brand_names,
                        "type": item.get('product_type', 'N/A'),
                        "dosage_form": item.get('dosage_form', 'N/A'),
                        "routes": item.get('route', []),
                        "pharm_class": item.get('pharm_class', [])
                    })
                    print(f"[{i+1}/{len(top_medications)}] {clean_name} classé avec {len(clean_brand_names)} marques associées.")
                else:
                    print(f"[{i+1}/{len(top_medications)}] Impossible de détailler {med_name}.")
                    
        except urllib.error.HTTPError as e:
            if e.code == 429: # Si Rate Limiting
                print("L'API signale 'Too Many Requests'. Pause de 10s...")
                time.sleep(10)
            else:
                pass # On ignore les petites erreurs ponctuelles
                
        # Pause obligatoire d'une seconde. L'API jette ceux qui font > 40 req/minute
        time.sleep(1.0)

    # 3. Sauvegarde sur le disque
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, indent=2, ensure_ascii=False)
        
    print(f"\nIncroyable ! Le top des {len(results_data)} médicaments fréquents a été généré sur {output_file}")

if __name__ == "__main__":
    fetch_essential_medications()