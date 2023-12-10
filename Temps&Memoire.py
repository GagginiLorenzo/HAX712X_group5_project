
#Fonction pour chronometrer le temps 
import time

def calculer_temps_execution(code_a_mesurer):
    debut = time.time()
    # Exécutez le code à mesurer
    exec(code_a_mesurer)
    fin = time.time()
    temps_execution = fin - debut
    return temps_execution


#Fonction pour l'efficacité de la mémoire 

#Installer memory_profiler 
from memory_profiler import profile

@profile
def main():
   
 # le code principale 
    pass  


if __name__ == "__main__":
    main()