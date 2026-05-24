# **********************************************************************
# Crazy8s v1.0
# **********************************************************************


from kivy import require as kivy_version
from kivy.config import Config
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import ObjectProperty, BooleanProperty, \
    NumericProperty, BoundedNumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.behaviors import DragBehavior
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.uix.checkbox import CheckBox
from kivy.graphics import Color, RoundedRectangle


from itertools import cycle
from random import shuffle

from players import Player
from cards import FrenchDeck, CardStack


# **********************************************************************
class SplashScreen(Screen):
    """ First application Screen """

    # ==================================================================
    def on_enter(self):
        """ Automatically change to next screen after a short delay """
        Clock.schedule_once(self.leave_splash, 2)

    # ==================================================================
    # noinspection PyUnusedLocal
    def leave_splash(self, *args):
        """ Abandon screen, activate SetupScreen. """
        self.parent.current = 'SetupScreen'


# **********************************************************************
class SetupScreen(Screen):
    """ Initial user data entry """

    requested_players = NumericProperty(None)
    requested_humans = NumericProperty(None)
    requested_autoplay = BooleanProperty(False)
    requested_autoplay_delay = NumericProperty(None)
    preferences_checked = BooleanProperty(False)

    # ==================================================================
    def on_enter(self):
        """
        Preferences need to be checked each time the
        user has the possibility to make a change
        """
        self.preferences_checked = False

    # ==================================================================
    def check_preferences(self):
        """ Validate user preferences """
        preferences = {
            'num_players': self.requested_players,
            'num_humans': self.requested_humans,
            'autoplay_delay': self.requested_autoplay_delay
        }
        app = App.get_running_app()
        ok_flag = True
        for prop in preferences:
            min_val, max_val = app.property(prop).bounds
            if not(min_val <= preferences[prop] <= max_val):
                msg = '{} out of bounds\n(value = {}, range = [{}-{}])'
                app.warning(msg.format(prop, preferences[prop],
                                       min_val, max_val))
                ok_flag = False
                break
        if self.requested_humans > self.requested_players:
            msg = 'Requested more humans than total players'
            app.warning(msg)
            ok_flag = False
        self.preferences_checked = ok_flag

    # ==================================================================
    # noinspection PyUnusedLocal
    def on_preferences_checked(self, instance, ok_value):
        """
        Activate game screen when all preferences are within bounds
        """
        if ok_value:
            app = App.get_running_app()
            try:
                app.num_players = self.requested_players
                app.num_humans = self.requested_humans
                app.autoplay = self.requested_autoplay
                app.autoplay_delay = self.requested_autoplay_delay
            except (ValueError, AttributeError, TypeError) as err:
                msg = 'Error in requested settings.\n{}'.format(err)
                Crazy8sApp.warning(msg)
            else:
                self.parent.current = 'GameScreen'


