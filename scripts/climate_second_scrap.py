import json

from climate_first_scrap import *


# Open the file with the corrected links
with open("./data/correct_urls.json") as file:
    correct_links = json.load(file)

logging.basicConfig(filename="./data/logs_correct_urls.log", filemode="w", level=logging.INFO)
current_date = date.today()
data_engr = getenv('DATA_ENGR')

try:
    connection = psycopg2.connect(getenv('POSTGRES_CONN'))
    cursor = connection.cursor()
    
    url_instance = 'https://www.weather-atlas.com/en/new-york-usa/new-york-climate?c,mm,mb,km'
    city_dict_instance = scrap_city_dict(url_instance)
    params_dict = get_params_dict(city_dict_instance)
    months_dict = get_months_dict(city_dict_instance)
    columns_list = get_columns_list(params_dict)
    df_params_empty = params_template_df(months_dict, columns_list)
    
    start_time = time.time()
    for index, url in correct_links.items():
        city_dict = scrap_city_dict(url)
        if not city_dict:
            logging.info('city_id:%s:wrong_url:%s', index, url)
        else:
            df_params_fill = df_params_empty.copy()
            df_params_fill['city_id'] = index
            df_params_full = fill_params_template_df(city_dict, months_dict, params_dict, df_params_fill)
            df_params_full[['sys_updated_date', 'sys_updated_by']] = [date.today(), getenv('DATA_ENGR')]
            for row in df_params_full.itertuples(index=False):
                cursor.execute("INSERT INTO avg_climate VALUES %s", (tuple(row),))
            connection.commit()
except (Exception, Error) as error:
    print("[INFO Error]:", error)
finally:
    if connection:
        cursor.close()
        connection.close()
        finish_time = time.time()
        print("[INFO] Postgres connection closed.")
        print("Code execution time: ", finish_time - start_time)
        logging.info('Finished scraping: %s', finish_time - start_time)


