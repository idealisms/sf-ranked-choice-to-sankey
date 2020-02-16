import collections
import sys
import xml.etree.ElementTree as ET

# TODO: Maybe have an option to use family/last names only.

CandidateData = collections.namedtuple('CandidateData', ['votes', 'transfer'])


def makeCandidateData(choiceGroup):
    cd = CandidateData([], [])
    for roundGroup in choiceGroup.findall('.//{RcvShortReport}roundGroup'):

        textbox9 = roundGroup.find('.//*[@votes]')
        cd.votes.append(int(float(textbox9.attrib['votes'])))

        transferType = roundGroup.find('.//*[@voteTransfer]')
        voteTransfer = int(float(transferType.attrib['voteTransfer']))
        if voteTransfer != 0:
            cd.transfer.append(voteTransfer)
    return cd


def makeSankeyOutput(candidates):
    for round_ in range(len(next(iter(candidates.values())).votes) - 1):
        for name, cd in candidates.items():
            if cd.votes[round_ + 1] > 0:
                # If someone is not eliminated, their votes transfer to
                # themselves.
                print('{} (round {}) [{}] {} (round {})'.format(
                    name, round_ + 1, cd.votes[round_], name, round_ + 2))
            elif len(cd.transfer) == round_ + 1:
                # If someone is eliminated, their votes transfer to others.
                transferVotes(candidates, name, round_)


def transferVotes(candidates, name, round_):
    cd = candidates[name]
    votesTransferred = 0
    for transferToName, transferToData in candidates.items():
        if transferToData.votes[round_ + 1] > 0:
            # print('transfering to', transferToName, transferToData)
            print('{} (round {}) [{}] {} (round {})'.format(
                name, round_ + 1, transferToData.transfer[round_],
                transferToName, round_ + 2))
            votesTransferred += transferToData.transfer[round_]
    if round_ == 0:
        print('{} (round {}) [{}] No second choice'.format(
            name, round_ + 1, cd.votes[0] - votesTransferred))

def main(filename):
    root = ET.parse(filename).getroot()
    choiceGroups = root.findall('.//{RcvShortReport}choiceGroup')

    candidates = {}
    for choiceGroup in choiceGroups:
        candidateName = choiceGroup[0].attrib['choiceName']
        if candidateName not in (
                'Blanks', 'Exhausted', 'Overvotes', 'Remainder Points'):
            candidates[candidateName] = makeCandidateData(choiceGroup)
    # print(candidates)

    makeSankeyOutput(candidates)

if __name__ == '__main__':
    main(sys.argv[1])