# **********************************************************************
class GameScreen(Screen):
    """ Main game screen """

    # Game table zones defined in kv file
    player_zone = ObjectProperty(None)
    draw_zone = ObjectProperty(None)
    discard_zone = ObjectProperty(None)
    msg = ObjectProperty(None)

    # ==================================================================
    def on_enter(self):
        """
        Instruct the app to create a new game and set up observers
        bound to selected game state variables
        """
        app = App.get_running_app()
        app.create_game()
        self.display_state(None, None)
        app.bind(current_player=self.display_state)
        app.bind(winner=self.display_state)
        app.bind(crazy_turn=self.display_crazy)

    # ==================================================================
    def on_pre_leave(self, *args):
        """ Stop running game before leaving screen """
        App.get_running_app().autoplay = False

    # ==================================================================
    # noinspection PyUnusedLocal
    def display_crazy(self, instance, value):
        """ Display crazy 8 move """
        app = App.get_running_app()
        if value:
            self.msg.text = \
                'Crazy 8 played by {}! Next suit is {}.'.format(
                    app.current_player.name, app.next_suit)
            self.display_state(None, None)
        else:
            self.msg.text = ''

    # ==================================================================
    # noinspection PyUnusedLocal
    def display_state(self, instance, value):
        """ Display present game state """

        # --------------------------------------------------------------
        def highlight_player(flag):
            normal_color = (1, 1, 1, 0.8)   # Gray
            highlight_color = (1, 1, 0, 1)  # Yellow
            if flag and frame:
                # Highlight frame
                with frame.canvas.before:
                    Color(0, 0.3, 0.2)  # Light green
                    RoundedRectangle(pos=frame.pos, size=frame.size)
                # Highlight label
                player.data['label'].color = highlight_color
                # Mark text, user might be color-blind
                player.data['label'].text = '[ ' + player.name + ' ]'
            else:
                # Reset highlights on non-current player
                if frame:
                    frame.canvas.before.clear()
                player.data['label'].color = normal_color
                player.data['label'].text = player.name

        # --------------------------------------------------------------
        app = App.get_running_app()

        # First time, initialize zones
        if app.turn == 0:
            self.msg.text = 'Waiting for game to start...'
            self.clear_card_zones()
            self.create_player_zones()
        elif app.turn == 1:
            self.msg.text = 'Game is running.'

        # Update discard zone
        GameScreen.update_card_zone(self.discard_zone, app.discard)

        # Update draw zone
        GameScreen.update_card_zone(self.draw_zone, app.draw)

        # Iterate over players to find their zones
        for player in app.players:
            # Verify frame presence
            frame = player.data['frame']
            if frame is None:
                self.clear_card_zones()
                self.create_player_zones()

            # Verify winner
            if player == app.winner:
                win_img_src = app.IMAGE_DIR + 'happy_face_win.jpg'
                img = Image(source=win_img_src)
                frame.clear_widgets()
                frame.add_widget(img)
                self.msg.text = player.name + ' wins!'
            else:
                # When passing over current player, visually mark it
                highlight_player(player == app.current_player)

                # Show number of cards in player caption
                # num_cards = len(player.data['hand'])
                # label_len = len(player.data['label'].text)
                # add_caption = \
                #     '({} card{})'.format(num_cards,
                #                          's' if num_cards != 1 else '')
                # player.data['label'].text += \
                #     '\n' + add_caption.center(label_len)
                # Update the player zone
                GameScreen.update_card_zone(player.data['zone'],
                                            player.data['hand'])

    # ==================================================================
    def clear_card_zones(self):
        """ Clear (possible) previous card zones """
        card_zones = [
            self.draw_zone,
            self.discard_zone,
            self.player_zone
        ]
        for zone in card_zones:
            for widget in zone.walk(restrict=True):
                widget.clear_widgets()

    # ==================================================================
    def create_player_zones(self):
        """ Create players and their widget sub-zones """

        app = App.get_running_app()

        for player in app.players:
            # Container for card and label
            player.data['frame'] = \
                BoxLayout(orientation='vertical',
                          padding=4,
                          pos_hint={'center_x': 0.5, 'center_y': 0.5})
            # Card zone
            player.data['zone'] = \
                BoxLayout(spacing=-50,
                          size_hint=(1, 0.6))
            # Player label
            player.data['label'] = \
                Label(text=player.name,
                      size_hint=(1, 0.4),
                      font_size=13)
            # Put card zone and player label on container frame
            player.data['frame'].add_widget(player.data['zone'])
            player.data['frame'].add_widget(player.data['label'])
            # Add whole container to Player Zone
            self.player_zone.add_widget(player.data['frame'])

    # ==================================================================
    @staticmethod
    def update_card_zone(zone, cards):
        """ Update UI zone with cards """
        zone.clear_widgets()
        for card in cards:
            image = card.back if card.facedown else card.front
            zone.add_widget(
                Image(texture=CoreImage(image, ext='png').texture))


