#!/usr/bin/env python3
"""
Standalone smoke test for cards.py + players.py
Run this before trying to launch the Kivy app.
No Kivy dependency required.
"""

from cards import FrenchDeck, CardStack
from players import Player
from io import BytesIO
import os

def main():
    print("=== Crazy8s Cards + Players Smoke Test ===\n")

    # 1. Test Player
    print("1. Testing Player.createlist()...")
    players = Player.createlist(4, prefix="Player ")
    for p in players:
        print(f"   {p}")
    print("   OK\n")

    # 2. Create deck
    print("2. Creating FrenchDeck...")
    deck = FrenchDeck.create(shuffle=True)
    print(f"   Deck size: {len(deck)}")
    print("   OK\n")

    # 3. Load images (critical for Kivy rendering)
    img_dir = "./img/"
    print(f"3. Loading images from {img_dir} ...")
    if not os.path.isdir(img_dir):
        print(f"   ERROR: {img_dir} not found. Run this script from project root.")
        return

    FrenchDeck.loadimages(deck, dirname=img_dir)
    print("   loadimages() completed\n")

    # 4. Verify image data on cards
    print("4. Verifying image data (front/back as BytesIO)...")
    sample = list(deck)[:3]
    for card in sample:
        front = card.front
        back = card.back
        front_ok = isinstance(front, BytesIO) and len(front.getvalue()) > 1000
        back_ok = isinstance(back, BytesIO) and len(back.getvalue()) > 1000
        print(f"   {card.name}: front={front_ok}, back={back_ok}")
        if not (front_ok and back_ok):
            print("   WARNING: Some images failed to load properly.")
    print("   OK\n")

    # 5. Test CardStack search (used by AI)
    print("5. Testing CardStack.search()...")
    hearts = list(deck.search(suits=["HEARTS"]))
    eights = list(deck.search(ranks=["8"]))
    print(f"   Hearts found: {len(hearts)}")
    print(f"   Eights found: {len(eights)}")
    print("   OK\n")

    print("=== All smoke tests passed ===")
    print("You can now proceed to install Kivy and test the full app.\n")


if __name__ == "__main__":
    main()
