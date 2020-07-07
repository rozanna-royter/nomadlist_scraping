from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import time
import utils
import config


def get_users_info(driver, usernames):
    """
    Main function for processing pages of users from usernames list.
    Uses selenium webdriver as well as beautiful soup.
    :param driver: The instantiated web driver
    :param usernames: List of user names
    :return: Dictionary of users' info
    """
    result = {}
    for username in usernames:
        utils.go_to_url(driver, f'{config.BASE_URL}/@{username}')
        time.sleep(config.USERS_WAITER)
        soup_html = BeautifulSoup(driver.page_source, 'html.parser')
        result[username] = {}

        result[username][config.NAMES_DICT["USER_ID"]] = soup_html.find(config.ATTRIBUTES_DICT["DIV_TAG"],
                                                                        class_=config.ATTRIBUTES_DICT["LIKE_USER"]
                                                                        )[config.ATTRIBUTES_DICT["USER_ID"]]

        for element in config.ELEMENTS_TO_PARSE:
            result[username][element] = get_text_from_info_bar(soup_html, element)

        result[username][config.NAMES_DICT["TRIP_LIST"]] = get_trips_selenium(driver)

        twitter_string = config.NAMES_DICT["TWITTER"]
        instagram_string = config.NAMES_DICT["INSTAGRAM"]
        result[username][twitter_string] = get_socials(driver, twitter_string)
        result[username][instagram_string] = get_socials(driver, instagram_string)

        result[username][config.NAMES_DICT["BIO"]] = soup_html.find(config.ATTRIBUTES_DICT["DIV_TAG"],
                                                                    class_=config.ATTRIBUTES_DICT["USER_BIO"]).text

        print_details(result[username], username)
    return result


def print_details(info, username):
    """
    Prints all collected data per user
    :param info: Dictionary of user info
    :param username: User name
    :return: None
    """
    print(f"Username: {username}\nNumber of followers: {info['follower-count']}\n"
          f"Following: {info['following-count']}\nNumber of trips: {info['trips-count']}\n"
          f"Distance traveled: {info['distance-traveled']}\nCountries visited: {info['countries-count']}\n"
          f"Cities visited: {info['cities-count']}\nTrip list: {info['trip_list']}\n"
          f"Twitter account: {info['twitter']}\nInstagram account: {info['instagram']}\n")


def get_trips_selenium(driver):
    """
    Returns trips info from current page using selenium (faster than bs4)
    :param driver: The instantiated web driver
    :return: Dictionary of trip info
    """
    trips = driver.find_elements_by_xpath(config.TRIPS_XPATH)
    trip_ids = [t.get_attribute(config.ATTRIBUTES_DICT["ID"]) for t in trips]
    trip_editor_string = config.NAMES_DICT["TRIP_EDITOR"]
    if trip_editor_string in trip_ids:
        trip_ids.pop(trip_ids.index(trip_editor_string))
    if '' in trip_ids:
        trip_ids.pop(trip_ids.index(''))
    try:
        expand_trips_btn = driver.find_element_by_xpath(config.BUTTON_EXPAND_ALL_TRIPS)
    except NoSuchElementException:
        expand_trips_btn = None
    if expand_trips_btn:
        expand_trips_btn.click()
    trips_dict = {}
    for tid in trip_ids:
        trips_dict[tid] = {}
        for element in config.TRIP_ELEMENTS:
            if element == config.NAMES_DICT["NAME"]:
                trips_dict[tid][element] = driver.find_element_by_xpath(
                    config.CITY_NAME_ELEMENT_XPATH.format(tid, element)).text
            else:
                trips_dict[tid][element] = driver.find_element_by_xpath(
                    config.TRIP_ELEMENT_XPATH.format(tid, element)).text
    return trips_dict


