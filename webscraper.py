import login
import tweets

if __name__ == '__main__':
    bearer = login.authorization()
    tweets.writeTodayTweets(bearer)

