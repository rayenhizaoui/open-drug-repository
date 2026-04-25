# Open Drug Repository

Un projet simple et efficace permettant de générer et maintenir une base de données exhaustive des médicaments à partir de l'API officielle mondiale **[OpenFDA](https://open.fda.gov/)**.

## 🚀 Fonctionnalités

- **Performant & Optimisé** : Conçu pour traiter des milliers, voire des millions de données instantanément grâce à l'utilisation de `set()` en Python pour éviter les doublons en temps réel O(1).
- **Reprise Automatique (Resumable)** : Le script sauvegarde sa progression dans `fetch_state.txt`. En cas de coupure (ou de limite API), il reprendra exactement là où il s'est arrêté à la prochaine exécution.
- **Respect des Limites API (Anti-Ban)** : Délais intégrés (`time.sleep`) et gestion des erreurs HTTP 429 pour ne pas se faire bloquer par les serveurs gouvernementaux.
- **Export JSON Propre** : Génère un fichier `medications_full.json` prêt à être utilisé dans n'importe quelle application (Web, Mobile, etc.).

## 📦 Utilisation

1. Assurez-vous d'avoir Python installé sur votre machine.
2. Clonez le dépôt et naviguez dans le dossier.
3. Lancez le script de récupération :
   ```bash
   python fetch_medications.py
   ```
4. Le script commencera à télécharger les données et créera/mettra à jour le fichier `medications_full.json`. Vous pouvez l'arrêter à tout moment (Ctrl+C) et le relancer plus tard.

## 📄 Structure des données générées

Le fichier de sortie `medications_full.json` suit ce format :

```json
[
  {
    "name": "Acetaminophen",
    "brand_name": "Tylenol",
    "type": "Generic",
    "dosage_form": "TABLET"
  },
  {
    "name": "Ibuprofen",
    "brand_name": "Advil",
    "type": "Generic",
    "dosage_form": "CAPSULE"
  }
]
```

## 🛠 Fichiers du projet

- `fetch_medications.py` : Le script principal de collecte (Web Scraper/API Fetcher).
- `medications_sample.json` : Un petit échantillon statique contenant les médicaments "grand public" les plus courants pour tester rapidement sans lancer le script.
- `fetch_state.txt` : *Fichier généré automatiquement* mémorisant l'état de la pagination.
- `medications_full.json` : *Fichier généré automatiquement* contenant la base de données de milliers de médicaments.
