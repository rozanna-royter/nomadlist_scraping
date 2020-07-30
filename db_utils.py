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

        try:
            with conn.cursor() as cur:
                if username not in existing_users_dict.keys():

                    cur.execute(config.INSERT_SCRAPED_INFO,
                                (user_info['user_id'], username, user_info['follower-count'], user_info['following-count'],
                                 user_info['trips-count'], user_info['distance-traveled'], user_info['countries-count'],
                                 user_info['cities-count'], user_info['twitter'], user_info['instagram'], user_info['bio'])
                                )
                    conn.commit()
                    current_user_id = cur.lastrowid

                    twitter_details = user_info['twitter_details']
                    if twitter_details:
                        cur.execute(config.INSERT_TWITTER_INFO,
                                    (current_user_id, twitter_details['id_str'], twitter_details['screen_name'],
                                        twitter_details['location'], twitter_details['description'],
                                        twitter_details['followers_count'], twitter_details['friends_count'],
                                        twitter_details['favourites_count'], twitter_details['verified'],
                                        twitter_details['statuses_count']
                                     )
                                    )
                        conn.commit()

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

                    twitter_details = user_info['twitter_details']

                    if twitter_details:
                        query_tw = config.SELECT_TWITTER_USER.format(current_user_id)
                        cur.execute(query_tw)
                        tu_id = cur.fetchall()

                        if not tu_id:
                            cur.execute(config.INSERT_TWITTER_INFO,
                                        (current_user_id, twitter_details['id_str'], twitter_details['screen_name'],
                                         twitter_details['location'], twitter_details['description'],
                                         twitter_details['followers_count'], twitter_details['friends_count'],
                                         twitter_details['favourites_count'], twitter_details['verified'],
                                         twitter_details['statuses_count']
                                         )
                                        )
                            conn.commit()

                        else:
                            cur.execute(config.UPDATE_TWITTER_INFO,
                                        (twitter_details['id_str'], twitter_details['screen_name'],
                                         twitter_details['location'], twitter_details['description'],
                                         twitter_details['followers_count'], twitter_details['friends_count'],
                                         twitter_details['favourites_count'], twitter_details['verified'],
                                         twitter_details['statuses_count'], current_user_id
                                         )
                                        )
                            conn.commit()

                trips_query = config.SELECT_TRIPS.format(current_user_id)
                cur.execute(trips_query)
                existing_trips = cur.fetchall()
                existing_trips_ext_ids = [t['external_id'] for t in existing_trips]
                for trip_id in trips:
                    if trip_id not in existing_trips_ext_ids:

                        cur.execute(config.SELECT_CITY_COUNTRY, (trips[trip_id]['name'], trips[trip_id]['country']))
                        cc_id = cur.fetchall()

                        if not cc_id:

                            query2 = config.SELECT_COUNTRY
                            cur.execute(query2, trips[trip_id]['country'])
                            country_id = cur.fetchall()

                            if not country_id:
                                cur.execute(config.INSERT_COUNTRY, (trips[trip_id]['country']))
                                conn.commit()
                                country_id = cur.lastrowid
                            else:
                                country_id = country_id[0]['id']

                            cur.execute(config.INSERT_CITY_COUNTRY,
                                        (trips[trip_id]['name'], country_id)
                                        )
                            conn.commit()

                            cc_id = cur.lastrowid
                        else:
                            cc_id = cc_id[0]['id']

                        trips_list.append((trip_id, current_user_id, trips[trip_id]['trip_start'],
                                           trips[trip_id]['trip_length'], trips[trip_id]['trip_end'], cc_id))

                cur.executemany(config.INSERT_TRIPS_INFO, trips_list)
                conn.commit()
        except pymysql.err.InternalError as error:
            print('error in sql. user: ', username)
            print('dict: ', user_info)
            print(error)
