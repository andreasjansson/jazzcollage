import numpy as np
import os
from glob import glob
import collections
import simplejson as json
import cPickle
import random
from andreasmusic import audio, pitches

import scores

CHROMAGRAM_FOLDER = 'blah'
AUDIO_FOLDER = 'blah'

def klanginess(values, n=2):
    template = np.zeros(len(values))
    template[-n:] = 1
    values = np.sort(values) / np.max(values)
    dist = np.power(values - template, 2)
    return np.sum(dist)

def en_chromagrams():
    parent_folder = os.path.expanduser(CHROMAGRAM_FOLDER)
    for folder in glob('%s/*' % parent_folder):
        path = '%s/echonest.json' % folder
        with open(path) as f:
            data = json.load(f)
        chromagram = np.array([s['pitches'] for s in data['segments']])
        segments = [(s['start'], s['start'] + s['duration']) for s in data['segments']]
        filename = [data['meta']['filename']][0]
        yield os.path.basename(filename), chromagram, segments

def peaks_are_good(peaks):
    for i in peaks:
        for j in peaks:
            if (i + 1) % 12 == j or (j + 1) % 12 == i:
                return False
    return True

def generate_nklangs():
    nklangs = collections.defaultdict(list)

    for progress, (filename, ch, segments) in enumerate(en_chromagrams()):
        print progress
        for n in (1, 2, 3):
            nklanginess = [klanginess(c, n) for c in ch]
            nklang_indices = np.where(np.array(nklanginess) < .3)[0]
            for i in nklang_indices:
                c = ch[i,:]
                peaks = frozenset(np.argsort(c)[-n:])
                if peaks_are_good(peaks):
                    start, end = segments[i]
                    nklangs[peaks].append((c, filename, start, end))

    with open('nklangs.pkl', 'w') as f:
        cPickle.dump(nklangs, f, protocol=cPickle.HIGHEST_PROTOCOL)

    return nklangs

def synthesize_chords(chords, resolution):
    sr = 44100.0
    bpm = 120.0
    timesig = 4
    tfactor = resolution * sr * timesig / (bpm / 60)
    signal = np.zeros(len(chords) * tfactor)
    for i, (root, notes) in enumerate(chords):
        start = int(i * tfactor)
        end = int((i + 1) * tfactor)
        l = end - start
        for j, n in enumerate(notes):
            if n:
                fq = pitches.C4.fq * np.power(2, j / 12.0)
                signal[start:end] += np.sin(np.arange(l) * np.pi * 2 * fq / sr)
        root_fq = pitches.C2.fq * np.power(2, root / 12.0)
        signal[start:end] += np.sin(np.arange(l) * np.pi * 2 * root_fq / sr)

    signal /= np.max(np.abs(signal))
    signal = signal.astype('float32')
        
    return audio.Audio(signal, sr)

def synthesize_tune(chords):
    a = synthesize_chords(chords, resolution=0.5)
    audio.play(a)

def klang_in_chord(klang, chord):
    for k in klang:
        if not chord[k]:
            return False
    return True

def find_klang(nklangs, root, chord):
    n_notes = np.random.choice(3) + 1

    for _ in xrange(10000): # this is art, not science
        klang = frozenset(np.random.choice(12, n_notes))
        if klang_in_chord(klang, chord) and klang in nklangs:
            return klang

    return frozenset([root])

def random_snippet(nklangs, klang):
    chromagram, filename, start, end = random.choice(nklangs[frozenset(klang)])
    a = audio.read('%s/%s' % (AUDIO_FOLDER, filename))
    a2 = audio.crop_seconds(a, start, end)
    return a2.signal

def make_song(nklangs, chords, bpm=30, root_prob=0.3, same_chord_prob=.8):
    sample_rate = 44100
    n_signals = 5
    all_klangs = []
    for i, (root, chord) in enumerate(chords):
        klangs = [None] * n_signals
        for j in xrange(n_signals):

            old_chord_still_works = i > 0 and klang_in_chord(all_klangs[i - 1][j], chord)

            if (i == 0
                or not old_chord_still_works
                or np.random.rand() > same_chord_prob):
                if np.random.rand() < root_prob:
                    klang = frozenset([root])
                else:
                    klang = find_klang(nklangs, root, chord)
                klangs[j] = klang
            else:
                klangs[j] = all_klangs[i - 1][j]
        all_klangs.append(klangs)

    timed_klangs = [[] for _ in range(n_signals)]
    for j in xrange(n_signals):
        prev = None
        t = 0
        for i in xrange(len(chords)):
            klang = all_klangs[i][j]
            if prev is not None and klang != prev:
                timed_klangs[j].append((prev, t))
                t = 0
            t += 1
            prev = klang
        if prev is not None:
            timed_klangs[j].append((prev, t))

    signals = np.zeros(((60. / bpm) * sample_rate * len(chords), 2, n_signals))

    fade_time = (60. / bpm) * sample_rate
    fade_in = np.sqrt(np.linspace(0, 1, fade_time))
    fade_in = np.vstack((fade_in, fade_in)).T
    fade_out = 1 - fade_in

    for k in xrange(n_signals):
        i = 0
        for klang, reps in timed_klangs[k]:
            random_shift = np.random.randint(fade_time) * 2
            start = max(round((60. / bpm) * sample_rate * i) - random_shift, 0)
            end = min(start + round((60. / bpm) * sample_rate * reps) + random_shift, signals.shape[0])

            signal = random_snippet(nklangs, klang)
            signal = (signal / np.max(np.abs(signal))) / n_signals

            n_repeats = int(np.ceil((end - start) / len(signal)))
            signal = np.tile(signal.T, n_repeats).T

            signal = signal[:end - start, :]
            signal[:fade_time, :] *= fade_in

            signal[-fade_time:, :] *= fade_out

            signals[start:end, :, k] += signal

            i += reps

            print int(start), int(end), reps

    signal = np.sum(signals, 2)
    signal = signal.astype('float32')

    return audio.Audio(signal, sample_rate)

# nklangs = generate_nklangs()
# a = make_song(nklangs, scores.IPANEMA)
# audio.write(a, 'output.mp3')
