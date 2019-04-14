# Speechtux, ler prolongement de Gspeech

## Intro

Aidant au dev de la distribution Primtux, j'ai participé progressivement à **Gspeech** : un synthétiseur vocal basé sur **picoTTS**.
Rapidement, j'ai donc effectué quelques patchs.

J'ai vite identifié les défauts de l'outil, principalement lorsque je me suis penché sur l'extension **picovox** de libreoffice qui permettait de règler la vitesse de lecture.
(Car elle est basé sur un binding de la lib et non sur la ligne de commande).

Fort de ce constat, j'ai décidé de partir d'une feuille blanche, de créer un nouveau projet et de choisir un langage bas niveau : Rust.

## Le projet pour une V1

Le but du projet est de fournir :

- [ ] une ligne de commande plus complète que celle de **pico2wave**

- [x] une API C simplifié pour donner accès au fonctionnalité de **SpeechTux** à d'autres langages de programmation : Python notamment.
  il sera notamment possible d'adapter l'extension **picovox** de libreoffice pour qu'il se base intégralement sur cet outil :
  réduction du code, cohérence etc.

- [ ] une interface en GTK similaire à celle de Gspeech mais plus fourni : **Gspeech** est bien pensé, le but n'est donc pas de révolutionné mais d'améliorer.

- [ ] un serveur web permettant via une API Rest de piloter la lecture.
L'avantage est d'avoir des applis en HTML5 qui peuvent bénéficier de cet outil facilement.

- [ ] un moteur d'amélioration de la lecture. Là, on est dans le coeur du projet. **picovox** est un bon synthétiseur mais n'a rien pour reconnaitre des mots.

- [ ] une gestion de la lecture unifié : pour éviter la cacophonie, seul 1 logiciel peut commanditer la lecture.
Du coup, **speechtux** sera capable (en se basant sur la lib d'Alsa) de savoir quand la lecture c'est terminé.

- un paquet .deb pour les distributions basé sur Debian.

## Les limitations

- Le soft est basé sur Linux, principalement dédié à Primtux. C'est un choix volontaire.
- Le soft n'est pensé que pour le français

## L'existant

Le soft est à l'état de prototype.
Certaines bases sont déjà présentes mais l'on est encore loin du compte pour une version stable en production.

Le serveur web se lance actuellement ainsi :

```sh
cargo run --bin web
```

Un exemple est disponible dans examples/javascript qui permet de lire un texte saisie dans une mini page web que l'on peut lancer directement dans un navigateur.

Par exemple :

```sh
firefox examples/javascript/index.html
```

Un example de programme en python se lance ainsi :

```sh
./examples/python/read.py
```

## D'autres améliorations envisageables

- une interface DBUS pour communiquer avec d'autres programmes de manière standardisé.

## Moteur de lecture

Le but est de pouvoir lire :

- un terme provenant de l'anglais => ex: hacker, wiki, hardware, ram
- une abréviations courantes => ex: SNCF
- les logiciels les plus courants dans la sphère linux
- des marques connus => ex: google
- du langage sms ou des abréviations/acronymes
- la lecture des signes particuliers : €, $ etc.
    
- de corriger à la volé des fautes de frappes

- de lire correctement des motifs uniques => ex 

"google" peut se retrouver dans "dégooglelisons" et sera prononcé "gougeulle"
l'abréviation odt ne se retrouvera pas dans une autre chaine donc il n'y a que "o d t" qui est acceptable.

