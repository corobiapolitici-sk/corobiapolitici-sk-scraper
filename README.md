# corobiapolitici.sk

This repo contains the backend for the webpage www.corobiapolitici.sk. Feel free to test it out on your own machine, or verify that the source code actually does what we claim it does.

## Setup
The following was tested as working on Ubuntu 18.04, other versions / systems might require some tweaks.

### 1. Install MongoDB

The MongoDB is used thorough the scraper from storing raw html to storing processed files in the format required for the graph database. For proper setup, follow the instructions from [here](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/). They should look similar to this:
```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4

echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list

sudo apt-get update
sudo apt-get install -y mongodb-org

```
After running all of these commands, you should have the MongoDB ready. Start the service by running 
```
sudo service mongod start
```
The default port is used in the scraper. If you have configured a different port, specify in it `config.yaml` as the `mongo-client-port`.

### 2. Install Neo4j

The Neo4j graph database stores the data in an easily queryable format, which is the starting point for our frontend. To install the neo4j database, you first need to make sure that Java 8 is available on your machine. You can install it by running:
```
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java8-installer
```
After this is completed, you can proceed to install the neo4j database by running
```
wget -O - https://debian.neo4j.org/neotechnology.gpg.key | sudo apt-key add -

echo 'deb https://debian.neo4j.org/repo stable/' | sudo tee -a /etc/apt/sources.list.d/neo4j.list

sudo apt-get update
sudo apt-get install neo4j
```
The last step is to start the service by running
```
sudo service neo4j start
```
Again, the default port for neo4j is used in the scraper. If you want to use a different port, specify it in `config.yaml` as the `neo4j-client-uri` and the authentication user/password as the `neo4j-client-auth`. Note, that by default a new dataset has the user/password combination set to `neo4j/neo4j`. You will be prompted to change the password the first time you access the database through the browser on `localhost:PORT`.

Lastly, configure the field `neo4j-import_path` to point to the neo4j import folder.

## 3. Setup Python

The main language used for scraping and processing is python 3. In the following steps we assume that `python3` is on your path and `pip3` is the corresponding package interface. Navigate to the project root and run:
```
pip3 install pipenv
pipenv install
```
After finishing the above commands, all the required packages should be installed.

## 4. Run the scraper

The main routine is contained within the file `main.py`. Run it using the command:
```
pipenv run sudo python3 main.py
```
The `sudo` is required to access the import folder of neo4j. If you would like the command without `sudo`, configure the access rights to the import folder.

The main script is configured to scrape, parse, process everything and add it to the running neo4j database. The first time, it takes more than an hour to complete, as it needs to scrape everything from scratch. All the successive runs are shorter, as they only consider updates.

If you would like to scrape only some parts of the data, comment out the relevant lines in the `main.py` script.

## 5. Verify that all went well

If everything finished without errors, you have most likely the whole database setup. To verify this, open the neo4j browser on `localhost:PORT` (most likely `localhost:7474`) and run a command such as 
```
MATCH (p:Poslanec)-[:Člen]->(k:Klub) RETURN p, k
```
The output should be an interactive graph showing the membership of politicians to their respective political parties.
