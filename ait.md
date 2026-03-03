Read skill [mvp-rhythm](file:///c%3A/Users/thoma/Desktop/programmes/M1DENG/Semestre%202/M1DE-ai-gateway/Projet/.github/skills/mvp-rhythm/SKILL.md?vscodeLinkType%3Dskill)

Read skill [qualitative-code](file:///c%3A/Users/thoma/Desktop/programmes/M1DENG/Semestre%202/M1DE-ai-gateway/Projet/.github/skills/qualitative-code/SKILL.md?vscodeLinkType%3Dskill#1-1), lines 1 to 80

Voici le plan complet, organisé par phases, avec les prompts exacts à utiliser.

---

## Phase 1 — Setup (15 min)

### Étape 1 : Créer la structure du projet

**Prompt :**
```
Crée la structure de fichiers suivante pour un projet Python "extracteur de données de formulaires" :
src/
  main.py           # Point d'entrée CLI
  extractor.py      # Logique d'extraction IA
  validator.py      # Validation Pydantic
  models.py         # Les modèles Pydantic (schéma + résultat)
schemas/
  exemple_facture.json    # Un schéma exemple
samples/
  exemple_facture.txt     # Un document texte exemple
.env.example
requirements.txt

Pour requirements.txt, inclure : openai, pydantic, python-dotenv
```

---

## Phase 2 — Modèles de données (30 min)

### Étape 2 : Définir les modèles Pydantic

**Prompt :**
```
Contexte : Je construis un extracteur de données de formulaires en Python.
Exigence : Crée les modèles Pydantic dans models.py.

J'ai besoin de :
1. FieldDefinition : définit un champ attendu (nom, type, obligatoire, description)
2. ExtractionSchema : liste de FieldDefinition + nom du schéma
3. FieldResult : résultat d'un champ extrait (valeur, score de confiance 0.0-1.0, statut: "found"/"missing"/"uncertain")
4. ExtractionResult : résultat global (statut "success"/"warning"/"error", dict de FieldResult, alertes list[str], metadata)

Contraintes :
- confiance doit être entre 0.0 et 1.0
- Si un champ obligatoire est absent, son statut est "missing" et sa valeur est null
- Utilise Field() de Pydantic pour les contraintes et descriptions

Explique chaque classe avec un commentaire docstring en français.
```

### Étape 3 : Créer un schéma JSON exemple

**Prompt :**
```
Crée un fichier schemas/exemple_facture.json qui définit un schéma d'extraction pour une facture commerciale.
Champs attendus : nom_fournisseur, date_facture, montant_total, numero_facture, nom_client.
Chaque champ doit avoir : name, type (string/number/date), required, description.
Crée aussi samples/exemple_facture.txt avec un exemple réaliste de facture en texte brut.
```

---

## Phase 3 — Cœur de l'application (1h30)

### Étape 4 : Le moteur d'extraction IA

**Prompt :**
```
Contexte : Extracteur de données en Python, modèles Pydantic définis dans models.py.
Exigence : Implémente extractor.py avec une fonction extract(document_text: str, schema: ExtractionSchema) -> ExtractionResult.

Architecture :
- Construire un prompt système strict qui interdit à l'IA d'inventer des données manquantes
- Utiliser l'API OpenAI (gpt-4o-mini) avec response_format JSON
- Parser la réponse et construire un ExtractionResult

Contraintes critiques :
- Si l'IA ne trouve pas un champ : valeur = null, statut = "missing", confiance < 0.3
- Le prompt doit contenir la phrase exacte : "Si un champ est absent du document, retourne null. Ne jamais inventer."
- Gérer les erreurs API : timeout, rate limit → retourner un ExtractionResult avec statut "error"
- Gérer si la réponse JSON est malformée

Cas limites à gérer :
- document_text vide ou None
- schéma sans aucun champ
- réponse de l'IA hors format JSON attendu

Utilise python-dotenv pour charger OPENAI_API_KEY depuis .env
```

### Étape 5 : La validation

**Prompt :**
```
Contexte : Extracteur de données, extractor.py est implémenté.
Exigence : Implémente validator.py avec une fonction validate(result: ExtractionResult, schema: ExtractionSchema) -> ExtractionResult.

La validation doit :
1. Vérifier que tous les champs "required=True" sont présents (statut != "missing")
2. Vérifier la cohérence des types (si type="number", la valeur doit être convertible en float)
3. Ajouter des alertes dans result.validation.alertes pour chaque anomalie
4. Calculer un statut global : "success" si confiance_globale > 0.8 ET aucun champ obligatoire manquant, sinon "warning"
5. Ne pas modifier les valeurs extraites (la validation signale, elle ne corrige pas)

Retourne le même ExtractionResult enrichi avec les alertes.
```

---

## Phase 4 — Interface CLI (30 min)

### Étape 6 : Le point d'entrée

**Prompt :**
```
Contexte : Extracteur de données Python, tous les modules sont prêts.
Exigence : Crée main.py avec une CLI simple via argparse.

Commandes :
- python main.py extract --document chemin/vers/doc.txt --schema chemin/vers/schema.json [--output resultat.json]
- python main.py validate --result resultat.json --schema chemin/vers/schema.json

Comportement :
- Affiche un résumé lisible dans le terminal (pas juste le JSON brut)
- Affiche les alertes en rouge (utilise colorama ou simple préfixe [ALERTE])
- Exporte le JSON complet dans --output si précisé
- Exit code 1 si statut="error", exit code 0 sinon

Gestion d'erreurs :
- Fichier introuvable → message clair, pas de stack trace
- JSON Schema invalide → indiquer quelle propriété est incorrecte
```

---

## Phase 5 — Tests des cas limites (30 min)

### Étape 7 : Tester les cas qui cassent

**Prompt :**
```
Crée un fichier tests/test_edge_cases.py qui teste les cas limites de l'extracteur.

Tests à écrire (sans appel réel à l'API, utilise unittest.mock) :
1. Document vide → statut "error" ou "warning", pas de crash
2. Tous les champs manquants → chaque champ a statut "missing" et confiance < 0.3
3. JSON malformé retourné par l'IA → géré sans crash
4. Schéma sans champs obligatoires → extraction réussie
5. Valeur de type incorrect (string là où number attendu) → alerte de validation

Montre-moi aussi comment tester manuellement avec :
- samples/document_vide.txt
- samples/document_hors_sujet.txt (texte sans rapport avec le schéma)
```

---

## Phase 6 — Documentation finale (30 min)

### Étape 8 : README

**Prompt :**
```
Rédige un README.md complet pour ce projet "Extracteur de données de formulaires".

Sections requises :
1. Description du problème résolu (2-3 phrases)
2. Architecture (reprend le schéma ASCII du sujet)
3. Installation (pip install, .env setup)
4. Utilisation avec exemples de commandes concrètes
5. Format du schéma JSON (avec un exemple complet annoté)
6. Format de la sortie JSON (avec un exemple complet annoté)
7. Gestion des cas limites (tableau : input → comportement attendu)
```

---

## Récapitulatif du temps (MVP ~6h)

| Phase | Durée |
|-------|-------|
| Setup + Structure | 15 min |
| Modèles Pydantic | 30 min |
| Moteur d'extraction | 1h30 |
| Validation | 30 min |
| CLI | 30 min |
| Tests cas limites | 30 min |
| README + Journal | 30 min |
| **Buffer debug** | **1h15** |

---

### Les 3 règles d'or à respecter tout au long

1. **Jamais d'invention** : Chaque prompt à l'IA doit contenir explicitement "champ absent = null, ne pas inventer".
2. **Tester le "mauvais cas"** : Après chaque feature, teste avec un input vide ou incohérent.
3. **Noter dans le journal** : Après chaque étape, une entrée de 3 lignes dans JOURNAL.md.