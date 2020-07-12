import pymysql.cursors
import config


def connect_to_db(host, user, password, db):
    """
    Connects to a database
    :param host: hostname of DB
    :param user: DB user
    :param password: DB password
    :param db: DB name
    :return: pymysql connection
    """
    connection = pymysql.connect(host=host,
                                 user=user,
                                 password=password,
                                 db=db,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def get_existing_usernames(conn, users_list):
    """
    Returns list of usernames from users_list that exist in the DB
    :param conn: pymysql connection
    :param users_list: list of usernames to select
    :return: list of users that exist in the DB
    """
    users_dict = select_users(conn, users_list)
    result = []
    for user in users_dict:
        result.append(user['username'])
    return result


def select_users(conn, username_list):
    """
    Runs a select query, gets the usernames that exist in the DB
    :param conn: pymysql connection
    :param username_list: list of usernames to select
    :return: dict of usernames
    """
    usernames = ','.join(f'"{username}"' for username in username_list)
    query = config.SELECT_USERS_BY_USERNAME.format(usernames)
    with conn.cursor() as cur:
        cur.execute(query)
        result = cur.fetchall()
    return result


def transform_dictionary(input_list, key_field_name, value_field_name):
    """
    Transforms dictionaries from input list into a key-value dictionary
    :param input_list: list of dictionaries
    :param key_field_name: name of a dict field to become key
    :param value_field_name: name of a dict field to become value
    :return: dictionary
    """
    new_dict = {}
    for item in input_list:
        new_dict[item[key_field_name]] = item[value_field_name]
    return new_dict


def save_user_info(conn, users_dict):
    """
    Saves data from dictionary into the DB
    :param conn: pymysql connection
    :param users_dict: dictionary of user info
    :return: None
    """
    existing_users_dict = transform_dictionary(select_users(conn, users_dict.keys()), 'username', 'id')
    for username in users_dict:
        user_info = users_dict[username]
        trips = user_info[config.NAMES_DICT["TRIP_LIST"]]
        trips_list = []

        with conn.cursor() as cur:
            if username not in existing_users_dict.keys():

                cur.execute(config.INSERT_SCRAPED_INFO,
                            (user_info['user_id'], username, user_info['follower-count'], user_info['following-count'],
                             user_info['trips-count'], user_info['distance-traveled'], user_info['countries-count'],
                             user_info['cities-count'], user_info['twitter'], user_info['instagram'], user_info['bio'])
                            )
                conn.commit()
                current_user_id = cur.lastrowid
            else:
                cur.execute(config.UPDATE_USER,
                            (
                                user_info['follower-count'], user_info['following-count'], user_info['trips-count'],
                                user_info['distance-traveled'], user_info['countries-count'], user_info['cities-count'],
                                user_info['twitter'], user_info['instagram'], user_info['bio'],
                                existing_users_dict[username]
                            )
                            )
                conn.commit()
                current_user_id = existing_users_dict[username]

            trips_query = config.SELECT_TRIPS.format(current_user_id)
            cur.execute(trips_query)
            existing_trips = cur.fetchall()
            existing_trips_ext_ids = [t['external_id'] for t in existing_trips]
            for trip_id in trips:
                if trip_id not in existing_trips_ext_ids:

                    query = config.SELECT_CITY_COUNTRY.format(trips[trip_id]['name'], trips[trip_id]['country'])
                    cur.execute(query)
                    cc_id = cur.fetchall()

                    if not cc_id:

                        cur.execute(config.INSERT_CITY_COUNTRY, (trips[trip_id]['name'], trips[trip_id]['country']))
                        conn.commit()

                        cc_id = cur.lastrowid
                    else:
                        cc_id = cc_id[0]['id']

                    trips_list.append((trip_id, current_user_id, trips[trip_id]['trip_start'],
                                       trips[trip_id]['trip_length'], trips[trip_id]['trip_end'], cc_id))

            cur.executemany(config.INSERT_TRIPS_INFO, trips_list)
            conn.commit()
