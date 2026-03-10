# Specification Fonctionnelle et Technique — FormAI

## 1. Objet du projet

FormAI est une application d'extraction de donnees structurees a partir de documents non structures. Le systeme prend en entree un document texte ou un fichier importable et un schema de champs attendus, puis produit un resultat JSON valide, enrichi par des metadonnees de confiance et des alertes de validation.

Le projet vise un MVP exploitable dans un contexte pedagogique et met l'accent sur :

- la definition dynamique d'un schema d'extraction ;
- l'extraction assistee par LLM sans invention de valeurs ;
- la validation technique et metier du resultat ;
- une interface web simple d'utilisation ;
- une robustesse minimale face aux cas limites courants.

## 2. Probleme adresse

Dans de nombreux flux metiers, les informations utiles arrivent sous forme de documents heterogenes : factures, CV, devis, contrats, fiches de paie, bons de commande. Ces documents ne sont pas directement exploitables par un systeme d'information sans ressaisie ou transformation manuelle.

FormAI automatise cette transformation en convertissant un contenu non structure en donnees structurees conformes a un schema cible.

## 3. Objectifs

### 3.1 Objectifs fonctionnels

- Permettre a un utilisateur de definir un schema d'extraction compose de champs, types, obligations et descriptions.
- Permettre l'analyse d'un document saisi manuellement ou importe depuis un fichier.
- Extraire les valeurs attendues via un modele LLM compatible API OpenAI.
- Retourner pour chaque champ une valeur, un statut et un score de confiance.
- Signaler explicitement les champs absents, incertains ou incoherents.
- Exporter les resultats au format JSON.

### 3.2 Objectifs non fonctionnels

- Fournir une architecture modulaire facile a comprendre et maintenir.
- Encadrer les cas limites les plus frequents sans crash.
- Limiter les risques elementaires lies a l'upload de fichiers.
- Conserver une stack legere, lisible et facile a lancer localement.

## 4. Perimetre du MVP actuel

Le perimetre reellement implemente couvre :

- une API FastAPI locale ;
- une interface web mono-page en HTML/CSS/JavaScript ;
- un pipeline extraction puis validation ;
- un mode texte direct ;
- un mode upload de fichiers TXT, JSON et PDF avec extraction de texte ;
- un mode batch cote interface ;
- des schemas d'exemple charges depuis `data/schemas` ;
- une CLI minimale pour lancer une extraction depuis des fichiers.

Ne sont pas implementes dans la version actuelle :

- persistance serveur des extractions ;
- base de donnees ;
- authentification ;
- OCR avance sur documents images ou PDF sans couche texte ;
- regles metier specialisees comme IBAN, TVA, SIRET ou coherence multi-champs ;
- apprentissage a partir des corrections utilisateur ;
- traitement asynchrone distribue ;
- interface de correction manuelle champ par champ.

## 5. Utilisateurs cibles

- Utilisateur metier souhaitant extraire rapidement des informations d'un document.
- Developpeur ou evaluateur souhaitant tester le pipeline via API ou CLI.
- Etudiant ou mainteneur ayant besoin d'un projet lisible et justifiable techniquement.

## 6. Cas d'usage principaux

### 6.1 Extraction simple depuis l'interface

1. L'utilisateur ouvre l'application web.
2. Il construit ou charge un schema d'extraction.
3. Il colle un document texte ou charge un exemple.
4. Il lance l'extraction.
5. Il consulte les valeurs extraites, les scores de confiance et les alertes.
6. Il exporte le JSON genere.

### 6.2 Import d'un fichier unique

1. L'utilisateur glisse ou selectionne un fichier `.txt`, `.json` ou `.pdf`.
2. Le backend valide le fichier puis en extrait le texte.
3. Le texte est injecte dans l'interface.
4. L'utilisateur lance l'extraction sur ce contenu.

### 6.3 Traitement par lots

1. L'utilisateur importe plusieurs fichiers compatibles.
2. Le backend renvoie le texte extrait pour chaque document.
3. L'interface affiche une previsualisation batch.
4. L'application appelle l'endpoint d'extraction sequentiellement pour chaque document.
5. Les resultats sont affiches sous forme consolidee et exportables en JSON.

### 6.4 Extraction via CLI

1. L'utilisateur fournit un document texte et un schema JSON.
2. La CLI charge les fichiers, lance l'extraction, puis la validation.
3. Un resume est affiche en console.
4. Un fichier de sortie JSON peut etre ecrit si un chemin est fourni.

## 7. Exigences fonctionnelles detaillees

### 7.1 Definition du schema

Le schema d'extraction doit contenir :

- `schema_name` : nom du schema ;
- `description` : description libre ;
- `fields` : liste des champs attendus.

Chaque champ doit contenir :

