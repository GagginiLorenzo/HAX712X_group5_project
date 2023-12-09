import time

def calculer_temps_execution(code_a_mesurer):
    debut = time.time()
    # Exécutez le code à mesurer
    exec(code_a_mesurer)
    fin = time.time()
    temps_execution = fin - debut
    return temps_execution