# **********************************************************************
class PopupWidgetMenu(DragBehavior, Popup):
    """ Widget selection with popup menu """

    # ==================================================================
    def __init__(self, widget_list=None, **kwargs):
        """ Extend Popup initialization to build contents """

        self.auto_dismiss = False
        self.title_align = 'center'
        super(PopupWidgetMenu, self).__init__(**kwargs)

        self._chosen_index = None
        self._option_list = []

        options_frame = BoxLayout(orientation='horizontal')
        if widget_list:
            self._option_list = \
                [CheckBox(group='1',
                          disabled=widget.disabled,
                          on_press=self.find_selected_choice)
                 for widget in widget_list]
            for widget, option in zip(widget_list.copy(), self._option_list):
                item_frame = BoxLayout(orientation='vertical',
                                       disabled=option.disabled)
                if item_frame.disabled:
                    item_frame.opacity = 0.25
                item_frame.add_widget(widget)
                item_frame.add_widget(option)
                options_frame.add_widget(item_frame)

        button = Button(text='Ok',
                        size_hint=(0.25, 0.25),
                        pos_hint={'center_x': 0.5, 'center_y': 0.5},
                        on_press=self.dismiss)

        self.content = BoxLayout(orientation='vertical', padding=2)
        self.content.add_widget(options_frame)
        self.content.add_widget(button)

    # ==================================================================
    # noinspection PyUnusedLocal
    def find_selected_choice(self, obj):
        """ Set choice to currently active option """
        for index, option in enumerate(self._option_list):
            if option.active:
                self._chosen_index = index
                break

    # ==================================================================
    @property
    def choice(self):
        """ Return index of selected choice """
        return self._chosen_index

    # ==================================================================
    # noinspection PyUnusedLocal
    def on_pos(self, instance, value):
        """ Update drag rectangle when position changes """
        self.drag_rectangle = (self.x, self.y, self.width, self.height)


