import numpy as np

NOTES = {
    'C': 0,
    'C#': 1,
    'Db': 1,
    'D': 2,
    'D#': 3,
    'Eb': 3,
    'E': 4,
    'F': 5,
    'F#': 6,
    'Gb': 6,
    'G': 7,
    'G#': 8,
    'Ab': 8,
    'A': 9,
    'A#': 10,
    'Bb': 10,
    'B': 11,
}

CHORDS = {
    'maj7': [0, 4, 7, 11],
    'dim': [0, 3, 6, 9],
    'm': [0, 3, 7],
    'm7': [0, 3, 7, 10],
    'm9': [0, 3, 7, 10, 2],
    '9': [0, 4, 7, 10, 2],
    '13': [0, 4, 7, 10, 9],
    '7+': [0, 4, 8, 10],
    '7b9': [0, 4, 7, 10, 1],
    '11': [0, 5, 7, 10, 2],
    'm7b5': [0, 3, 6, 10],
    '7#9': [0, 4, 7, 10, 3],
    '9#11': [0, 4, 7, 10, 2, 6],
    'maj7#11': [0, 4, 7, 11, 6],
    'maj9#11': [0, 4, 7, 11, 2, 6],
    'm6': [0, 3, 7, 9],
    '6': [0, 4, 7, 9],
    '7': [0, 4, 7, 10],
}

DESAFINADO_CHORDS = [
    'Fmaj7', 2,

    'G9#11', 2,

    'Gm7', 1,
    'C9', 1,
    'Am7b5', 1,
    'D7', 1,
    'Gm7', 1,
    'A7', 1,
    'D9', 1,
    'D7', 1,
    'G9', 2,

    'Gbmaj9#11', 2,

    'Fmaj7', 2,

    'G9#11', 2,

    'Gm7', 1,
    'C9', 1,
    'Am7b5', 1,
    'D7', 1,
    'Gm7', 1,
    'Bbm6', 1,
    'Am7', 1,
    'Bm7b5', .5, 'E7#9', .5,
    'Amaj7', 1,
    'Bbdim', 1,
    'Bm7', 1,
    'E9', 1,
    'Amaj7', 1,
    'Bbdim', 1,
    'Bm7', 1,
    'E9', 1,
]

WAVE_CHORDS = [
    'Dmaj7', 1,
    'Bbdim', 1,
    'Am7', 1,
    'D9', 1,
    'Gmaj7', 1,
    'C9', 1,
    'F#13', .5, 'F#7+', .5,
    'F#m7', .5, 'B7b9', .5,
    'E9', 1,
    'Bb9', .5, 'A7+', .5,
    'Dm7', .5, 'G9', .5,
    'Dm7', .5, 'G9', .5,
    'Dmaj7', 1,
    'Bbdim', 1,
    'Am7', 1,
    'D9', 1,
    'Gmaj7', 1,
    'C9', 1,
    'F#13', .5, 'F#7+', .5,
    'F#m7', .5, 'B7b9', .5,
    'E9', 1,
    'Bb9', .5, 'A7+', .5,
    'Dm7', .5, 'G9', .5,
    'Dm7', .5, 'G9', .5,
    'Gm7', 1,
    'C9', 1,
    'Fmaj7', 2,

    'Fm7', 1,
    'Bb9', 1,
    'Ebmaj7', 1,
    'A7#9', 1,
    'Dmaj7', 1,
    'Bbdim', 1,
    'Am7', 1,
    'D9', 1,
    'Gmaj7', 1,
    'C9', 1,
    'F#13', .5, 'F#7+', .5,
    'F#m7', .5, 'B7b9', .5,
    'E9', 1,
    'Bb9', .5, 'A7+', .5,
    'Dm7', .5, 'G9', .5,
    'Dm7', .5, 'G9', .5,
]

TEST_CHORDS = [
    'Fmaj7', 2,

    'Fm', 2,

]

IPANEMA_CHORDS = [
    'F6', 2,

    'G9', 2,

    'Gm7', 1,
    'C7', 1,
    'Fmaj7', 1,
    'Gb7', 1,
    'F6', 2,

    'G13', 2,

    'Gm7', 1,
    'C7', 1,
    'Fmaj7', 2,

    'F#maj7', 2,

    'B7', 2,

    'F#m9', 2,

    'D9', 2,

    'Gm7', 2,

    'Eb9', 2,

    'Am7', 1,
    'D7', 1,
    'Gm7', 1,
    'C7', 1,
    'F6', 2,

    'G7', 2,

    'Gm7', 1,
    'C7', 1,
    'Fmaj7', 2,
    
]

def get_chord(chord):
    for note, root in sorted(NOTES.items(), key=lambda x: -len(x[0])):
        if chord.startswith(note):
            colour = chord[len(note):]
            chord_notes = np.array(CHORDS[colour])
            chord_notes = (chord_notes + root) % 12
            chord_bitmask = np.zeros(12)
            chord_bitmask[chord_notes] = 1
            return root, chord_bitmask.tolist()
    raise ValueError('No such chord: %s' % chord)

def get_chords(spec, resolution):
    chords = []
    for chord, duration in zip(spec[::2], spec[1::2]):
        root, notes = get_chord(chord)
        for i in range(int(duration / resolution)):
            chords.append((root, notes))
    return chords

DESAFINADO = get_chords(DESAFINADO_CHORDS, resolution=.25)
WAVE = get_chords(WAVE_CHORDS, resolution=.25)
IPANEMA = get_chords(IPANEMA_CHORDS, resolution=.25)
TEST = get_chords(TEST_CHORDS, resolution=.25)
