import sys
sys.path.append('metrics')
import yaml
import dateUtil
import hourUtil
import utility_distance
import utility_meet
import utility_POI
import utility_POI_perWeek
import utility_tuile

def get_config():
    with open('config.yml') as f:
        return yaml.load(f, Loader=yaml.FullLoader)

config = get_config()
original_file = config['original_file']
ano_file = config['ano_file']
utility_metrics = [
    dateUtil,
    hourUtil,
    utility_distance,
    utility_meet,
    utility_POI,
    utility_POI_perWeek,
    utility_tuile
]
for metric in utility_metrics:
    print(metric.__name__ + " : " + str(getattr(metric, "main")(original_file, ano_file)))