# **********************************************************************
# noinspection PyAttributeOutsideInit
class Crazy8sApp(App):
    """ Play a Crazy Eights game """

    IMAGE_DIR = './img/'
    MAX_TURNS = 300
    CRAZY8 = '8'    # Rank of wildcard

    num_players = \
        BoundedNumericProperty(4, min=2, max=10, errorvalue=4)
    num_humans = \
        BoundedNumericProperty(1, min=0, max=10, errorvalue=1)
    autoplay = \
        BooleanProperty(False)
    autoplay_delay = \
        BoundedNumericProperty(2, min=0, max=10, errorvalue=2)
    crazy_turn = \
        BooleanProperty(False)

    turn = NumericProperty(0)
    current_player = ObjectProperty(None, allownone=True)
    winner = ObjectProperty(None, allownone=True)

    # ==================================================================
    def create_game(self):
        """ Create the game """

        # Disable previous pending play
        Clock.unschedule(self.start_turn)

        # Create deck
        self.draw = FrenchDeck.create(shuffle=True, facedown=True)
        FrenchDeck.loadimages(self.draw, dirname=self.IMAGE_DIR)

        # Create players and deal the cards
        self.create_players()
        shuffle(self.players)
        hand_size = 5 if self.num_players > 2 else 7
        for player in self.players:
            player.data['hand'] = \
                self.draw.deal(hand_size, facedown=True)

        # Discard heap
        self.discard = self.draw.deal(1, facedown=False)

        # Reset game data
        self.winner = None
        self.current_player = None
        self.turn_order = cycle(self.players)
        self.reshuffles = 0
        self.next_suit = self.discard.top().suit
        self.next_rank = self.discard.top().rank
        self.elected_card, self.elected_suit = None, None

    # ==================================================================
    def create_players(self):
        """ Create the players, assign their names and turn order """

        # noinspection SpellCheckingInspection
        bot_player_list = [
            'R2-D2', 'C-3P0', 'BB-8', 'Bubo', 'ENIAC', 'Multivac',
            'Sonny', 'R. Daneel', 'R. Giskard', 'Robbie', 'Andrew',
            'Wall-E', 'E.V.E.', 'Johnny 5', 'Data', 'Ash', 'Bishop',
            'Call', 'David', 'Cortana', 'Siri', 'Bender', 'Mr. Roboto',
            'Tron', 'Quorra', 'Rinzler', 'Jarvis', 'TARS', 'CASE',
            'Skynet', 'T-800', 'T-1000', 'D.A.R.Y.L.', 'Gerty 3000',
            'HAL-9000', 'SAL-9000', 'Gort', 'Marvin', 'CABAL', 'Muffit',
            'Optimus Prime', 'Starscream', 'Megatron', 'Pris', 'Clu',
            'K.I.T.T', 'K.A.R.R', 'TET', 'Maria', 'Ironhide', 'Robby',
            'Ultron', 'Vision', 'Wintermute', 'Deep Thought', 'Tik-Tok',
            'Mazinger-Z', 'Dai-Apolon', 'Arbegas', 'Gunslinger',
            'Iron Giant', 'Bumblebee', 'Vincent',
        ]

        shuffle(bot_player_list)
        self.players = \
            Player.createlist(numplayers=self.num_players,
                              prefix='Player ')
        for index, player in enumerate(self.players):
            player.data = {
                'hand': None,   # Cards
                'func': None,   # Turn play function
                'frame': None,  # Widget holding cards and caption
                'zone': None,   # Visualization widget
                'label': ''     # Caption
            }
            if index < self.num_humans:
                player.is_human = True
                player.data['func'] = self.select_by_human
            else:
                player.is_human = False
                player.name = bot_player_list.pop()
                player.data['func'] = self.select_by_program

    # ==================================================================
    # noinspection PyUnusedLocal
    def on_current_player(self, instance, value):
        """ Actions when player changes """
        if self.current_player is None:
            self.turn = 0
        else:
            self.turn += 1

    # ==================================================================
    # noinspection PyUnusedLocal
    def on_autoplay(self, instance, value):
        """ Update scheduling of turn according to autoplay setting """
        if value and self.current_player is not None:
            self.start_turn()
        else:
            Clock.unschedule(self.start_turn)

    # ==================================================================
    def has_ended(self):
        """ Check if game has ended or not """
        return self.turn >= self.MAX_TURNS or self.winner is not None

    # ==================================================================
    # noinspection PyUnusedLocal
    def start_turn(self, *args):
        """ Invoke turn actions method for current player """

        if self.has_ended():
            return

        self.current_player = next(self.turn_order)
        self.elected_card, self.elected_suit = None, None

        # Call play function for current player
        try:
            self.current_player.data['func']()
        except (KeyError, TypeError) as err:
            # If play function cannot be called, stop autoplay and pass
            msg = 'Cannot call play function for {}.'
            msg += '\nPassing (No turn actions taken).'
            msg += '\nAutoplay was stopped.' if self.autoplay else ''
            msg += '\n{}'
            Crazy8sApp.warning(
                msg.format(self.current_player.name, err))
            self.autoplay = False
            self.current_player = next(self.turn_order)

    # ==================================================================
    def process_election(self):
        """ Executes actions previously selected """

        # elected, suit = self.elected_card, self.elected_suit
        hand = self.current_player.data['hand']
        if self.elected_card is not None:
            # Show the card and play it
            self.elected_card.flip()
            hand.cards.remove(self.elected_card)
            self.discard.cards.append(self.elected_card)
            if not hand:
                self.winner = self.current_player
            if self.elected_card.rank == self.CRAZY8 \
                    and self.elected_suit is not None:
                self.next_suit = self.elected_suit
            else:
                self.next_suit = self.elected_card.suit
            self.crazy_turn = (self.elected_card.rank == self.CRAZY8)
        else:
            # No card to play
            if len(self.draw) < 1 < len(self.discard):
                # Attempt a reshuffle from discard if deck is emtpy
                self.discard, self.draw = \
                    self.discard.deal(1), self.discard
                self.draw.flip()
                self.draw.shuffle()
                self.reshuffles += 1
            if len(self.draw) > 0:
                # If deck is not empty, draw
                hand.cards.append(self.draw.draw())
            else:
                self.empty_draws += 1
        # Next rank always from top, even if crazy 8 was played
        self.next_rank = self.discard.top().rank

    # ==================================================================
    def end_turn(self):
        """ Perform turn-closing actions """
        if self.autoplay and not self.has_ended():
            Clock.schedule_once(self.start_turn,
                                self.autoplay_delay)

    # ==================================================================
    def get_candidates(self, hand):
        """ Return list of candidate cards for play """
        return [
            card for card in hand
            if (card.rank == self.CRAZY8 or
                card.suit == self.next_suit or
                card.rank == self.next_rank)
        ]

    # ==================================================================
    def select_by_human(self):
        """ Let human select what to play """

        # --------------------------------------------------------------
        def img_menu(title, img_list, dismiss_function, size=(400, 250)):
            """ Create image menu """
            return PopupWidgetMenu(
                widget_list=img_list,
                title=title,
                size_hint=(None, None),
                size=size,
                separator_color=[0.2, 0.4, 0.2, 1],
                title_color=[0.5, 0.9, 0.5, 1],
                separator_height='2dp',
                background_color=[0, 0.1, 0, 0.2],
                on_dismiss=dismiss_function
            )

        # --------------------------------------------------------------
        # noinspection PyUnusedLocal,PyShadowingNames
        def end_card_selection(*args):
            """ Ends current interaction and continues game """
            card_choice_index = card_menu.choice
            if card_choice_index is None:
                self.process_election()
                self.end_turn()
            else:
                self.elected_card = hand[card_choice_index]
                if self.elected_card.rank == self.CRAZY8:
                    suit_menu.open()
                else:
                    self.process_election()
                    self.end_turn()

        # --------------------------------------------------------------
        # noinspection PyUnusedLocal,PyShadowingNames
        def end_suit_selection(*args):
            suit_choice_index = suit_menu.choice
            if suit_choice_index is None:
                self.process_election()
                self.end_turn()
            else:
                self.elected_suit = \
                    list(FrenchDeck.SUITS)[suit_choice_index]
                self.process_election()
                self.end_turn()

        # --------------------------------------------------------------
        # noinspection PyUnusedLocal
        card_choice_index = None
        # noinspection PyUnusedLocal
        suit_choice_index = None

        hand = self.current_player.data['hand']
        candidates = self.get_candidates(hand)

        prefix = self.IMAGE_DIR + 'suit_'
        suit_images = [
            Image(source=prefix + suit.lower() + '.png')
            for suit in FrenchDeck.SUITS
        ]
        suit_menu = \
            img_menu('Crazy 8 played. Choose the next suit',
                     suit_images, end_suit_selection)

        card_images = [
            Image(texture=CoreImage(card.front, ext='png').texture,
                  disabled=card not in candidates)
            for card in hand
        ]
        card_menu = \
            img_menu(self.current_player.name + ': Choose a card',
                     card_images, end_card_selection)
        card_menu.open()

    # ==================================================================
    def select_by_program(self):
        """ Algorithmic selection of what to play """

        # --------------------------------------------------------------
        def card_ranking(card):
            """ Assign a playing value (ranking) to a card """
            initial = -52 * 7 if card.rank == self.CRAZY8 else 0
            same_suit_in_hand = \
                len(list(hand.search(suits=[card.suit])))
            same_rank_in_hand = \
                len(list(hand.search(ranks=[card.rank])))
            same_suit_in_discard = \
                len(list(self.discard.search(suits=[card.suit])))
            same_rank_in_discard = \
                len(list(self.discard.search(ranks=[card.rank])))
            return initial + same_suit_in_hand \
                           + same_rank_in_hand \
                           + same_suit_in_discard \
                           + same_rank_in_discard

        # --------------------------------------------------------------
        def select_crazy_suit():
            """ Find best next suit when a crazy 8 was played """

            # Exclude 8's from selection as their suit is irrelevant
            no8 = CardStack(hand.search(ranks=[self.CRAZY8],
                                        negate=True))
            if len(no8) > 0:
                # Choose the most common suit in hand
                crazy_suit = \
                    max((suit for suit in set(no8.suits())),
                        key=lambda s: len(list(no8.search(suits=[s]))))
            else:
                crazy_suit = None
            return crazy_suit

        # --------------------------------------------------------------
        # Evaluate candidate cards if available
        hand = self.current_player.data['hand']
        candidates = self.get_candidates(hand)
        if candidates:
            # Select card with highest ranking
            self.elected_card = max((card for card in candidates),
                                    key=lambda c: card_ranking(c))
            # Select the next suit:
            # If crazy 8 was played, choose by selection function
            if self.elected_card.rank == self.CRAZY8:
                self.elected_suit = select_crazy_suit()
        self.process_election()
        self.end_turn()

    # ==================================================================
    @staticmethod
    def warning(msg):
        """ Display a warning as a modal popup """

        label = Label(text=msg, size_hint=(1, 0.8))
        button = Button(text='Ok', size_hint=(0.5, 0.2),
                        pos_hint={'center_x': 0.5, 'center_y': 0.5})
        content = BoxLayout(orientation='vertical',
                            padding=5, spacing=5)
        content.add_widget(label)
        content.add_widget(button)
        popup = Popup(title='Application warning',
                      content=content, auto_dismiss=False,
                      size_hint=(None, None), size=(400, 200))
        button.bind(on_press=popup.dismiss)
        popup.open()


# **********************************************************************
if __name__ == '__main__':
    kivy_version('2.3.0')
    Config.set('graphics', 'width', '800')
    Config.set('graphics', 'height', '600')
    Config.set('graphics', 'resizable', False)
    Config.set('input', 'mouse', 'mouse,disable_multitouch')
    Crazy8sApp().run()
