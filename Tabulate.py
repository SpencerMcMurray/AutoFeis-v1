place_to_irish = {1: 100, 2: 75, 3: 65, 4: 60, 5: 56, 6: 53, 7: 50, 8: 47, 9: 45, 10: 43, 11: 40, 12: 39, 13: 38,
                  14: 37, 15: 36, 16: 35, 17: 34, 18: 33, 19: 32, 20: 31, 21: 30, 22: 29, 23: 28, 24: 27, 25: 26,
                  26: 25, 27: 24, 28: 23, 29: 22, 30: 21, 31: 20, 32: 19, 33: 18, 34: 17, 35: 16, 36: 15, 37: 14,
                  38: 13, 39: 12, 40: 11, 41: 10, 42: 9, 43: 8, 44: 7, 45: 6, 46: 5, 47: 4, 48: 3, 49: 2, 50: 1}


class DancerNotFound(Exception):
    pass


def merge_sort_dancers(dancers):
    """(list of Dancers) -> list of Dancers
    Merge sort, but works in terms of Dancer scores.
    """
    def merge(first, second):
        ordered = []
        while len(first) != 0 and len(second) != 0:
            if first[0].score < second[0].score:
                ordered.append(second.pop(0))
            else:
                ordered.append(first.pop(0))
        while len(first) != 0:
            ordered.append(first.pop(0))
        while len(second) != 0:
            ordered.append(second.pop(0))
        return ordered

    # Recursively merge two halves together.
    if len(dancers) <= 1:
        result = dancers
    else:
        result = merge(merge_sort_dancers(dancers[:len(dancers)//2]),
                       merge_sort_dancers(dancers[len(dancers)//2:]))
    return result


class Dancer:
    """A simple class giving a Dancer a number and a score"""

    def __init__(self, dancer_num, score, scores=list()):
        self.dancer_num = dancer_num
        # Will be a list of judge's raw marks for each judge (nested), with the last item in each sublist being the
        # grid from that judge.
        self.scores = scores
        self.score = score
        self.place = 0

    def __repr__(self):
        """(Dancer) -> str
        Returns the dancer number and place for testing/understanding purposes.
        """
        return str(self.dancer_num) + ': ' + str(self.score)

    def show_all(self):
        """(Dancer) -> str
        Shows all Dancer attributes for testing/understanding.
        """
        return self.dancer_num, self.scores, self.score, self.place


def find_dancer(dancers, num):
    """(list of Dancers, int) -> Dancer
    Finds and returns the dancer with the given dancer number in a list of Dancers.
    RAISES: DancerNotFound if a Dancer with the given dancer number isn't found in the list.
    """
    for dancer in dancers:
        if dancer.dancer_num == num:
            return dancer
    raise DancerNotFound("Dancer wasn't found, did a judge forget to mark someone?")


def get_irish_points(place, num_ties=0):
    """(int, int) -> int or float
    Turns a placement with the given number of ties(two people implies 1 tie) into points on the Irish CLRG grid scale.
    """
    if place > 50:
        pts = 0
    elif num_ties > 0:
        pts = get_tie(place, num_ties)
    else:
        pts = place_to_irish[place]
    return round(pts, 2)


def get_tie(start_place, num_ties):
    """(int, int) -> int or float
    Returns the number of Irish points that should be given to a dancer at start_place when there are num_ties ties.
    """
    total = 0
    for i in range(start_place, num_ties + start_place + 1):
        total += place_to_irish[i]
    return total/(num_ties + 1)


def order_by_total_pts(dancer_list):
    """(list of list of int) -> list of Dancers
    Given a list of dancer info obtained from GetDigits, returns the list of Dancers in increasing order, ordered by
    score.
    """
    # Format the input list into a list of Dancers.
    dancers = list()
    for dancer in dancer_list:
        scores = list()
        raw = 0
        for i in range(1, len(dancer)):
            scores.append(dancer[i])
            raw += dancer[i]
        dancers.append(Dancer(dancer[0], raw, scores))
    # Order said list in terms of dancer score.
    dancers = merge_sort_dancers(dancers)

    # Now go through that ordered list and assign everyone the correct amount of Irish points.
    ordered_dancers = list()
    i = 0
    while i < len(dancers):
        place = i + 1
        num_ties = 0
        # As long as there is a next item, make sure its not the same as the current one.
        while i + num_ties + 1 < len(dancers) and dancers[i].score == dancers[i + num_ties + 1].score:
            num_ties += 1
        irish_pts = get_irish_points(place, num_ties)
        dancers[i].scores.append(irish_pts)
        for j in range(i, i + num_ties + 1):
            ordered_dancers.append(Dancer(dancers[j].dancer_num, irish_pts, dancers[j].scores))
            ordered_dancers[-1].place = place
        i += num_ties + 1
    return ordered_dancers


def get_overalls(all_marks):
    """(list of list of Dancers) -> list of Dancers
    Given a list of each judges ordered list of Dancers(using order_by_total_pts), returns the overall cumulative
    scores of each dancer in increasing score order.
    """
    overalls = []
    for i in range(len(all_marks)):
        for dancer in all_marks[i]:
            dancer_sum = dancer.score
            # Get all of this Dancer's marks across all judges.
            scores = list()
            scores.append(dancer.scores)
            for j in range(1, len(all_marks)):
                other_same_dancer = find_dancer(all_marks[j], dancer.dancer_num)
                scores.append(other_same_dancer.scores)
                dancer_sum += other_same_dancer.score
            overalls.append(Dancer(dancer.dancer_num, dancer_sum, scores))
    overalls = merge_sort_dancers(overalls)
    i = 0
    while i < len(overalls):
        place = i + 1
        num_ties = 0
        # As long as there is a next item, make sure its not the same as the current one.
        while i + num_ties + 1 < len(overalls) and overalls[i].score == overalls[i + num_ties + 1].score:
            num_ties += 1
        for j in range(i, i + num_ties + 1):
            overalls[j].place = place
        i += num_ties + 1
    return overalls


def get_round_medals(dancers, judge_for_round):
    """(list of Dancers) -> list of list of Dancers
    Given a list of Dancers ordered by get_overalls, returns the list of list of ordered Dancers for each round.
    """
    placements = list()
    for round in range(len(dancers[0].scores[0]) - 1):
        # Identify which judge its to be
        if judge_for_round:
            judge = round
        else:
            judge = 0
        new_dancers = list()
        # Create a new list which records the marks of just this one round from this one judge for each dancer.
        for i in range(len(dancers)):
            new_dancers.append([dancers[i].dancer_num, dancers[i].scores[judge][round]])

        # Order those dancers.
        placements.append(order_by_total_pts(new_dancers))
    return placements
