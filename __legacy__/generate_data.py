import data_neo4j
import rozpravy
import zakony
import hlasy
import rozpravy_selenium

hlasy.Scraper().get_all_data()
zakony.Scraper().get_all_data()
rozpravy.Scraper().get_all_data()
rozpravy_selenium.Scraper().get_all_data()

data_neo4j.process_hlasovania_metadata()
data_neo4j.process_zakony()
data_neo4j.process_kluby()
data_neo4j.process_hlasovania()
data_neo4j.process_spektrum()
data_neo4j.process_rozpravy()

