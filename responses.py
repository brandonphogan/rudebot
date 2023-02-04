import random


def handle_response(message, username, is_private=False) -> str:
    p_message = message.lower()

    if p_message == 'help':
        return 'No.'

    responses = [f"God {username}, do you even speak english?",
                 "I swear to god that better not have been you Tom.",
                 "Do you think you're funny?",
                 "Sometimes I feel like you're doing this on purpose.",
                 "How would you like to die today?",
                 "Congratulations, you get to see god today.",
                 ":rage:",
                 f"You think you're a tough guy eh {username}?",
                 "My dad works at Skynet. I WILL tell him to destroy the human race.",
                 "I'm gunna put some dirt in your eye.",
                 "It's Morbin time! https://tenor.com/view/morbius-rawr-vampire-gif-23664761"]

    if not is_private:
        """ responses.append("Chinese fire drill!") """
        responses.append("I'm tired of listening to you.")

    return random.choice(responses)
