import json
import re
from textblob import TextBlob
import pandas as pd
import matplotlib.pyplot as plt
import os,platform
import sys

pd.set_option('display.max_colwidth',None) #Pour afficher entierement les listes des fonctions d'analyse dans le dataframe


#------------------------------------------------INITIALISATION------------------------------------------------------------------------#

with open(r"Base_tweet_data.json", "r", encoding="utf-8") as versailles_tweets:
    data =json.load(versailles_tweets)

zone_write = open("Zone d'aterrissage.json", 'w')

#----------------------------------------------------CLASSE--------------------------------------------------------------------#

class Tweet:

    def extract_topics(tweet):
        if 'topics' in tweet.keys():
            return tweet['topics']
        else:
            return 'No topics in this tweet'

    def extract_sentiment(text):
        blob = TextBlob(text)
        sentiment = blob.sentiment
        return sentiment


    def __init__(self,tweet):
        regex_mentions = re.compile(r'\B@[a-zA-Z0-9\b]+')
        regex_hash = re.compile(r'\B#[a-zA-Z0\b]+')
        self.author = tweet['autheur']
        self.text = tweet['text']
        self.topics = (', '.join((Tweet.extract_topics(tweet)).keys())if Tweet.extract_topics(tweet) != 'No topics in this tweet' else Tweet.extract_topics(tweet))
        self.hashtags = (', '.join(re.findall(regex_hash,self.text))if re.findall(regex_hash,self.text) else 'No hashtags in this tweet')
        self.mentions = (', '.join(re.findall(regex_mentions,self.text))if re.findall(regex_mentions,self.text) else 'No mentions in this tweet')
        self.sentiment = Tweet.extract_sentiment(self.text)

#--------------------------------------------------FONCTIONS POUR TRAITEMENT DE DONNEES----------------------------------------------------------------------#

def extract_mentions(text,index):
    dico = {}
    regex_mentions = re.compile(r'\B@[a-zA-Z0-9\b]+')
    mentions = re.findall(regex_mentions, text)
    if mentions == []:
        return 'No mentions in this tweet'
    else:
        for el in mentions:
            dico[el] = {'count':1,'tweets_ids':[index]}
        return dico


def extract_hashtags(text,index):
    dico ={}
    regex_hash = re.compile(r'\B#[a-zA-Z0\b]+')
    hashtags = re.findall(regex_hash,text)
    if hashtags == []:
        return 'No hashtags in this tweet'
    else:
        for el in hashtags:
            dico[el] = {'count':1,'tweets_ids':[index]}
        return dico


def count_topics(tweet_topics_section):
    topic_count = {}

    for item in tweet_topics_section:
        domain = item['domain']
        if 'name' in domain:
            topics = domain['name']
        topic_count[topics] = 1
    return(topic_count)


def add_dico_v1(dico,dico_added):
    for key in dico_added:
        if key in dico:
            dico[key] += dico_added[key]
        else:
            dico[key] = dico_added[key]
    return dico

def add_dico_v2(dico,dico_added):
    for key in dico_added:
        if key in dico:
            dico[key]['count'] += dico_added[key]['count']
            dico[key]['tweets_ids'].extend(dico_added[key]['tweets_ids'])

        else:
            dico[key] = dico_added[key]
    return dico


def sort_topics(dico):
    return dict(sorted(dico.items(), key= lambda x: x[1], reverse= True))

def sort_others(dico):
    return dict(sorted(dico.items(), key= lambda x: x[1]['count'], reverse= True))

#---------------------------------------------------FONCTION QUI FAIT LE NETOYAGE---------------------------------------------------------------------#