- `name` : identifiant unique du champ ;
- `type` : `string`, `number`, `date` ou `boolean` ;
- `required` : booleen indiquant si le champ est obligatoire ;
- `description` : contexte metier facultatif.

Contraintes :

- le nom du schema ne peut pas etre vide ;
- les noms de champs doivent etre uniques ;
- un schema vide est refuse par l'API d'extraction ;
- la CLI et le frontend doivent manipuler un schema JSON conforme au modele Pydantic.

### 7.2 Document d'entree

Le document peut provenir :

- d'une saisie ou d'un collage dans une zone texte ;
- d'un fichier `.txt` ;
- d'un fichier `.json` ;
- d'un fichier `.pdf` disposant d'une couche texte extractible.

Contraintes :

- un document vide est refuse a l'extraction ;
- la taille maximale par fichier est de 5 Mo ;
- le texte extrait est tronque a 50 000 caracteres maximum avant appel au LLM ;
- le systeme ne garantit pas le support des PDF purement image.

### 7.3 Règles d'extraction LLM

Le moteur d'extraction doit :

- construire un prompt a partir du document et du schema ;
- imposer un format de sortie JSON objet ;
- exiger la presence de chaque champ dans la reponse du modele ;
- interdire explicitement l'invention de valeurs ;
- forcer `null` pour les informations absentes.

Pour chaque champ, la reponse attendue du modele comprend :

- `value` ;
- `confidence` compris entre 0 et 1 ;
- `status` parmi `found`, `missing`, `uncertain` ;
- `source_hint` pour indiquer l'origine ou un indice textuel.

### 7.4 Normalisation post-extraction

Apres reception de la reponse LLM :

- le JSON est parse de maniere defensive ;
- si un champ est absent ou mal structure dans la reponse, il est reconstruit comme manquant ;
- une valeur `null` force le statut `missing` ;
- la confiance est bornee entre 0 et 1 ;
- pour un champ manquant, la confiance est plafonnee a 0.3 ;
- des alertes sont ajoutees si un champ obligatoire est absent.

### 7.5 Validation metier et technique

Le validateur doit verifier :

- la presence des champs obligatoires ;
- la presence effective des champs dans `result.data` ;
- la compatibilite de type entre la valeur extraite et le type declare ;
- le format de date attendu `YYYY-MM-DD`.

La validation ne modifie pas les valeurs extraites, mais enrichit :

- `validation.alerts` ;
- `validation.confidence_global` ;
- `status` global du resultat.

### 7.6 Statuts globaux

Les statuts globaux du resultat sont :

- `success` ;
- `warning` ;
- `error`.

Comportement actuel :

- l'extracteur retourne `error` si le document est vide ou si l'appel LLM echoue ;
- l'extracteur retourne `success` si la confiance moyenne est au moins egale a `0.8` et sans alerte ;
- sinon l'extracteur retourne `warning` ;
- apres validation, le statut devient `success` si la confiance moyenne est strictement superieure a `0.8` et qu'aucun champ obligatoire n'est manquant ;
- sinon le statut devient `warning`, sauf si le resultat etait deja en `error`.

Note importante :

- dans l'etat actuel du code, des alertes de type peuvent coexister avec un statut global `success` si les champs obligatoires sont presents et que la confiance globale reste superieure au seuil.

### 7.7 Confiance globale

La confiance globale correspond a la moyenne des confiances de tous les champs presents dans le resultat. Elle est calculee :

- une premiere fois dans l'extracteur ;
- une seconde fois dans le validateur sur les champs effectivement presents.

### 7.8 Affichage des resultats

L'interface web doit permettre :

- d'afficher le statut global ;
- d'afficher les champs extraits ;
- de visualiser la confiance par champ ;
- de lister les alertes de validation ;
- d'exporter le resultat JSON.

En mode batch, l'interface doit afficher un resultat consolide par fichier traite.

### 7.9 Schemas d'exemple

Le backend doit charger automatiquement les fichiers JSON presents dans `data/schemas` et les exposer au frontend. Chaque schema d'exemple peut embarquer un `sample_document` pour precharger un document de demonstration.

Schemas fournis actuellement :

- facture ;
- devis commercial ;
- bon de commande ;
- contrat de travail ;
- fiche de paie ;
- CV candidat.

## 8. Exigences techniques

### 8.1 Stack retenue

- Python 3.10+ ;
- FastAPI pour l'API ;
- Uvicorn pour le serveur ASGI ;
- Pydantic v2 pour la modelisation et la validation ;
- OpenAI SDK utilise contre une API DeepSeek compatible ;
- `python-dotenv` pour le chargement de configuration ;
- `pypdf` pour l'extraction texte PDF ;
- frontend en HTML, CSS et JavaScript natifs ;
- Pytest et `unittest.mock` pour les tests.

