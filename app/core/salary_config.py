import yaml

def load_salary_percentiles():
    with open("config/salary_percentiles.yaml", "r", encoding="utf-8") as file:
        salary_percentiles = yaml.safe_load(file)
    return salary_percentiles

salary_percentiles = load_salary_percentiles()

def get_all_cities(salary_percentiles):
    cities = set()
    for role, locations in salary_percentiles.items():
        for city in locations.keys():
            cities.add(city)
    return sorted(list(cities))

available_cities = get_all_cities(salary_percentiles)

def get_all_roles(salary_percentiles):
    roles = set(salary_percentiles.keys())
    return sorted(list(roles))

available_roles = get_all_roles(salary_percentiles)

def get_all_seniorities(salary_percentiles):
    seniorities = set()
    for role, locations in salary_percentiles.items():
        for location_data in locations.values():
            seniorities.update(location_data.keys())
    return sorted(list(seniorities))

available_seniorities = get_all_seniorities(salary_percentiles)
