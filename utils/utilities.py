#TODO:
# def generateRoomKeys():
#     global ROOM_IDs
#     f = open("roomKeys.txt",'w')
#     for w in range(100):
#         s = []
#         for l in range(16):
#             s.append(string.ascii_letters[random.randint(0, 51)])
#         ROOM_IDs.append(''.join(s))
#     print("Session keys generated and saved in roomKeys.txt")
#     f.write("SESSION KEYS GENERATED "+str(datetime.datetime.now())[:-7]+"\n--------\n"+'\n'.join(ROOM_IDs))
#     f.close()