# ----------------------------------------------------------------------
# Players 0.3
# Classes for players}
#
# v. 0.2
#   Add human support
# v. 0.3
#   Add filling zeroes to player names in Player.createlist
#   Change attribute name "ishuman" to "is_human"
#   Change attribute name "isactive" to "is_active"
# ----------------------------------------------------------------------


class Player():

    __next_id = 0

    def __init__(self, name="Player", is_human=False,
                 is_active=True, data=None):
        Player.__next_id += 1
        self.__id = Player.__next_id
        self.name = name
        self.is_human = is_human
        self.is_active = is_active
        self.data = data

    def __repr__(self):
        return "{:03}:'{}':{}:{}:<{}>".format(
                    self.__id, self.name,
                    self.is_human, self.is_active, self.data)

    @staticmethod
    def createlist(numplayers, prefix="Player"):
        players = []
        seq_len = len(str(numplayers))
        fmt = '{:0' + str(seq_len) + '}' 
        for seq in range(1, numplayers + 1):
            players.append(Player(name=prefix + fmt.format(seq)))
        return players

# ----------------------------------------------------------------------
# Main segment for testing purposes
# ----------------------------------------------------------------------

if __name__ == "__main__":

    print("Testing player class v 0.2")
    print(Player.createlist(7))
    print(Player.createlist(13))

    while True:
        if input("\nq to exit ") == "q":
            break
