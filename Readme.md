pour build le conteneur en local:
docker build -t mufasa-api .     

pour lancer le conteneur en local:
docker run -p 8000:8000 --env-file .env

pour lancer le conteneur avec le reload auto:
docker run -p 8000:8000 --env-file .env -v ${PWD}:/app mufasa-api 