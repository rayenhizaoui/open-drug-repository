import json
import urllib.request
import urllib.error
import time
import os

def fetch_medications():
    """
    Script optimisé pour de gros volumes.
    Utilise un "set" pour des performances éclair et gère mieux les données.
    """
    output_file = 'medications_full.json'
    state_file = 'fetch_state.txt'
    
    medications = []
    seen_names = set() # OPTIMISATION MAJEURE : Les vérifications de doublons se feront instantanément
    
    skip = 0
    limit = 100
    fetch_amount = 5000 
    
    # 1. Charger les médicaments déjà récupérés
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                medications = json.load(f)
                
            # Peupler le "set" pour une vérification ultra-rapide
            for m in medications:
                seen_names.add(m['name'].lower())
                
            print(f"Fichier existant trouvé: {len(medications)} médicaments en mémoire.")
        except json.JSONDecodeError:
            print("Erreur de lecture du fichier existant, on repart de zéro.")
            medications = []
            seen_names = set()

    # 2. Lire la dernière position
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                skip = int(f.read().strip())
            print(f"Reprise automatique à partir de la position {skip} sur l'API...")
        except ValueError:
            skip = 0
            
    target_stop = skip + fetch_amount
    print(f"Objectif : avancer jusqu'à la position {target_stop}...\n")
    
    # Configuration du délai (OpenFDA limite à 40 requêtes par minute sans clé API)
    # Pour faire massivement des requêtes sans se faire bloquer, 1.5s est plus sûr.
    delay_between_requests = 1.0 
    
    while skip < target_stop:
        url = f"https://api.fda.gov/drug/ndc.json?search=_exists_:generic_name&limit={limit}&skip={skip}"
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
                results = data.get('results', [])
                if not results:
                    print("Plus aucun résultat trouvé sur l'API.")
                    break
                    
                for item in results:
                    generic_name = item.get('generic_name', '').strip()
                    brand_name = item.get('brand_name', '').strip()
                    dosage_form = item.get('dosage_form', 'Unknown')
                    
                    if generic_name:
                        name_lower = generic_name.lower()
                        # Vérification de doublon ultra-rapide O(1) au lieu de O(N)
                        if name_lower not in seen_names:
                            seen_names.add(name_lower)
                            medications.append({
                                "name": generic_name.capitalize(),
                                "brand_name": brand_name,
                                "type": "Generic",
                                "dosage_form": dosage_form
                            })
                            
                print(f"API progression: {skip}/{target_stop} - Noms uniques trouvés: {len(medications)}")
                skip += limit
                
                # Pause sécurisée pour ne pas être banni (Rate Limit)
                time.sleep(delay_between_requests)
                
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("\n[!] Rate Limit atteint (Trop de requêtes).")
                print("L'API OpenFDA nous demande de ralentir. Le script va sauvegarder et s'arrêter.")
                break
            elif e.code == 400:
                print("\n[!] Limite de pagination atteinte (Souvent bloquée à 25000 par OpenFDA).")
                break
            else:
                print(f"Erreur HTTP: {e}")
                break
        except urllib.error.URLError as e:
            print(f"Error fetching data: {e}")
            break
            
    # 3. Sauvegarder les résultats mis à jour
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(medications, f, indent=2, ensure_ascii=False)
        
    # 4. Enregistrer là où on s'est arrêté
    with open(state_file, 'w') as f:
        f.write(str(skip))
        
    print(f"\nSuccès ! {len(medications)} médicaments sont maintenant sauvés dans {output_file}")

if __name__ == "__main__":
    fetch_medications()