### 8.2 Configuration

Variables d'environnement attendues :

- `DEEPSEEK_API_KEY` : cle d'acces au service ;
- `DEEPSEEK_API_URL` : URL de base de l'API ;
- `DEEPSEEK_MODEL` : nom du modele, valeur par defaut `deepseek-chat`.

### 8.3 Structure logique

- `src/core` : logique metier d'extraction, modeles, validation ;
- `src/backend` : API HTTP et gestion des uploads ;
- `src/frontend` : interface utilisateur et orchestration navigateur ;
- `data/schemas` : schemas et exemples de documents ;
- `tests` : verification des cas limites.

## 9. Architecture applicative

### 9.1 Vue d'ensemble

Le systeme suit une architecture en couches simple :

1. Presentation : frontend web mono-page.
2. Transport : API REST FastAPI.
3. Metier : moteur d'extraction et validateur.
4. Integration externe : service LLM compatible OpenAI.

### 9.2 Flux principal

1. Le frontend compose un schema et fournit un document.
2. Le frontend envoie une requete `POST /api/extract`.
3. Le backend valide le schema et le document.
4. Le backend appelle `extract(document_text, schema)`.
5. L'extracteur interroge le LLM et normalise la reponse.
6. Le backend applique `validate_extraction(result, schema)`.
7. Le resultat final est retourne au frontend en JSON.

### 9.3 Flux upload

1. Le frontend envoie les fichiers a `POST /api/upload`.
2. Le backend valide taille, extension et signature binaire si necessaire.
3. Le backend extrait du texte selon le type de fichier.
4. Le backend tronque si necessaire.
5. Le frontend exploite les textes retournes en mode simple ou batch.

## 10. Contrats de donnees

### 10.1 Modele `FieldDefinition`

- `name: str`
- `type: string | number | date | boolean`
- `required: bool`
- `description: str`

### 10.2 Modele `ExtractionSchema`

- `schema_name: str`
- `description: str`
- `fields: list[FieldDefinition]`

### 10.3 Modele `FieldResult`

- `value: Any | null`
- `confidence: float` entre 0 et 1
- `status: found | missing | uncertain`
- `source_hint: str`

### 10.4 Modele `ValidationSummary`

- `confidence_global: float`
- `alerts: list[str]`

### 10.5 Modele `ExtractionMetadata`

- `model: str`
- `extracted_at: datetime`

### 10.6 Modele `ExtractionResult`

- `status: success | warning | error`
- `data: dict[str, FieldResult]`
- `validation: ValidationSummary`
- `metadata: ExtractionMetadata`

## 11. API HTTP

### 11.1 `GET /api/health`

Objectif : verifier que l'API est disponible.

Reponse attendue :

```json
{
  "status": "ok",
  "version": "1.1.0"
}
```

### 11.2 `GET /api/schemas/examples`

Objectif : retourner les schemas d'exemple presents sur disque.

Chaque element retourne contient :

- `name`
- `description`
- `schema`
- `sample_document`

### 11.3 `POST /api/upload`

Objectif : importer un ou plusieurs fichiers et en extraire le texte brut.

Entree : `multipart/form-data` avec `files`.

Sortie :

- pour chaque fichier accepte : `filename`, `text`, `size_ko`, `file_type`, `truncated`, `char_count`, `status=success` ;
- pour chaque fichier en erreur : `filename`, `status=error`, `error`.

Codes et comportements :

- `413` si le fichier depasse la taille maximale ;
- `422` si le format n'est pas supporte ou si le fichier est incoherent ;
- `503` si `pypdf` manque pour le traitement PDF.

### 11.4 `POST /api/extract`

Objectif : lancer le pipeline extraction puis validation.

Corps attendu :

```json
{
  "document_text": "...",
  "schema": {
    "schema_name": "...",
    "description": "...",
    "fields": []
  }
}
```

Reponse : un `ExtractionResult` serialise.

Erreurs metier et techniques traitees :

- `422` si le document est vide ;
- `422` si le schema est invalide ;
- `422` si le schema ne contient aucun champ ;
- `503` si la configuration DeepSeek est manquante ;
- `500` pour toute autre erreur inattendue du backend.

## 12. Interface web

### 12.1 Ecran principal

L'interface est composee de trois zones principales :

- colonne schema ;
- colonne document ;
- colonne resultats.

### 12.2 Fonctions UI principales

- ajout, suppression et edition dynamique de champs ;
- previsualisation JSON du schema ;
- chargement de schemas d'exemple ;
- chargement d'un document exemple associe au schema ;
- glisser-deposer de fichiers ;
- traitement d'un fichier unique ou de plusieurs fichiers ;
- verification de disponibilite du backend ;
- raccourci `Ctrl+Enter` pour lancer l'extraction ;
- export JSON du dernier resultat ou du dernier lot.

