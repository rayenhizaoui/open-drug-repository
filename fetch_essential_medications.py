import json
import urllib.request
import urllib.parse
import urllib.error
import time
from deep_translator import GoogleTranslator

# Cache de traduction pour éviter de surcharger Google avec les mêmes termes (Poudre, Comprimé, etc)
FR_CACHE = {}

def translate_to_fr(text):
    if not text or text == 'N/A' or text == 'Human Prescription Drug':
        return text
        
    # Gérer les listes (ex: routes d'administration)
    if isinstance(text, list):
        translated_list = []
        for item in text:
            translated_list.append(translate_to_fr(item))
        return translated_list
        
    if text in FR_CACHE:
        return FR_CACHE[text]
        
    try:
        # Traduire de l'anglais vers le français avec Google Translate
        res = GoogleTranslator(source='en', target='fr').translate(str(text))
        if res:
            res = res.capitalize()
            FR_CACHE[text] = res
            return res
        return text
    except Exception:
        # En cas d'erreur de traduction, on renvoie le texte original (Anglais)
        return text

def fetch_essential_medications():
    """
    Script pour récupérer automatiquement les 1000 médicaments les plus fréquents 
    de la base de données américaines, et les traduire en français.
    """
    output_file = 'medications_essential.json'
    max_items = 1000 # La limite max de la fonction count d'OpenFDA est 1000
    
    print(f"Étape 1 : Demande du Top {max_items} des médicaments les plus fréquents au niveau mondial...\n")
    
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
                    # Nettoyer un peu le nom (METFORMIN -> Metformin)
                    clean_name_en = med_name.lower().title()
                    
                    # Traduire vers le français !
                    name_fr = translate_to_fr(clean_name_en)
                    type_fr = translate_to_fr(item.get('product_type', 'N/A').title())
                    form_fr = translate_to_fr(item.get('dosage_form', 'N/A').title())
                    routes_fr = [translate_to_fr(r.title()) for r in item.get('route', ["N/A"])]
                    class_fr = [translate_to_fr(c.title()) for c in item.get('pharm_class', ["N/A"])]
                    
                    results_data.append({
                        "id": i + 1,
                        "name_fr": name_fr,
                        "name_en": clean_name_en,
                        "brand_name": item.get('brand_name', 'N/A').strip(),
                        "type": type_fr,
                        "dosage_form": form_fr,
                        "routes": routes_fr,
                        "pharm_class": class_fr
                    })
                    print(f"[{i+1}/{len(top_medications)}] {clean_name_en} -> {name_fr} (Traduit)")
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