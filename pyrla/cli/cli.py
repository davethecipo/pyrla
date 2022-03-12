from boxcars_py import parse_replay

FOLDER_PATH='/media/davide/328AB7AC8AB76B4D/Documents and Settings/davide/Documenti/My Games/Rocket League/TAGame/Demos'
REPLAY_NAME='CF6F1BD040243950CF20B1BDE0258352.replay'

with open("your_replay.replay", "rb") as f:
  buf = f.read()
  f.close()

replay = parse_replay(buf)


def main():
    print('wewe')