### 12.3 Regles d'activation de l'action principale

Le bouton d'extraction n'est actif que si :

- au moins un champ est defini dans le schema ;
- un document texte est present ou un lot de fichiers a ete prepare.

### 12.4 Mode batch

Le mode batch est gere au niveau du frontend. Le backend ne fournit pas un endpoint d'extraction en masse dedie ; l'interface appelle `POST /api/extract` sequentiellement pour chaque document importé.

Implications :

- simplicite d'implementation ;
- traitement plus lent sur de gros volumes ;
- absence de parallélisation explicite ;
- export unique du lot possible cote navigateur.

## 13. CLI

La CLI actuelle expose une commande `extract`.

Commande :

```bash
python -m src.cli.main extract --document <fichier.txt> --schema <schema.json> [--output resultat.json]
```

Fonctions prises en charge :

- lecture du document ;
- chargement et validation du schema ;
- extraction ;
- validation ;
- affichage d'un resume ;
- ecriture optionnelle du JSON resultat.

Limitations actuelles :

- la commande `validate` documentee dans le journal et le README n'est pas exposee comme sous-commande distincte dans l'etat courant du code ;
- la lecture du document en CLI suppose un fichier texte UTF-8.

## 14. Securite et defense en profondeur

Le projet integre une defense minimale adaptee a un MVP local.

Mesures appliquees :

- whitelist d'extensions sur l'upload ;
- controle du type MIME recu ;
- verification des magic bytes pour les PDF ;
- parsing defensif des JSON importes ;
- limite de taille a 5 Mo ;
- troncature du texte a 50 000 caracteres ;
- gestion defensive des erreurs d'API externe ;
- validation stricte des modeles en entree et sortie.

Limites connues :

- pas d'antivirus ;
- pas d'authentification ;
- CORS ouvert pour le developpement local ;
- pas de sandbox de contenu ;
- pas de limitation de debit cote serveur ;
- pas de chiffrement ou de persistance controlee des resultats.

## 15. Gestion des erreurs et resilence

Le systeme doit eviter les crashs sur les situations suivantes :

- document vide ;
- schema vide ;
- schema avec noms de champs dupliques ;
- reponse LLM non JSON ;
- champ obligatoire absent ;
- type incoherent ;
- PDF sans texte extractible ;
- configuration API manquante ;
- fichier trop volumineux ;
- format de fichier non supporte.

La strategie retenue repose sur :

- retour de statuts explicites ;
- messages d'erreur exploitables ;
- alerts consolidees dans le resultat ;
- fallback defensif plutot que traceback expose a l'utilisateur final.

## 16. Tests et verification

Les tests automatises existants couvrent principalement les cas limites de la couche metier :

- document vide ;
- tous les champs manquants ;
- JSON mal forme retourne par le modele ;
- schema sans champ obligatoire ;
- incoherence de type detectee a la validation.

La strategie de test repose sur le mock du client LLM afin d'eviter les appels reseau reels.

## 17. Hypotheses et contraintes

- L'application est concue pour un usage local ou de demonstration, pas pour la production.
- Le fournisseur LLM expose une API compatible OpenAI.
- Les utilisateurs comprennent la logique schema vers extraction.
- Les donnees sensibles ne sont pas gerees avec un niveau de gouvernance production.
- Les formats dates attendus sont strictement normalises en `YYYY-MM-DD` lors de la validation.

## 18. Critères de succes du projet

Le projet est considere comme conforme au MVP si :

- l'application se lance localement sans erreur de demarrage ;
- un utilisateur peut definir un schema et obtenir un JSON structure ;
- les champs manquants ne sont pas inventes ;
- la confiance et les alertes rendent l'extraction interpretable ;
- les principaux cas limites sont traites sans crash ;
- l'usage via interface web est possible sans passer par du code.

## 19. Evolutions recommandees

- ajouter une validation metier enrichie par type de document ;
- introduire un endpoint batch cote backend ;
- ajouter une interface de correction manuelle ;
- persister les resultats et historiques d'execution ;
- gerer l'authentification et des profils d'usage ;
- ajouter OCR image ou PDF scanne ;
- introduire des tests d'integration API et frontend ;
- mieux harmoniser la documentation avec la CLI reelle.

## 20. Resume executif

FormAI est un extracteur de donnees pilote par schema, concu comme un MVP robuste et lisible. Son coeur metier repose sur une combinaison simple : schema JSON, extraction LLM contrainte, validation Pydantic, alertes et confiance. La version actuelle couvre correctement le besoin pedagogique et demonstratif, avec une interface exploitable, une API claire et des garde-fous utiles, tout en laissant visibles plusieurs axes d'industrialisation.