def get_socials(driver, sn_name):
    """
    Function for extracting social network information (i.e. Twitter and Instagram)
    :param driver: The instantiated web driver
    :param sn_name: Social network name
    :return: Social network username (if exists, else - None)
    """
    try:
        social_button = driver.find_element_by_xpath(
            config.GET_SOCIALS_XPATH.format(sn_name)).get_attribute(config.ATTRIBUTES_DICT["HREF"])
        if social_button:
            return social_button.split('/')[-1]
        else:
            return None
    except NoSuchElementException:
        return None


def get_text_from_info_bar(soup, el_name):
    """
    Function for extracting info from an element of info bar
    :param soup: Html of the page (BeautifulSoup)
    :param el_name: Element (class) name
    :return: Appropriate info by element name (if exists, else - None)
    """
    try:
        return soup.select_one(config.SELECT_CLASS_CONTAINS.format(el_name)).find(
            config.ATTRIBUTES_DICT["DIV_TAG"], attrs={config.ATTRIBUTES_DICT["CLASS"]: config.NAMES_DICT["NUMBER"]}
        ).text
    except AttributeError:
        return None


def log_in(driver):
    """
    Log in using a link
    :param driver: The instantiated web driver
    :return: None
    """
    utils.go_to_url(driver, config.LOGIN_URL)


def get_new_users(user_list, users_dict):
    """
    Returns a list of users that are present in user_list, but not present among the keys of users_dict
    :param user_list: Input list of users
    :param users_dict: Dictionary of users to check against
    :return: List of new users
    """
    res_list = []
    for u in user_list:
        if u not in users_dict.keys():
            res_list.append(u)
    return res_list


def user_info_extraction_cycle(driver, users_list):
    """
    Process of extracting user data of user_list and saving them to a file
    :param driver: The instantiated web driver
    :param users_list: List of user names
    :return: None
    """
    users_info_filename = config.USERS_INFO_FILENAME
    users_dict = {}
    if not config.START_FROM_TOP:
        try:
            users_dict = utils.read_dict_from_json(users_info_filename)
        except:
            users_dict = {}
        users_list = get_new_users(users_list, users_dict)
    if users_list:
        users_dict.update(get_users_info(driver, users_list))
        utils.write_dict_to_json(users_info_filename, users_dict)
        print(config.MSG_DICT["SAVING_USERS_COUNT"].format(len(users_list)))


def get_users_loop(driver, users_list):
    """
    Looping through sublists of users with extraction_cycle
    :param driver: The instantiated web driver
    :param users_list: List of user names
    :return: None
    """
    user_chunks = [users_list[x:x + config.USER_CHUNK_SIZE] for x in range(0, len(users_list), config.USER_CHUNK_SIZE)]
    i = 1
    for chunk in user_chunks:
        print(config.MSG_DICT["PROCESSING_USER_CHUNK"].format(i, len(user_chunks) + 1))
        user_info_extraction_cycle(driver, chunk)


