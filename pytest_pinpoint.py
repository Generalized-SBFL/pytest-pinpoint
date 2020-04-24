"""Major section for pytest pinpoint plugin"""

from coverage.data import CoverageData

import coverage
import os
import sys
import math
import pytest


def pytest_addoption(parser):
    """Create --pinpoint option to run the plugin"""
    group = parser.getgroup("pinpoint")
    group.addoption(
        "--pinpoint",
        action="store_true",
        help="pytest-pinpoint help \n--pinpoint: analyze branch coverage to detect faults",
    )


def rank(data, key):
    """Rank function used to rank SBFL scores"""
    ranks = [x+1 for x in range(len(data))]
    return sorted(ranks, reverse=True, key=lambda x:data[x-1][key])


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Generate terminal report for pytest-pinpoint"""
    # collect pass fail stats
    terminalreporter.section('Pytest PinPoint Data Collection')
    failures = [[report.nodeid, []]
                for report in terminalreporter.stats.get('failed', [])]
    passes = [[report.nodeid, []]
                for report in terminalreporter.stats.get('passed', [])]
    # print("failed ", len(failures), "times", failures)
    # print("passed ", len(passes), "times", passes)
    # connect to the database
    covdb = coverage.CoverageData()
    covdb.read()
    storage = []
    # Collect measured_files
    measured_files = covdb.measured_files()
    for measured_f in measured_files:
        current_context = covdb.contexts_by_lineno(measured_f)
        # not consider files which are not tested
        if current_context is [] or current_context is None:
            measured_files.remove(measured_f)
        else:
            # store pass/fail stats associated with context and line number
            for key, value in covdb.contexts_by_lineno(measured_f).items():
                if value is not ['']:
                    for context in value:
                        for failed_context in failures:
                            if failed_context[0] in context:
                                failed_context[1].append(abs(key))
                        for passed_context in passes:
                            if passed_context[0] in context:
                                passed_context[1].append(abs(key))
    # print("failures")
    # print(failures)
    # print("passes")
    # print(passes)
    # Link tested files to contexts information
    files = []
    for context in failures:
        file_name = context[0].split('::')[0]
        file_name = file_name.split('test_')[-1]
        if not any(file_name in file for file in files):
            files.append([file_name])
    for context in passes:
        file_name = context[0].split('::')[0]
        file_name = file_name.split('test_')[-1]
        if not any(file_name in file for file in files):
            files.append([file_name])
    # Count pass/faill information associated with line
    for file in files:
        for failed_context in failures:
            if file[0] in failed_context[0].split('::')[0]:
                for line in failed_context[1]:
                    if not any(line_info["line"] == line for line_info in file[1:]):
                        file.append({"line": line, "failed times": 1, "passed times": 0})
                    else:
                        for line_info in file[1:]:
                            if line_info["line"] is line:
                                line_info["failed times"] += 1
    for file in files:
        for passed_context in passes:
            if file[0] in passed_context[0].split('::')[0]:
                for line in passed_context[1]:
                    if not any(line_info["line"] == line for line_info in file[1:]):
                        file.append({"line": line, "failed times": 0, "passed times": 1})
                    else:
                        for line_info in file[1:]:
                            if line_info["line"] is line:
                                line_info["passed times"] += 1
    # Count total numbers of passes and fails
    totalfailed_num = 0
    totalpassed_num = 0
    for file in files:
        for line_info in file[1:]:
            totalfailed_num += line_info.get("failed times")
            totalpassed_num += line_info.get("passed times")
    # Calculate SBFL Scores
    scores = []
    for file in files:
        file_scores = []
        print("——————————————————————————")
        # Count total executed lines in a file
        for measured_file in measured_files:
            if file[0] in measured_file:
                totalnum = len(covdb.lines(measured_file))
        # Calculate scores for each line
        for line_info in file[1:]:
            print("File:", file[0])
            print("Line:", line_info["line"])
            total_times = 0
            total_times = line_info["passed times"] + line_info["failed times"]
            print("Failed:", line_info["failed times"])
            print("Passed:", line_info["passed times"])
            print("Tested:", total_times)
            Tarantula = (line_info["failed times"] / totalfailed_num) / ((line_info["failed times"] / totalfailed_num) + (line_info["passed times"] / totalpassed_num))
            print("Tarantula Score:", Tarantula)
            Ochiai = (line_info["failed times"] / math.sqrt(totalfailed_num * total_times))
            print("Ochiai Score:",Ochiai)
            Op2 = line_info["failed times"] - line_info["passed times"] / (totalpassed_num + 1)
            if Op2 > 0:
                print("Op2 Score", Op2)
            else:
                Op2 = 0
                print("Op2 Score", Op2)
            Barinel = 1 - line_info["passed times"] / total_times
            print("Barinel Score", Barinel)
            if line_info["failed times"] > 0:
                DStar = 2 / (line_info["passed times"] + totalfailed_num - line_info["failed times"])
            else:
                DStar = 0
            print("DStar Score", DStar)
            print("——————————————————————————")
            file_scores.append({"total": totalnum, "file": file[0], "line": line_info["line"], "Tarantula": Tarantula, "Ochiai": Ochiai, "Op2": Op2, "Barinel": Barinel, "DStar": DStar})
        scores.append(file_scores)
    # Rank scores
    for file_scores in scores:
        Tarantula_rank = rank(file_scores, "Tarantula")
        Ochiai_rank = rank(file_scores, "Ochiai")
        Op2_rank = rank(file_scores, "Op2")
        Barinel_rank = rank(file_scores, "Barinel")
        DStar_rank = rank(file_scores, "DStar")
        count = 0
        for line_score in file_scores:
            line_score["Tarantula_rank"] = Tarantula_rank[count]
            line_score["Tarantula_exam"] = Tarantula_rank[count] / line_score["total"]
            line_score["Ochiai_rank"] = Ochiai_rank[count]
            line_score["Ochiai_exam"] = Ochiai_rank[count] / line_score["total"]
            line_score["Op2_rank"] = Op2_rank[count]
            line_score["Op2_exam"] = Op2_rank[count] / line_score["total"]
            line_score["Barinel_rank"] = Barinel_rank[count]
            line_score["Barinel_exam"] = Barinel_rank[count] / line_score["total"]
            line_score["DStar_rank"] = DStar_rank[count]
            line_score["DStar_exam"] = DStar_rank[count] / line_score["total"]
            count = count + 1
            print("___________________")
            print("File:", line_score.get("file"))
            print("Line:", line_score.get("line"))
            print("Tarantula_rank num:", line_score.get("Tarantula_rank"))
            print("Tarantula_exam num:", line_score.get("Tarantula_exam"))
            print("Ochiai_rank num:", line_score.get("Ochiai_rank"))
            print("Ochiai_exam num:", line_score.get("Ochiai_exam"))
            print("Op2_rank num:", line_score.get("Op2_rank"))
            print("Op2_exam num:", line_score.get("Op2_exam"))
            print("Barinel_rank num:", line_score.get("Barinel_rank"))
            print("Barinel_exam num:", line_score.get("Barinel_exam"))
            print("DStar_rank num:", line_score.get("DStar_rank"))
            print("DStar_exam num:", line_score.get("DStar_exam"))
