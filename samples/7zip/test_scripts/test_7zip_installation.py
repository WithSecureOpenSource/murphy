from murphy.tester import run_remote_test

def test_install(worker):
    worker.In("Node 0").Do("Launch application")
    worker.Do("Install")
    
def test_install_2(worker):
    worker.In("Node 0").GoTo("Completing The 7_Zip 9_20 Setup Wizard")

def test_install_fail(worker):
    worker.In("Node 0").Do("Launch application")
    worker.Do("Installa")

    
if __name__ == '__main__':
    model_file = "../7zipWinScraper/7zipWinScraper.json"
    run_remote_test(test_install, model_file)
    run_remote_test(test_install_fail, model_file)
    run_remote_test(test_install_2, model_file)
    