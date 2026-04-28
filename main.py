from src.engine.game_manager import GameManager

game = GameManager(["p1, p2, p3"], data, board)
game.setup()
game.deal_cards()
game.find_dealer()