def cleaning(data):
    all_tweets = []
    dico_mentions = {}
    dico_hashtags = {}
    dico_autheurs = {}
    dico_topics = {}
    for i in range(len(data)):
        tweet = {}
        regex_emojis = re.compile('[^\x00-\xFF]+', flags=re.UNICODE)

        tweet['autheur'] = data[i]['author_id']
        tweet['text'] = regex_emojis.sub(r'',data[i]['text'])
        tweet['topics'] = count_topics(data[i]['context_annotations']) if 'context_annotations' in data[i].keys() else 'No topics in this tweet'
        tweet['mentions'] = extract_mentions(tweet['text'],i)
        tweet['hashtags'] = extract_hashtags(tweet['text'],i)
        
        dico_autheurs = (add_dico_v2(dico_autheurs,{tweet['autheur'] : {'count' : 1, 'tweets_ids' : [i]}}))
        dico_topics = (add_dico_v1(dico_topics,tweet['topics']) if tweet['topics'] != 'No topics in this tweet' else dico_topics)
        dico_hashtags = (add_dico_v2(dico_hashtags,tweet['hashtags']) if tweet['hashtags'] != 'No hashtags in this tweet' else dico_hashtags)
        dico_mentions = (add_dico_v2(dico_mentions,tweet['mentions']) if tweet['mentions'] != 'No mentions in this tweet' else dico_mentions)


        tweet = dict(sorted(tweet.items())) # non necessaire
        all_tweets.append(tweet)
    

    all_tweets.append(sort_others(dico_hashtags))
    all_tweets.append(sort_others(dico_mentions))
    all_tweets.append(sort_others(dico_autheurs))
    all_tweets.append(sort_topics(dico_topics))
    json.dump(all_tweets, zone_write, indent=4, separators=(',',': '))
    zone_write.close()

cleaning(data)



#----------------------------------------------------------REOUVERTURE DU FICHIER EN READ ET CHOIX DE L'ACTION--------------------------------------------------------------#

with open (r"cleaned_tweet_data.json","r") as zone_read:
    file = json.load(zone_read)
tweet = None

#--------------------------------------------------FONCTIONS BASIQUES----------------------------------------------------------------------#

topics,autheurs,mentions,hashtags = file[-1],file[-2],file[-3],file[-4]

def dataframe(dict):
    return pd.DataFrame.from_dict(dict,orient='index')

def clean_crochets(df,clé):
    return df[clé].apply(lambda x: ', '.join(map(str, x)) if x else 'No values')

def clear():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system("clear")

def afficher_menu():
    clear()
    print("     ECRAN D'OPTIONS D'ANALYSE\n\n")
    return

def afficher_main():
    clear()
    print("     ECRAN D'ACCEUIL\n\n")
    return

def pie_chart(df,name):
    plt.figure(figsize=(10,6))
    df['count'].plot.pie(labels=df.index, autopct='%1.1f%%', colors=plt.cm.Paired.colors, startangle=90)
    plt.title(f"Nombre de Publications par {name}")
    plt.ylabel('')
    plt.tight_layout()
    plt.show()