def main():  # TODO: bad gateway
    driver = webdriver.Chrome(utils.get_chromedriver_path())
    driver.maximize_window()
    # log_in(driver)
    users_list = utils.read_list_from_file(config.USERS_LIST_FILENAME)
    # users_list = ['stephlizwalden', 'stacey', 'jlkruse', 'morganberger', 'tgrassin', 'okokstefan_', 'sean_c', 'markbrooks', 'matekovacs', 'gijsheerkens', 'kossnocorp', 'nikolagjorgji', 'camrabier', 'yal', 'realalexfortin', 'pauline', 'dekim24', 'lexrodba', 'nomadpauline', 'angel', 'anibal', 'allenpreneur', 'jcwesterbeek', 'haoxilu', 'pixel', 'phil79', 'colinw', 'jivings', 'gareththinker', 'adrianavecc', 'joelmattinson', 'chrisblaser', 'goshakkk', 'kbagoy', 'farazpatankar', 'maddcapp', 'jurn', 'joy_friberg', 'karen', 'skarloey17', 'stefankp', 'juliendevoir', 'dunjalazic', 'maul_of_america', 'travel_kane', 'mathieu', 'aking', 'philiplindberg', 'gregtoros', 'opryshok', 'krista', 'scottpants', 'michelealdrich', 'ambroisedebret', 'merongivian', 'kobvel', 'gabo', 'ricardomorgado', 'pmillerd', 'slocklin', 'grapescan', 'marlon_g', 'rxs', 'mialiou', 'camemco', 'piet', 'youryoungko', 'ppnlo', 'clementromeas', 'mestizo_blanco', 'kristof', 'sibsfinx', 'konstantin', 'adriaan', 'pmoorcraft', 'devdev', 'joetravels', 'cheepo2109', 'cjackson27', 'haydenjameslee', 'brianclark55', 'alexku', 'shawkshami', 'kamil_dziedzic', 'averyford', 'fernando_data', 'simoelalj', 'trevorgerhardt', 'lopesrosanna', 'netbe', 'maurizio', 'replay', 'philippi', 'ajlende', 'ovihentea', 'tmcgee', 'edu', 'petracca', 'keeg', 'mgstapleton', 'pandapenguin', 'luhman', 'damienfogg', 'jimmy_colina', 'rynesweeney', 'brody', 'markcaggiano', 'braddwyer', 'vladkorzinin', 'hass', 'erikbrits', 'jessehoogeboom', 'jessicaliske', 'jesperbylund', 'jelmerdeboer', 'joshuaballard', 'sofinewsham', 'yordanoff', 'aksenov', 'mrscul', 'tsirlucas', 'djelikya', 'gtmcknight', 'deltamagnet', 'wfxyz', 'alshch', 'matheus', 'beardzitski', 'lucaslsf', 'necmttn', 'verdiventures', 'cetitania', 'aaatelier_ejay', 'roelb', 'luisbeat', 'shridhar', 'tris', 'ryanipete', 'jlnfbr', 'luizaugusto', 'johnnyfdk', 'reboramuriel', 'nadiasotnikova', 'tomheartstacos', 'floriandarroman', 'bengoa', 'rayan', 'gilesadamthomas', 'alexanderlloyd', 'keithbaumwald', 'mneysa23', 'blair', 'jamiesyke', 'magicmagida', 'spen_taylor', 'davidzw', 'keiran', 'anastasia_mapr', 'ranajay', 'pawel', 'jessehanley', 'nomadtax', 'bastienpetit', 'whatshawsysays', 'trevormeier', 'scottyallen', 'rrsahara', 'lucialucha', 'juniow', 'jay11', 'anthony', 'archan', 'duncan_m', 'teeps_to', 'amber', 'mvremmerden', 'stefanfeser', 'axel', 'carolinesyrup', 'rosco', 'norbertdragan', 'zachetcetc', 'dvr87', 'ebconspicuous', 'meedamian', 'andyabramson', 'dwhart', 'alextourgis', 'jfkerr', 'gavin476', 'gubikmic', 'elirang', 'coorsleftfield', 'keenahn', 'jasonhatesjazz', 'montes', 'josefrousek', 'ptisunov', 'janneke', 'kaleiwhite', 'daniellauding', 'jon_snow_pt', 'developer', 'laetitbe', 'mariebriand', 'mikeslaats', 'charlesworthjc', 'adomasb', 'elyse', 'lorenzlk', 'danielletdesign', 'warp', 'jamalx31', 'camposped', 'nicolejfu', 'alexd', 'jon00042', 'deepen', 'danbeaumont', 'bracht', 'chmarti4', 'cbovis', 'bassochette', 'chrisdurlej', 'dobstotev', 'gyvastis', 'jimmy', 'eladnava', 'so', 'rcm7', 'naimashhab', 'sandra', 'stevensanseau', 'skywinder', 'willows_gate', 'meredal', 'phileap', 'stevelacey', 'iamlasse', 'jiami', 'luannalita', 'yuya_uzu', 'mr_freelo', 'cookiewhirls', 'ganapativs', 'tonyventura', 'ballew', 'jamescrowley', 'mrisoli', 'martn_st', 'carl', 'pranitgarg', 'michaelloistl', 'livian', 'me1001', 'viktorwrange', 'alanhalley', 'frankdilo', 'mikerubini', 'vgan', 'duraca', 'casper', 'mikipiki', 'stefanie', 'doweig', 'smartorana99', 'ashishexponential', 'maxpou', 'slybridges', 'ezakto', 'verekia', 'tuckertriggs', 'jenontherun', 'kblanqua', 'timea_albert', 'julianamundim', 'martinb3', 'joaocunha', 'aloysius', 'jetroidmakes', 'chicoxyzzy', 'leifg', 'xyliaburos', 'roncafferky', 'kirill', 'naii', 'luchesigui', 'jppotess', 'mick', 'stefco', 'bogdan', 'alexnapierholland', 'tuesdaygroup', 'izolate', 'spacewood', 'sethhunter', 'johngernon', 'sarahb', 'micha', 'itsmatthieu', 'kethle', 'klassicd', 'seb', 'jamess', 'hella_gela', 'joshuajansen', 'hope_freiheit', 'mathieutozer', 'tomjamesdj', 'phpman', 'mattgelgota', 'roks0n', 'ninoskopac', 'wernerhoffmann', 'maxceem', 'colus001', 'hennessy808', 'rylamvik', 'johi', 'dinomarkio', 'emanuelepascale', 'josephliu', 'simone_scarduzio', 'philippg', 'johnbrett_', 'joellepittman', 'shinsuke', 'nappels', 'marteletofe', 'merakijoe', 'bern', 'gnikolas', 'meswarb', 'polinakocheva', 'zachcarrier', 'tvrhe', 'joncrawford', 'nomadbubble', 'dohertyjf', 'iamfledge', 'yangwao', 'simmschanita', 'jowilki', 'awallace', 'sadovnychyi', 'matousvins', 'kytwb', 'kolyo', 'damn', 'naz', 'return_true', 'kathleenhamilton', 'b_angpow', 'eammilsom', 'manacespereira', 'sanna', 'akeylimepie', 'charlottec', 'daniorq', 'jcleung', 'jeru', 'mrmading', 'jesper', 'psylvain324', 'ujutka', 'petersanchez', 'msaintcr', 'renee', 'arcaballero', 'mmmiller', 'whatthezach', 'quintinjadam', 'andrewgulik', 'dccb', 'separo', 'louisebhou', 'pauuu', 'jon_a', 'mariangoia', 'mickmick', 'adamaveray', 'patelkrystal', 'evan205', 'martinqz', 'sergiosa_la', 'lukenomadic', 'lucozade', 'lisarobynkeown', 'goodforenergy', 'adventureinmyveins', 'sebastienbarbier', 'mikewilltravel', 'livinextreme', 'vadymzh', 'godfoca', 'yamilurbina', 'patricksearle', 'mattyg', 'angie', 'paulohp', 'ed', 'timoteo', 'travmonkey', 'khodl', 'manuel_rojas_konkol', 'johannestvedt', 'sdullink', 'remy', 'jasongalvin', 'karelemck', 'blingless', 'allbombs', 'samshull', 'danroc', 'anthonycastrio', 'sebastian88', 'shoinwolfe', 'lenilsonjr', 'nickdanforth', 'bobgubko', '30andawakeup', 'belle_88', 'austinknight', 'davidrevoledo', 'erikbenjamin', 'taskett', 'florianbuerger', 'adamsimms', 'gvrizzo', 'attila', 'parasight', 'guar47', 'jamesd', 'anniestrout', 'bnchrch', 'yeeling', 'naathaan', 'madeddie', 'kirikiri', 'justinvz', 'oliviasuguri', 'deensel', 'radutudorie', 'adamnowek', 'phil', 'kenny', 'lianturc', 'nomadwanderer', 'k8ts11sara', 'jordnfk', 'emeliefagel', 'orestes', 'lhr0909', 'naumank', 'tibzback', 'gerhard', 'senorcodecat', 'bhullnatik', 'veryfyodor', 'darceybeau', 'momciloo', 'paulbohm', 'shastified', 'marcantoinefon', 'sanderfish', 'shadiosta', 'kaaist', 'luciddan', 'landen04', 'nomadnocry', 'gietema', 'muaddib', 'dhead', 'aileencgn', 'ivangudz', 'echowave', 'johnnymakes', 'jodroc', 'aakashdhuna', 'mqt', 'riichardmoody', 'videosushiroll', 'dennisvdalen', 'jasonc', 'dominikd', 'erikfrisk', 'jaredmason', 'thomas', 'tpechenina', 'veeraan', 'tinodeb', 'iramalama', 'jani', 'zakerving', 'yliasm', 'your.wordsmith', 'yovko', 'erkl', 'joehcooper', 'pri143u', 'diegonalvarez', 'skashevko', 'mattlewis92', 'joshwardini', 'swiftynomad', 'joelrunyon', 'nomadichoopla', 'wolvegames', 'jyarnallschane', 'individual8', 'bneiluj', 'tgurvicius', 'heverton', 'drorliebenthal', 'renanfelix', 'dinkydani', 'dmitriyabr', '1hakr', 'egorev', 'ralphius', 'shutsen', 'nickswider', 'paveldogreat', 'yildizalidzhikova', 'benrellick', 'andrewcross7', 'marksan', 'mjordan221', 'abarbar', 'giacomodangelo', 'anastasia', 'lonnylot', 'yurisilva', 'adsieg01', 'rosirodrigues', 'mtremmert', 'jb', 'jonli', 'taticonqueso', 'maratryndin', 'nathanjones', 'threadalist', 'akberkhan2121', 'carly_io', 'pj_manning', 'tristantennant', 'mrsergejl', 'cbridges', 'samhogg', 'tomek901', 'volodymyr_sadykov', 'fluidsonic', 'bastienbricout', 'sergioestrella', 'joseferrer', 'kellie', 'flowdee', 'jonsunandco', 'zackyoung', 'niklaslavrell', 'courtneyc', 'theitalianguy', 'internetjohnny', 'woahitsraj', 'aaleksandar', 'alainschlesser', 'craigfer', 'thomasagarate', 'divesamui', 'hafifuyku', 'nolan_brady', 'benmercer', 'gianlucaorlandi', 'nmai', 'vlafiser', 'hjunkim', 'karim', 'susanc', 'hyobii', 'vconde', 'sunny_cloud', 'klemenselakovic', 'davidfoong', 'maxzahariadis', 'sweaver', 'prakhar', 'antonniklasson', 'gogogodinez', 'johana', 'bsingbeil', 'ashleystonedrum', 'jd_s', 'cyndidawes', 'mcpete716', 'hunterpine', 'woutervr', 'woodiescaptain', 'paulbremer', 'tanjas', 'jackiegrag', 'wojtek', 'atktravels', 'manuk', 'patte', '_kieranmg', 'johan718', 'nethunter', 'nderkach', 'chaparronati', 'wattson12', 'roadwarrior', 'micah_w', 'barbaralicious', 'henningtegen', 'adammo', 'kerwood', 'flo', 'mattburman', 'seanwessmith', 'histreasurehunt', 'neoromantic', 'krsjoseph', 'anigupta', 'warrington11', 'annamcphee3', 'nicolas', 'bengen343', 'rebecca', 'cessperience', 'mtr19', 'aleksrk', 'watzing', 'thatuxdude', 'alxcnwy', 'niklasmodess', 'bruno706', 'aswinkp', 'pmilos99', 'louroboros', 'brmolin', 'jade', 'kjzz', 'zkumar', 'martinstenius', 'pianojukebox', 'tomaslau', 'keithkunz2', 'johnconnelly', 'asierlaukoa', 'failednormal', 'italo', 'alexiscreuzot', 'pjmurray', 'zigor_uriarte', 'craigcarlyle', 'yusuf_raza', 'raz', 'roseeppensteiner', 'katekendall', 'sharon', 'rubentdlh', 'danielbeck', 'bratta', 'steviezollo', 'karinaprosto', 'diemesleno', 'vlad', 'brucemarsh', 'herrobear', 'artbalsam', 'jules', 'nevslu', 'nomadlist399', 'michaltakac', 'marimalari', 'ryanchatterton', 'alex_sid', 'anthonyarden', 'alexanderbach', 'lucasmorello', 'illyism', 'jivins11', 'landland', 'nickpellant', 'obiefernandez', 'chilladx', 'vit_lastovka', 'maennchen', 'billey_b', 'patrick_mtl', 'fernand0moreira', 'clementsauvage', 'patrickbolle', 'pawsin2worlds', 'nickyborry', 'valia_walsk', 'shiori_nakajima', 'aditya', 'orenkurve', 'checkyourfuel', 'hfauq', 'val', 'nivvenkatesh', 'nickz', 'tevi', 'mikemjharris', 'sdnorton', 'reganha', 'francoisx', 'seniornomad', 'aymorgan', 'bjorn', 'iam', 'albertjllo', 'mariasokolova', 'campion', 'jsoklevski', 'erwin', 'allanvadham', 'rcrocker13', 'anytiffng', 'dimitrieh', 'sammyschuckert', 'ponchik', 'karljanisse', 'matthewspear', 'loule_j', 'morenus', 'that_chapp', 'camerondare', 'shanemcdermed', 'jennapotter6', 'jacopocascioli', '9102180', 'murillo', 'timhc22', 'dylan', 'enilsen016', 'davidgsylvia', 'andor', 'alfredo', 'ramon_g', 'ivanderbyl', 'iambenmay', 'breelig', 'ivanrigovsky', 'rdoyle99', 'larkin_nz', 'julianx', 'bibz', 'shylands', 'cavaton', 'jacquievchang', 'andrewy', 'serialblogamist', 'dvpita', 'mfrezz', 'grapplerulrich', 'christensentr', 'djoneverett', 'dgioulakis', 'vesper8', 'magnusalber', 'underyx', 'blured2000', 'ygalescot', 'pym', 'rockyrohde', 'melissawashin', 'nickpost', 'soulbait', 'timwhite', 'mefynn', 'samirajil', 'phil474', 'emrearan', 'tamatomoca', 'aidenbuis', 'nico_lrx', 'mary_oleksiuk', 'willc', 'eduardoborges', 'heikoco', 'flavialippi', 'kymellis', 'cso', 'atu', 'sheenan', 'majkel', 'tonyschmidt', 'seantempesta', 'sergio', 'martavit', 'linuz90', 'ryanleroux', 'grantbartel', 'velvetsand', 'cdk48', 'jasonbryant', 'gillianim', 'harrytucker', 'carosimon', 'pier', 'gaborsch', 'alexis_ouellet', 'enaros', 'ryanarthur', 'luciazw', 'jupiterandthegiraffe', 'spillere', 'horacio', 'tomchentw', 'swynt', 'rjarram', 'aczuleta', 'gilesbutler', 'malban127', 'atkit', 'stevenyilin', 'refuseillusion', 'ajmcgrath', 'jnpkr', 'petr_suska', 'tobi', 'rzdgodoy', 'astronautameya', 'heyangty', 'samclaassen', 'nunoarruda', 'kks', 'domas', 'thecocoanomad', 'jasonchiv', 'francescocarlucci', 'bastienfp', 'angelicism', 'gert_schreuder', 'clebercosta', 'jonnym1ller', 'burisu', 'lukasfingerle', 'tmaximini', 'olgavorona', 'robkale', 'llum', 'rasmuskroner', 'jezfx', 'cheraff', 'definegravity', 'calum', 'jankmeyer', 'harrisroberts', 'dogukanio', 'andreyazimov', 'm322', 'andykassier', 'bradzickafoose', 'rene', 'joytravels', 'beeman', 'jenmikh', 'novacoski', 'thelifeofjord', 'martintravels', 'heathhlee', 'twahlin', 'xoelipedes', 'rrppspain', 'leticiam0', 'screamingbox', 'arlton', 'lucsucces', 'anderkd', 'bryantmichaelhuether', 'jodiana', 'metamas', 'matei', 'wimgz', 'jackveiga', 'justin_butlion', 'wimdodson', 'trybradley', 'sa_cha', 'ohenrik', 'phaberest', 'couturelp', 'diannamallen', 'sarbogast', 'joeyfenny', 'wooster', 'clubturps', 'askl56', 'mironovartyom', 'lise', 'svenvdz', 'austin', 'dan_k', 'vas3k', 'daniellockyer', 'sebu', 'fredperrotta', 'legomyeggo', 'steph_danforth', 'noreaster360', 'danielzarick', 'andreassundman', 'charlestravers', 'ikbenhye0', 'greys', 'mnlfrgr', 'chrisrdodd', 'marcuschristiansen', 'chrisspiegl', 'bryanaka', 'messiermorgan', 'john', 'danielaf', 'marsty5', 'dylan_hey', 'dream', 'stephenwalker', 'dannypostma', 'samueldelesque', 'kellymsheridan', 'davidlorincz', 'mrtkawa', 'reen', 'janna', 'the_idyll_exile', 'emsu', 'empireflippers', 'oahourai', 'inessadoud', 'gridinoc', 'd_btlr', 'naim', 'artpi', 'vladtamas', 'jennzajac', '10kjuan', 'abbygmcclain', 'cmendes0101', 'anhphan', 'spextr', 'sapio', 'thomastullis', 'jeffermtl', 'zacyap', 'zerger', 'fredrivett', 'pierregillesleymarie', 'iamjamesrodgers', 'julia', 'rgeorgia_', 'facundo', 'stephsmith', 'espenmalling', 'moloneymb', 'yavor', 'kevinjamesparks', 'martindonadieu', 'paulevans85', 'jessgenevieve', 'xnutsive', 'gleb', 'antoine', 'snowgraphs', 'ingoworkstyles', 'katy', 'adimov', 'zhurbinchik', 'butkeviciusv', 'laird_evan', 'bosco', 'simondob', 'patwalls', 'sari', 'jacobjay', 'jojomunroro', 'superamit', 'chrisdengso', 'bryanjschaaf', 'dannybooboo', 'svanevik', 'paulh', 'thereseg', 'ainsley', 'melaniecibura', 'doctordan', 'dan_e_gray', 'ankitgoel', 'mariakinoshita', 'julesmarie', 'evaneustace', 'tiojoca', 'jonathanpoh', 'pam', 'whosdustin', 'c4augustus', 'maaria', 'lorism', 'eyobest', 'aleks_muse', 'noahnomad', 'lilian', 'ksellers', 'christianoliveira', 'blombergvictor', 'gracjan_grala', 'indi', 'mihaela', 'flormolla']
    # users_list = ['haoxilu', 'phil79']
    if config.SAVE_MID_RESULTS:
        get_users_loop(driver, users_list)
    else:
        user_info_extraction_cycle(driver, users_list)
    time.sleep(config.GENERAL_WAITER)
    driver.quit()


if __name__ == '__main__':
    main()



