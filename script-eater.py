import os, sys
from utilities import log
from utilities import Mode

def empty(string): return (string == '' or string == None)

def eat(file_name):
    abs_path = os.path.abspath(file_name)
    parent_dir = os.path.dirname(abs_path)
    if(not os.path.exists(abs_path)): raise FileNotFoundError("File: " + abs_path + " does not exist!")
    log(Mode.INFO, "Opening file for parsing: " + abs_path)

    # Transcript line storage
    raw_lines = []
    processed_lines = []

    file = open(abs_path)
    episode_number = file.readline().strip()
    if(not episode_number.isdigit()): raise Exception("Transcript line 1: \"" + episode_number + "\" has invalid episode header!\n\tThe first line of the transcript must contain exclusively the alphanumeric episode number")

    # Padding ep number
    if(int(episode_number) < 10): episode_number = '00' + episode_number
    elif(int(episode_number) < 100): episode_number = '0' + episode_number

    # User info
    log(Mode.INFO, "Processing episode " + episode_number)
    for line in file: raw_lines.append(line.strip())
    file.close()

    num = 2
    case = 0
    line_1 = None
    line_2 = None

    # Process Line combination
    while(len(raw_lines) > 0):
        # Grab more lines from the file as needed
        if(case != 2):
            line_1 = raw_lines.pop(0)
            num = num + 1
        if(len(raw_lines) > 0):
            line_2 = raw_lines.pop(0)
            num = num + 1
        else: line_2 = ''

        # log(Mode.WARN, "L1: " + line_1 + "\n\tL2: " + line_2 + "\n")

        # Process the lineup case and append or shift accordingly
        if(empty(line_1) and empty(line_2)):
            # log(Mode.DEBUG, "EMPTY SET LINE(" + str(num) + ")")
            case = 0
        elif(not empty(line_1) and empty(line_2)):
            processed_lines.append(line_1)
            # log(Mode.DEBUG, "SINGLE SET LINE(" + str(num) + "): " + line_1)
            case = 1
        elif(empty(line_1) and not empty(line_2)):
            line_1 = line_2
            # log(Mode.DEBUG, "SHIFT SET LINE (" + str(num) + "): " + line_2)
            case = 2
        elif(not empty(line_1) and not empty(line_2)):
            line = line_1 + '\\N' + line_2
            processed_lines.append(line)
            # log(Mode.DEBUG, "DOUBLE SET LINE (" + str(num) + "): " + line)
            case = 3

    last_badge = ''
    # Find badgeless lines and give them the last known one
    for i, line in enumerate(processed_lines):
        has_badge = (len(line.split(':')) == 2)
        if(has_badge): last_badge = line.split(':')[0]
        else: processed_lines[i] = last_badge + ": " + line

    # Figure out output path
    out_path = parent_dir + '/' + str(episode_number) + '_formatted_output.txt'
    log(Mode.INFO, "Writing out to file: " + out_path)

    # Create Formatted output
    out_file = open(out_path, 'w+')
    for line in processed_lines: out_file.write(line + "\n")
    out_file.close()

def main():
    args = sys.argv;

    if(len(args) != 2):
        log(Mode.ERROR, "Missing file in arguments!\n\tUsage: python3 script-eater.py [file]")
        sys.exit(0)

    try: eat(args[1])
    except Exception as e:  log(Mode.ERROR, str(e))

if __name__ == "__main__":
    main()