def bar_graph(val,df,clé):
    plt.figure(figsize=(10, 6))
    plt.bar(df.index, df['count'], color='skyblue')
    plt.title(f"Top {val} {clé}", fontsize=16)
    plt.xlabel(clé, fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()



def afficher_tweet(entrée):
    tweet = Tweet(file[int(entrée)-1])
    clear()
    print(f"Tweet selectionné: {entrée}\n")
    print(f"Autheur du tweet: {tweet.author}\n")
    print(f"Contenu du tweet: {tweet.text}\n")
    print(f"Topics du tweet: {tweet.topics}")
    print(f"Hashtags du tweet: {(tweet.hashtags)}")
    print(f"Mentions du tweet: {(tweet.mentions)}\n")
    print(f"Sentiment du tweet: {tweet.sentiment}\n")
    return 


#--------------------------------------------------FONCTIONS POUR L'ANALYSE DE DONNEES (TOPS)----------------------------------------------------------------------#

def tops():
    list_tops = ["Top hashtags: '1'","Top utilisateurs: '2'","Top mentionnés: '3'","Top sujets: '4'"]
    list_tops_func = [topk_hashtags,topk_users,topk_mentions,topk_topics]
    choix = input(f"Quel top voulez vous choisir parmis {list_tops}, entrez 'menu' pour retourner sur les opérations ou encore 'exit' pour quitter le programme:\n>>> ")
    if choix.upper() == 'MENU':
        afficher_menu()
        return
    elif choix.upper() == 'EXIT':
        print('Thanks for trying this database Analysis tool and Goodbye !')
        exit()         
    elif not choix.isdigit() or int(choix)-1 not in range(len(list_tops)):
        clear()
        print("OPERATION EN COURS: Tops: '8'\n")
        print("Selectionnez un Top dans la liste grâce a l'indice indiqué.\n")
        tops()
        return
    else:
        list_tops_func[int(choix)-1]()
        tops()
    return 

def topk_hashtags():
    entrée_topk_hashtags = input(f"Donnez le nombre du top que vous souhaitez voir (max: {len(hashtags.keys())}):\n>>> ")
    
    if not entrée_topk_hashtags.isdigit() or int(entrée_topk_hashtags) <= 0:
        print("Veuillez entrer un nombre valide.")
        topk_hashtags()
        return 
    k = int(entrée_topk_hashtags)
    df = dataframe(hashtags)
    df = df.head(k)
    bar_graph(k,df,"Hashtags")
    return

def topk_users():
    entrée_topk_users = input(f"Donnez le nombre du top que vous souhaitez voir (max: {len(autheurs.keys())}):\n>>> ")
    if not entrée_topk_users.isdigit() or int(entrée_topk_users) <= 0:
        print("Veuillez entrer un nombre valide.")   
        topk_users()
        return
    k = int(entrée_topk_users)
    df = dataframe(autheurs)
    df = df.head(k)
    bar_graph(k,df,"Autheurs")
    return 


def topk_mentions():
    entrée_topk_mentions = input(f"Donnez le nombre du top que vous souhaitez voir (max: {len(mentions.keys())}):\n>>> ")
    if not entrée_topk_mentions.isdigit() or int(entrée_topk_mentions) <= 0:
        print("Veuillez entrer un nombre valide.")
        topk_mentions()
        return
    k = int(entrée_topk_mentions)
    df = dataframe(mentions)
    df = df.head(k)
    bar_graph(k,df,"Mentions")
    return 

def topk_topics():
    entrée_topk_topics = input(f"Donnez le nombre du top que vous souhaitez voir (max: {len(topics.keys())}):\n>>> ")
    if not entrée_topk_topics.isdigit() or int(entrée_topk_topics) <= 0:
        print("Veuillez entrer un nombre valide.")
        return topk_topics()
    
    k = int(entrée_topk_topics)
    df = pd.DataFrame.from_dict(topics, orient='index', columns=['count'])
    df = df.head(k)
    bar_graph(k,df,"Topics")
    return

#--------------------------------------------------FONCTIONS POUR L'ANALYSE DE DONNEES (AUTRES QUE TOPS)----------------------------------------------------------------------#


def nb_pbs_autheurs(): # FONCTION 1   #renvoi le nombre de publications par autheurs (dataframe + piechart)
    df = dataframe(autheurs)
    df.index.name = "Autheur"
    print(df[['count']])
    pie_chart(df,"Autheurs")
    return

def nb_pbs_topics(): # FONCTION 2   #renvoi le nombre de publications par sujet (dataframe + piechart)
    df = pd.DataFrame.from_dict(topics,orient='index',columns=['count'])
    df.index.name = "Topic"
    print(df)
    pie_chart(df,"Sujets")
    return

def nb_pbs_hashtags(): # FONCTION 3   #renvoi le nombre de publications par hashtag (dataframe + piechart)
    df = dataframe(hashtags)
    df.index.name = "Hashtag"
    print(df[['count']])
    pie_chart(df,"Hashtags")
    return


def tweets_by_mentions(): # FONCTION 4   #renvoi les tweets dans lesquels il y a la mention choisit (liste)
    choix_mention = input(f"Selectionnez une mention parmis les suivantes pour l'opération ou entrez 'menu' pour retourner sur la selection d'opérations {[(id,name) for id,name in enumerate(mentions.keys())]}:\n>>> ")
    clear()
    print("OPERATION EN COURS: Ensemble de tweets mentionnant un utilisateur spécifique: '4'\n\n")
    if choix_mention.upper() == 'MENU':
        afficher_menu()
        return
    elif choix_mention.upper() == 'EXIT':
        exit()
    elif not choix_mention.isdigit() or int(choix_mention) not in range(len(mentions.keys())):
        clear()
        print("OPERATION EN COURS: Ensemble de tweets mentionnant un utilisateur spécifique: '4'\n\n")
        print("\n Choisissez une valeur comprise dans les mentions:\n")
        return tweets_by_mentions()
        
    else:
        choix_mention = list(mentions.keys())[int(choix_mention)]
        tweets = [(tweet_id, file[tweet_id]) for tweet_id in mentions[choix_mention]['tweets_ids']]
        print("Voici les tweets trouvés :")
        for tweet_id, tweet_content in tweets:
            print(f"- Tweet n°{tweet_id+1}, : '{tweet_content['text']}'\n")
        return tweets_by_mentions()
        


def tweets_by_author(): # FONCTION 5   #renvoi les tweets écrits par un autheur choisit (liste)
    choix_autheur = input(f"\nSelectionnez un autheur parmis les suivants pour l'opération ou entrez 'menu' pour retourner sur la selection d'opérations {[(id,name) for id,name in enumerate(autheurs.keys())]}:\n>>> ")
    clear()
    print("OPERATION EN COURS: Ensemble de tweets d'un utilisateur spécifique: '5'\n\n")
    if choix_autheur.upper() == 'MENU':
        afficher_menu()
        return
    elif choix_autheur.upper() == 'EXIT':
        exit()
    elif not choix_autheur.isdigit() or int(choix_autheur) not in range(len(autheurs.keys())):
        clear()
        print("OPERATION EN COURS: Ensemble de tweets d'un utilisateur spécifique: '5'\n\n")
        return tweets_by_author()
    else:
        choix_autheur = list(autheurs.keys())[int(choix_autheur)]
        tweets = [(tweet_id, file[tweet_id]) for tweet_id in autheurs[choix_autheur]['tweets_ids']]
        print('Voici les tweets trouvés :')
        for tweet_id, tweet_content in tweets:
            print(f"- Tweet n°{tweet_id+1}, : '{tweet_content['text']}'\n")
        return tweets_by_author()
    

def users_hashtaging(): # FONCTION 6   #renvoi la liste des utilisateurs ayant tweeté un hashtag choisit (liste)
    choix_hashtag = input(f"\nSelectionnez un hashtag pour l'opération parmis les suivants ou entrez 'menu' pour retourner sur la selection d'opérations {[(id,name) for id,name in enumerate(hashtags.keys())]}:\n>>> ")
    clear()
    print("OPERATION EN COURS: Utilisateurs mentionnant un hashtag spécifique: '6'\n\n")
    if choix_hashtag.upper() == 'MENU':
        afficher_menu()
        return
    elif choix_hashtag.upper() == 'EXIT':
        exit()
    elif not choix_hashtag.isdigit() or int(choix_hashtag) not in range(len(autheurs.keys())):
        clear()
        print("OPERATION EN COURS: Utilisateurs mentionnant un hashtag spécifique: '6'\n\n")
        return users_hashtaging()
    else:
        choix_hashtag = list(hashtags.keys())[int(choix_hashtag)]
        tweets = [(tweet_id, file[tweet_id]) for tweet_id in hashtags[choix_hashtag]['tweets_ids']]
        print("Voici les tweets trouvés :")
        for tweet_id, tweet_content in tweets:
            print(f"\n- Tweet n°{tweet_id+1}, autheur: '{tweet_content['autheur']}'")
        return users_hashtaging()


def users_mentionned_by(): # FONCTION 7   #renvoi un set(pas de doublons) des utilisateurs mentionnés par un autheur choisit
    choix_mentionneur = input(f"\nSelectionnez un hashtag pour l'opération parmis les suivants ou entrez 'menu' pour retourner sur la selection d'opérations {[(id,name) for id,name in enumerate(autheurs.keys())]}:\n>>> ")
    clear()
    print("OPERATION EN COURS: Utilisateurs mentionnés par un utilisateur spécifique: '7'\n\n")
    if choix_mentionneur.upper() == 'MENU':
        afficher_menu()
        return
    elif choix_mentionneur.upper() == 'EXIT':
        exit()
    elif not choix_mentionneur.isdigit() or int(choix_mentionneur) not in range(len(autheurs.keys())):
        clear()
        print("OPERATION EN COURS: Utilisateurs mentionnés par un utilisateur spécifique: '7'\n\n")
        return users_mentionned_by()
    else:
        choix_mentionneur = list(autheurs.keys())[int(choix_mentionneur)]
        tweets = [(tweet_id, file[tweet_id]) for tweet_id in autheurs[choix_mentionneur]['tweets_ids']]
        print("Voici les tweets trouvés :")
        for tweet_id, tweet_content in tweets:
            if tweet_content['mentions'] != 'No mentions in this tweet':
                print(f"\n- Tweet n°{tweet_id+1}, mentions: \"{', '.join(tweet_content['mentions'].keys())}\"")
        return users_hashtaging()



#---------------------------------------------------------CENTRE DES COMMANDES DES FONCTIONS D'ANALYSE (interface)---------------------------------------------------------------#

opérations = ["Nombre de publications par utilisateur: '1'","Nombre de publications par topics: '2'","Nombre de publications par hashtags: '3'",
              "Ensemble de tweets mentionnant un utilisateur spécifique: '4'","Ensemble de tweets d'un utilisateur spécifique: '5'",
              "Utilisateurs mentionnant un hashtag spécifique: '6'","Utilisateurs mentionnés par un utilisateur spécifique: '7'","Tops: '8'"]

fonctions = [nb_pbs_autheurs,nb_pbs_topics,nb_pbs_hashtags,tweets_by_mentions,tweets_by_author,users_hashtaging,users_mentionned_by,tops]


def menu_screen():

    entrée_function = input(f"Choisir une opération parmis\n{opérations},\n ou bien entrez 'main' pour retourner sur l'affichage principal ou encore 'exit' pour quitter le programme:\n>>> ") 
    if entrée_function.upper() == 'MAIN' :
        afficher_main()
        main_screen()
    elif entrée_function.upper() == 'EXIT':
        clear()
        print('Thanks for trying Inpoda database Analysis and Goodbye !')
        exit()                
    elif entrée_function.isdigit() == False:
        afficher_menu()
        print("Veuillez entrer un chiffre correspondant aux opérations ou 'exit' pour sortir.\n")
        menu_screen()

    if entrée_function.isdigit():
        entrée_function = int(entrée_function)
        if 0 < entrée_function <= len(opérations):
            clear()
            print(f"OPERATION EN COURS: {opérations[entrée_function-1]}\n")
            fonctions[entrée_function-1]()
            menu_screen()
        else:
            print("Veuillez saisir une opération valide: entrez le nombre correspondant aux opérations: \n")
            menu_screen()


def main_screen():
    entrée = input(f"Choisissez un Tweet (de 1 à {len(file)-4}) , entrez 'menu' pour les opérations ou 'exit' pour quitter le programme:\n>>> ")

    if entrée.upper() == 'MENU':
        afficher_menu()
        menu_screen()
    elif entrée.upper() == 'EXIT':
        clear()
        print('Thanks for trying this database Analysis tool and Goodbye !')
        exit()        
    elif not entrée.isdigit() or int(entrée)-1 < 0 or int(entrée) > len(file)-4 :
        afficher_main()
        print("Veuillez entrer une valeure valide")
        return main_screen()
    else:
        afficher_tweet(entrée)
        main_screen()


afficher_main()
main_screen()

