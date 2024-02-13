from twitterscraper import query_tweets#name-twitterscraper

if __name__ == '__main__':
    #list_of_tweets = query_tweets("里神咕", 10)

    #print the retrieved tweets to the screen:
    for tweet in query_tweets("里神咕", 15):
        print(tweet)

    #Or save the retrieved tweets to file:
    file = open("output.txt", "w")
    for tweet in query_tweets("里神咕", 10):
        file.write(str(tweet.text.encode('utf-8')))
    file.close()
