from mido import MidiFile, Message, MidiTrack
import argparse

class note:
    end = None

    def __init__(self, start, note, velocity, channel, debug=0):
        self.start = start
        self.note = note
        self.velocity = velocity
        self.channel = channel
        self.debug = debug

    def __str__(self):
        return f"note: {self.note}, start: {self.start}, end: {self.end}, debug: {self.debug}"

class pair:
    note = None
    track = []

parser = argparse.ArgumentParser()
parser.add_argument("input", type=str)
parser.add_argument("output", type=str)
parser.add_argument("track", type=int)
args = parser.parse_args()
name = args.input

# (note [int] , track [list])
new_tracks = []
time = 0
a=0

f = MidiFile(name, clip=True)
track = f.tracks[args.track]

for msg in track:
    time += msg.time
    if msg.type == "note_on":
        a += 1
        found_track = False
        for i in new_tracks:
            if i.note == None:
                found_track = True
                i.note = msg.note
                i.track.append(note(time, msg.note, msg.velocity, msg.channel, debug=a))
                break
        if not found_track:
            t = [note(time, msg.note, msg.velocity, msg.channel, debug=a)]
            new_pair = pair()
            new_pair.note = msg.note
            new_pair.track = t
            new_tracks.append(new_pair)

    elif msg.type == "note_off":
        for tp in new_tracks:
            if tp.note == msg.note:
                tp.note = None
                tp.track[-1].end = time

#debug counter
for t in new_tracks:
    print(len(t.track))
    #for n in t.track:
    #    print(n)


#new file
new_file = MidiFile()
new_file.tracks.append(f.tracks[0])

c = 0
for t in new_tracks:
    track = MidiTrack()
    last_off = 0
    for n in t.track:
        track.append(Message("note_on", note=n.note, velocity=n.velocity, channel=c, time=n.start-last_off))
        track.append(Message("note_off", note=n.note, channel=c, time=n.end-n.start))
        last_off = n.end

    c += 1
    new_file.tracks.append(track)

new_file.save(args.output)