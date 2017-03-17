#!/usr/bin/env python3

import argparse
from matplotlib import pyplot as plt
import re

parser = argparse.ArgumentParser()
parser.add_argument('log_files', nargs='+')
parser.add_argument('--output')
parser.add_argument('--max-steps', type=int, default=0)
parser.add_argument('--min-steps', type=int, default=0)
parser.add_argument('--labels', nargs='+')
parser.add_argument('--plot', nargs='+', default=['train', 'dev', 'bleu', 'ter'])

args = parser.parse_args()
args.plot = [x.lower() for x in args.plot]

if args.labels:
    if len(args.labels) != len(args.log_files):
        raise Exception('error: wrong number of labels')
    labels = args.labels
else:
    labels = ['model {}'.format(i) for i in range(1, len(args.log_files) + 1)]

for label, log_file in zip(labels, args.log_files):
    current_step = 0

    dev_perplexities = []
    train_perplexities = []
    bleu_scores = []
    ter_scores = []

    with open(log_file) as f:
        for line in f:
            m = re.search('main step (\d+)', line)
            if m:
                current_step = int(m.group(1))

            if 0 < args.max_steps < current_step:
                break
            if current_step < args.min_steps:
                continue

            m = re.search(r'eval: loss (-?\d+.\d+)', line)
            if m and not any(step == current_step for step, _ in dev_perplexities):
                perplexity = float(m.group(1))
                dev_perplexities.append((current_step, perplexity))
                continue

            m = re.search(r'loss (-?\d+.\d+)$', line)
            if m and not any(step == current_step for step, _ in train_perplexities):
                perplexity = float(m.group(1))
                train_perplexities.append((current_step, perplexity))

            m = re.search(r'bleu=(\d+\.\d+)', line)
            m = m or re.search(r'score=(\d+\.\d+)', line)
            if m and not any(step == current_step for step, _ in bleu_scores):
                bleu_score = float(m.group(1))
                bleu_scores.append((current_step, bleu_score))

            m = re.search(r'ter=(\d+\.\d+)', line)
            m = m or re.search(r'score=(\d+\.\d+)', line)
            if m and not any(step == current_step for step, _ in ter_scores):
                ter_score = float(m.group(1))
                ter_scores.append((current_step, ter_score))

    if 'bleu' in args.plot and bleu_scores:
        plt.plot(*zip(*bleu_scores), ':', label=' '.join([label, 'BLEU']))
    if 'ter' in args.plot and ter_scores:
        plt.plot(*zip(*ter_scores), ':', label=' '.join([label, 'TER']))
    if 'dev' in args.plot and dev_perplexities:
        plt.plot(*zip(*dev_perplexities), '--', label=' '.join([label, 'dev loss']))
    if 'train' in args.plot and train_perplexities:
        plt.plot(*zip(*train_perplexities), label=' '.join([label, 'train loss']))

legend = plt.legend(loc='upper center', shadow=True)

if args.output is not None:
    plt.savefig(args.output)
else:
    plt.show()