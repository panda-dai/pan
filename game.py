import random
from typing import List, Dict

from models import GameRound, GameConfig, GamePlayerRole, GuessAttempt
from players import GamePlayer


class Game:

    def __init__(self, config: GameConfig, players: List[GamePlayer]):
        self.config = config
        self.game_rounds = []
        self.id_to_player = {player.id: player for player in players}

    def start_game(self) -> None:
        num_rounds = self.config.num_rounds
        while num_rounds > 0:
            self.game_rounds.append(self.start_game_round())
            num_rounds -= 1
        player_to_score = self.get_scores_by_player()
        print('Game ends. Here is the score board.')
        print(player_to_score)

    def start_game_round(self) -> GameRound:
        # Assign players roles randomly
        secret_keeper_player_id = random.choice(list(self.id_to_player.keys()))
        secret_keeper_player = self.id_to_player[secret_keeper_player_id]
        guesser_players = [player for player_id, player in self.id_to_player.items() if
                           player_id != secret_keeper_player_id]
        print(f'Player {secret_keeper_player_id}, you have been selected to be the secret keeper for this round.')
        print(f'Players {",".join([str(guesser_player.id) for guesser_player in guesser_players])}, you are going to guess the secret word in turns.')
        print('Let the game begin')

        secret_keeper_player.choose_word()
        print('Secret keeper has chosen the word.')

        game_round = GameRound(player_to_role={**{secret_keeper_player_id: GamePlayerRole.SECRET_KEEPER},
                                               **{guesser_player.id: GamePlayerRole.GUESSER for guesser_player in
                                                  guesser_players}},
                               secret_word_length=secret_keeper_player.tell_word_length())
        print(f'Word: {game_round.get_current_word_with_markup()}')

        tries_left = self.config.num_tries_per_round
        while tries_left > 0:
            for guesser_player in guesser_players:
                print(f'player {guesser_player.id}, it\'s your turn.')
                print(f'Already guess chars: {",".join(game_round.get_already_guessed_characters())}')
                guess = guesser_player.guess(game_round)
                matched_positions = secret_keeper_player.check(game_round, guess)
                if len(matched_positions) == 0:
                    tries_left -= 1
                    print(
                        f'Wrong guess :( {guess} is not in the secret word. Guessers now have {tries_left} tries left.')
                else:
                    print(f'You guess correctly :) {guess} presents in the secret word.')
                game_round.add_attempt(GuessAttempt(guesser_player.id, guess, matched_positions))
                print(f'The current word is: {game_round.get_current_word_with_markup()}')
                if game_round.has_guessed_the_word():
                    print('Guessers won this round!')
                    return game_round
        print('Secret keeper won this round!')
        print(f'The secret word is {secret_keeper_player.tell_secret_word()}')
        return game_round

    def get_scores_by_player(self) -> Dict[int, int]:
        player_to_score = {}
        for player_to_score_round in [game_round.calculate_players_scores() for game_round in self.game_rounds]:
            for player, score in player_to_score_round.items():
                if player in player_to_score:
                    player_to_score[player] += score
                else:
                    player_to_score[player] = score
        return player_to_score
