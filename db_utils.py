import pymysql.cursors  # TODO: req
import config

SELECT_USERS_BY_USERNAME = "SELECT id, username FROM users WHERE username in ({})"
INSERT_SCRAPED_INFO = '''INSERT INTO users (external_id, username, follower_count, following_count, trips_count, 
distance_traveled, countries_count, cities_count, twitter, instagram, bio) 
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
UPDATE_USER = '''UPDATE users SET follower_count = %s, following_count = %s, trips_count = %s,  distance_traveled = %s, 
countries_count = %s, cities_count = %s, twitter = %s, instagram = %s, bio = %s WHERE id = %s'''
SELECT_TRIPS = "SELECT external_id FROM trips WHERE user_id = {}"
INSERT_TRIPS_INFO = '''INSERT INTO trips (external_id, user_id, trip_start, trip_length, trip_end, city_country) 
VALUES (%s,%s,%s,%s,%s,%s)'''
SELECT_CITY_COUNTRY = "SELECT id FROM city_country WHERE city_name = '{}' and country_name = '{}' LIMIT 1"
INSERT_CITY_COUNTRY = "INSERT INTO city_country (city_name, country_name) VALUES (%s, %s)"


def connect_to_db(host, user, password, db):
    connection = pymysql.connect(host=host,
                                 user=user,
                                 password=password,
                                 db=db,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def get_existing_usernames(conn, users_list):
    users_dict = select_users(conn, users_list)
    result = []
    for user in users_dict:
        result.append(user['username'])
    return result


def select_users(conn, username_list):
    usernames = ','.join(f'"{username}"' for username in username_list)
    query = SELECT_USERS_BY_USERNAME.format(usernames)
    with conn.cursor() as cur:
        cur.execute(query)
        result = cur.fetchall()
    return result


def transform_dictionary(input_list, key_field_name, value_field_name):
    new_dict = {}
    for item in input_list:
        new_dict[item[key_field_name]] = item[value_field_name]
    return new_dict


def save_user_info(conn, users_dict):
    existing_users_dict = transform_dictionary(select_users(conn, users_dict.keys()), 'username', 'id')
    for username in users_dict:
        user_info = users_dict[username]
        trips = user_info[config.NAMES_DICT["TRIP_LIST"]]
        trips_list = []

        with conn.cursor() as cur:
            if username not in existing_users_dict.keys():

                cur.execute(INSERT_SCRAPED_INFO,
                            (user_info['user_id'], username, user_info['follower-count'], user_info['following-count'],
                             user_info['trips-count'], user_info['distance-traveled'], user_info['countries-count'],
                             user_info['cities-count'], user_info['twitter'], user_info['instagram'], user_info['bio'])
                            )
                conn.commit()

                current_user_id = cur.lastrowid
            else:
                cur.execute(UPDATE_USER,
                            (
                                user_info['follower-count'], user_info['following-count'], user_info['trips-count'],
                                user_info['distance-traveled'], user_info['countries-count'], user_info['cities-count'],
                                user_info['twitter'], user_info['instagram'], user_info['bio'],
                                existing_users_dict[username]
                            )
                            )
                conn.commit()
                current_user_id = existing_users_dict[username]

            trips_query = SELECT_TRIPS.format(current_user_id)
            cur.execute(trips_query)
            existing_trips = cur.fetchall()
            existing_trips_ext_ids = [t['external_id'] for t in existing_trips]
            for trip_id in trips:
                if trip_id not in existing_trips_ext_ids:

                    query = SELECT_CITY_COUNTRY.format(trips[trip_id]['name'], trips[trip_id]['country'])
                    cur.execute(query)
                    cc_id = cur.fetchall()

                    if not cc_id:

                        cur.execute(INSERT_CITY_COUNTRY, (trips[trip_id]['name'], trips[trip_id]['country']))
                        conn.commit()

                        cc_id = cur.lastrowid
                    else:
                        cc_id = cc_id[0]['id']

                    trips_list.append((trip_id, current_user_id, trips[trip_id]['trip_start'],
                                       trips[trip_id]['trip_length'], trips[trip_id]['trip_end'], cc_id))

            cur.executemany(INSERT_TRIPS_INFO, trips_list)
            conn.commit()
