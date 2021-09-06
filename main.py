from total_tests import *
from total_experiments import run_experiments
import sys


def main():
    # Running experiments
    if len(sys.argv) == 2 and sys.argv[1] == '--experiments':
        run_experiments()

    # Running validation tests
    else:
        to_run = []
        draw = False

        # Default setup
        if len(sys.argv) == 1:
            to_run = ["SAT", "CSP", "CSP_iterative", "SAT_iterative"]
        # Custom setup
        else:
            for i in range(1, len(sys.argv)):
                if sys.argv[i] == '--draw':
                    draw = True
                else:
                    to_run.append(sys.argv[i])

        for mode in to_run:
            if mode == "CSP" or mode == "SAT" or mode == "CSP_iterative" or mode == "SAT_iterative":
                if run_tests(mode, draw):
                    print("Tests passed.")
                else:
                    print("Tests failed.")
            else:
                print("Unsupported mode")
                return


if __name__ == '__main__':
    main()
